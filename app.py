import customtkinter as ctk
from tkinter import ttk
from widgets import active_dropdowns
from ui.colleges import CollegeUI
from ui.programs import ProgramUI
from ui.students import StudentUI
import mysql_handler as dh

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")


class SISApp(CollegeUI, ProgramUI, StudentUI, ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Student Information System")
        self.geometry("1200x750")

        self.setup_treeview_style()

        self.tabview = ctk.CTkTabview(self, command=self.on_tab_change)
        self.tabview.pack(expand=True, fill="both", padx=20, pady=20)

        self.student_tab = self.tabview.add("  Students  ")
        self.program_tab = self.tabview.add("  Programs  ")
        self.college_tab = self.tabview.add("  Colleges  ")

        self.student_count_label = None
        self.program_count_label = None
        self.college_count_label = None

        self.filtered_student_count = None
        self.filtered_program_count = None

        self.prog_filter_window = None
        self.stud_filter_window = None

        self.student_current_page = 1
        self.student_page_size = 10
        self.student_total_pages = 1
        self.student_total_count = 0
        self.student_search_where = None
        self.student_search_params = None
        self.student_filter_data = None
        self.student_current_sort = None
        self.student_current_reverse = False

        self.program_current_page = 1
        self.program_page_size = 10
        self.program_total_pages = 1
        self.program_total_count = 0
        self.program_search_where = None
        self.program_search_params = None
        self.program_filter_data = None
        self.program_current_sort = None
        self.program_current_reverse = False

        self.setup_college_ui()
        self.setup_program_ui()
        self.setup_student_ui()

        self.bind_all("<Button-1>", self.on_global_click)

    def reset_focus_state(self):
        self.focus_set()

    def on_global_click(self, event):
        widget = event.widget
        current = widget
        while current and hasattr(current, 'master'):
            if isinstance(current, ctk.CTkOptionMenu):
                return
            current = current.master

        for dropdown in active_dropdowns[:]:
            if dropdown.dropdown_window and dropdown.dropdown_window.winfo_exists():
                current = widget
                is_dropdown_click = False
                while current and hasattr(current, 'master'):
                    if current == dropdown.dropdown_window or current == dropdown.entry:
                        is_dropdown_click = True
                        break
                    current = current.master
                if not is_dropdown_click:
                    dropdown.hide_dropdown()

    def setup_treeview_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        rowheight=30,
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading",
                        background="#333333",
                        foreground="white",
                        relief="flat",
                        font=("Roboto", 10, "bold"))
        style.map("Treeview.Heading",
                  background=[("active", "#4a4a4a")],
                  foreground=[("active", "white")])

    def update_all_record_counts(self):
        if self.college_count_label:
            count = len(dh.college_db.load_data('colleges'))
            self.college_count_label.configure(text=f"Total Records: {count}")

        if self.program_count_label:
            total = len(dh.program_db.load_data('programs'))
            if self.filtered_program_count is not None:
                self.program_count_label.configure(text=f"Showing: {self.filtered_program_count} / {total} records")
            else:
                self.program_count_label.configure(text=f"Total Records: {total}")

        if self.student_count_label:
            total = len(dh.student_db.load_data('students'))
            if self.filtered_student_count is not None:
                self.student_count_label.configure(text=f"Showing: {self.filtered_student_count} / {total} records")
            else:
                self.student_count_label.configure(text=f"Total Records: {total}")

    def create_button_frame(self, parent, add_cmd, update_cmd, delete_cmd, clear_cmd):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="Add", width=90, fg_color="#2a942a", command=add_cmd).grid(row=0, column=0, padx=2, pady=2)
        ctk.CTkButton(btn_frame, text="Update", width=90, command=update_cmd).grid(row=0, column=1, padx=2, pady=2)
        ctk.CTkButton(btn_frame, text="Delete", width=90, fg_color="#942a2a", hover_color="#701e1e", command=delete_cmd).grid(row=1, column=0, padx=2, pady=2)
        ctk.CTkButton(btn_frame, text="Clear", width=90, fg_color="gray", command=clear_cmd).grid(row=1, column=1, padx=2, pady=2)

        return btn_frame

    def _close_filter(self, window, kind):
        if kind == 'prog':
            self.prog_filter_window = None
        else:
            self.stud_filter_window = None
        window.destroy()

    def on_tab_change(self):
        tab = self.tabview.get().strip()
        if tab == "Students":
            codes = [p['code'] for p in dh.program_db.load_data('programs')]
            self.combo_stud_prog.set_items(codes if codes else ["No Programs"])
        elif tab == "Programs":
            self.update_college_dropdown()
