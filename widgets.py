import customtkinter as ctk
from tkinter import ttk, Listbox, Toplevel

active_dropdowns = []


class SearchableCombobox(ctk.CTkFrame):
    def __init__(self, parent, placeholder_text="Select...", width=200, height=30, dropdown_height=150, **kwargs):
        super().__init__(parent, fg_color="transparent")

        self.width = width
        self.height = height
        self.dropdown_height = dropdown_height
        self.placeholder_text = placeholder_text
        self.selected_value = ""
        self.items = []
        self.filtered_items = []
        self.dropdown_window = None
        self.listbox = None

        self.entry = ctk.CTkEntry(self, width=width, height=height, placeholder_text=placeholder_text)
        self.entry.pack()
        self.entry.bind("<KeyRelease>", self.on_key_release)
        self.entry.bind("<FocusIn>", self.on_focus_in)
        self.entry.bind("<Return>", self.on_enter)
        self.entry.bind("<Down>", self.on_arrow_down)

    def set_items(self, items):
        self.items = items
        self.filtered_items = items

    def get(self):
        return self.selected_value if self.selected_value else self.entry.get()

    def set(self, value):
        self.selected_value = value
        self.entry.delete(0, "end")
        if value:
            self.entry.insert(0, value)

    def on_key_release(self, event):
        search_text = self.entry.get().lower()
        self.filtered_items = [item for item in self.items if search_text in item.lower()]
        if self.dropdown_window and self.dropdown_window.winfo_exists():
            self.update_listbox()
        else:
            self.show_dropdown()

    def on_focus_in(self, event):
        if not self.dropdown_window or not self.dropdown_window.winfo_exists():
            self.show_dropdown()

    def on_enter(self, event):
        if self.filtered_items:
            self.set(self.filtered_items[0])
            self.hide_dropdown()
            if hasattr(self.master, 'reset_focus_state'):
                self.master.reset_focus_state()
            else:
                self.master.focus_set()
            self.after(10, self.hide_dropdown)

    def on_arrow_down(self, event):
        if not self.dropdown_window or not self.dropdown_window.winfo_exists():
            self.show_dropdown()
        elif self.listbox and self.listbox.size() > 0:
            self.listbox.selection_set(0)
            self.listbox.focus_set()

    def show_dropdown(self):
        if self.dropdown_window and self.dropdown_window.winfo_exists():
            return

        self.dropdown_window = Toplevel(self)
        self.dropdown_window.overrideredirect(True)
        self.dropdown_window.configure(bg="#1a1a1a")

        active_dropdowns.append(self)

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.height
        self.dropdown_window.geometry(f"{self.width}x{self.dropdown_height}+{x}+{y}")

        list_frame = ctk.CTkFrame(self.dropdown_window, fg_color="#1a1a1a")
        list_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.listbox = Listbox(list_frame, yscrollcommand=scrollbar.set,
                               bg="#2b2b2b", fg="white", selectbackground="#2a942a",
                               activestyle="none", highlightthickness=0, borderwidth=0,
                               font=("Roboto", 10))
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        self.listbox.bind("<ButtonRelease-1>", self.on_listbox_select)
        self.listbox.bind("<Motion>", self.on_listbox_motion)
        self.listbox.bind("<Leave>", self.on_listbox_leave)

        self.update_listbox()
        self.dropdown_window.bind("<Escape>", lambda e: self.hide_dropdown())
        self.dropdown_window.focus_set()

    def hide_dropdown(self):
        if self.dropdown_window and self.dropdown_window.winfo_exists():
            if self in active_dropdowns:
                active_dropdowns.remove(self)
            self.dropdown_window.destroy()
            self.dropdown_window = None
            self.listbox = None

    def update_listbox(self):
        if not self.listbox:
            return
        self.listbox.delete(0, "end")
        for item in self.filtered_items:
            self.listbox.insert("end", item)

    def on_listbox_select(self, event):
        if self.listbox.curselection():
            selected = self.listbox.get(self.listbox.curselection())
            self.set(selected)
            self.hide_dropdown()
            if hasattr(self.master, 'reset_focus_state'):
                self.master.reset_focus_state()
            else:
                self.master.focus_set()
            self.after(10, self.hide_dropdown)

    def on_listbox_motion(self, event):
        index = self.listbox.nearest(event.y)
        if index >= 0:
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(index)
            self.listbox.activate(index)

    def on_listbox_leave(self, event):
        self.listbox.selection_clear(0, "end")
