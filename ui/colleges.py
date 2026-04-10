import customtkinter as ctk
from tkinter import ttk, messagebox
import mysql_handler as dh


class CollegeUI:
    def setup_college_ui(self):
        self.coll_form = ctk.CTkFrame(self.college_tab)
        self.coll_form.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.coll_form, text="College Information", font=("Roboto", 16, "bold")).pack(pady=10)

        self.entry_college_code = ctk.CTkEntry(self.coll_form, placeholder_text="College Code", width=200)
        self.entry_college_code.pack(pady=5, padx=10)

        self.entry_college_name = ctk.CTkEntry(self.coll_form, placeholder_text="College Name", width=200)
        self.entry_college_name.pack(pady=5, padx=10)

        self.create_button_frame(self.coll_form, self.add_college, self.update_college,
                                 self.delete_college, self.clear_college_fields)

        table_frame = ctk.CTkFrame(self.college_tab)
        table_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=0)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_columnconfigure(1, weight=0)

        self.college_count_label = ctk.CTkLabel(table_frame, text="Total Records: 0",
                                                font=("Roboto", 12, "bold"), text_color="#2a942a")
        self.college_count_label.grid(row=1, column=1, sticky="e", padx=5, pady=5)

        self.college_tree = ttk.Treeview(table_frame, columns=("Code", "Name"), show="headings")
        self.college_tree.heading("Code", text="College Code")
        self.college_tree.heading("Name", text="College Name")
        self.college_tree.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.college_tree.bind("<<TreeviewSelect>>", self.on_college_select)

        self.refresh_college_table()
        self.update_all_record_counts()

    def add_college(self):
        try:
            code = self.entry_college_code.get().strip().upper()
            name = self.entry_college_name.get().strip()
            if not code or not name:
                messagebox.showerror("Error", "All fields are required!")
                return
            if not code.isalnum():
                messagebox.showerror("Error", "College code must be alphanumeric!")
                return
            if dh.college_db.record_exists('colleges', 'code', code):
                messagebox.showerror("Error", "College Code already exists!")
                return
            if dh.college_db.insert_record('colleges', {'code': code, 'name': name}):
                self.refresh_college_table()
                self.update_college_dropdown()
                self.update_all_record_counts()
                messagebox.showinfo("College Added", "College added successfully!")
                self.clear_college_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add college: {str(e)}")

    def update_college(self):
        code = self.entry_college_code.get().strip()
        name = self.entry_college_name.get().strip()
        if not code or not name:
            messagebox.showerror("Error", "All fields are required!")
            return
        if not messagebox.askyesno("Confirm", f"Update college {code}?"):
            return
        result = dh.college_db.update_record('colleges', {'name': name}, 'code', code)
        if result > 0:
            self.refresh_college_table()
            self.update_college_dropdown()
            self.update_all_record_counts()
            messagebox.showinfo("College Updated", "College updated successfully!")
        elif result == 0:
            messagebox.showinfo("No Changes", "Nothing was changed.")
        self.clear_college_fields()

    def delete_college(self):
        code = self.entry_college_code.get().strip()
        if not code:
            return
        if messagebox.askyesno("Confirm", f"Delete college {code}?"):
            if dh.college_db.delete_record('colleges', 'code', code):
                self.refresh_college_table()
                self.refresh_program_table()
                self.update_college_dropdown()
                self.update_all_record_counts()
                messagebox.showinfo("College Deleted", "College deleted successfully!")
                self.clear_college_fields()

    def clear_college_fields(self):
        self.entry_college_code.configure(state="normal")
        self.entry_college_code.delete(0, 'end')
        self.entry_college_name.delete(0, 'end')

    def on_college_select(self, event):
        selected = self.college_tree.selection()
        if not selected:
            return
        val = self.college_tree.item(selected[0])['values']
        self.clear_college_fields()
        self.entry_college_code.insert(0, val[0])
        self.entry_college_code.configure(state="disabled")
        self.entry_college_name.insert(0, val[1])

    def refresh_college_table(self):
        for item in self.college_tree.get_children():
            self.college_tree.delete(item)
        for college in dh.college_db.load_data('colleges'):
            self.college_tree.insert("", "end", values=(college['code'], college['name']))
