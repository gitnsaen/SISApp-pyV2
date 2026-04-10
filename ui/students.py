import customtkinter as ctk
from tkinter import ttk, messagebox, Toplevel, BooleanVar
from widgets import SearchableCombobox
import mysql_handler as dh


class StudentUI:
    def setup_student_ui(self):
        self.stud_form = ctk.CTkFrame(self.student_tab)
        self.stud_form.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.stud_form, text="Student Information", font=("Roboto", 16, "bold")).pack(pady=10)

        self.entry_stud_id = ctk.CTkEntry(self.stud_form, placeholder_text="ID: YYYY-NNNN", width=200)
        self.entry_stud_id.pack(pady=2)
        self.entry_stud_fname = ctk.CTkEntry(self.stud_form, placeholder_text="First Name", width=200)
        self.entry_stud_fname.pack(pady=2)
        self.entry_stud_lname = ctk.CTkEntry(self.stud_form, placeholder_text="Last Name", width=200)
        self.entry_stud_lname.pack(pady=2)

        self.combo_stud_prog = SearchableCombobox(self.stud_form, placeholder_text="Select Program", width=200)
        self.combo_stud_prog.pack(pady=5)

        self.combo_stud_year = ctk.CTkOptionMenu(self.stud_form, width=200, values=["Select Year", "1", "2", "3", "4"],
                                                 command=lambda value: self.reset_focus_state())
        self.combo_stud_year.pack(pady=5)
        self.combo_stud_year.set("Select Year")

        self.combo_stud_gender = ctk.CTkOptionMenu(self.stud_form, width=200, values=["Select Gender", "Male", "Female"],
                                                   command=lambda value: self.reset_focus_state())
        self.combo_stud_gender.pack(pady=5)
        self.combo_stud_gender.set("Select Gender")

        self.create_button_frame(self.stud_form, self.add_student, self.update_student,
                                 self.delete_student, self.clear_student_fields)

        right_frame = ctk.CTkFrame(self.student_tab)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        right_frame.grid_rowconfigure(0, weight=0)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_rowconfigure(2, weight=0)
        right_frame.grid_rowconfigure(3, weight=0)
        right_frame.grid_columnconfigure(0, weight=1)

        sortFilter_frame = ctk.CTkFrame(right_frame)
        sortFilter_frame.grid(row=0, column=0, sticky="nsew")

        search_filter_frame = ctk.CTkFrame(sortFilter_frame, fg_color="transparent")
        search_filter_frame.pack()

        self.entry_search = ctk.CTkEntry(search_filter_frame, placeholder_text="Search students...", width=450)
        self.entry_search.pack(side="left", padx=10, pady=10)
        self.entry_search.bind("<KeyRelease>", self.search_student)

        ctk.CTkButton(search_filter_frame, text="Filter", command=self.open_filter_window_stud, width=50).pack(side="right", padx=10, pady=10)

        tree_container = ctk.CTkFrame(right_frame)
        tree_container.grid(row=1, column=0, sticky="nsew")

        self.student_tree = ttk.Treeview(tree_container, columns=("ID", "First Name", "Last Name", "Program", "Year", "Gender"), show="headings")
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.student_tree.pack(side="left", fill="both", expand=True)

        self.student_count_label = ctk.CTkLabel(right_frame, text="Total Records: 0",
                                                font=("Roboto", 12, "bold"), text_color="#2a942a")
        self.student_count_label.grid(row=2, column=0, sticky="e", padx=5, pady=5)

        pagination_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        pagination_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        page_size_frame = ctk.CTkFrame(pagination_frame, fg_color="transparent")
        page_size_frame.pack(side="left", padx=5)
        ctk.CTkLabel(page_size_frame, text="Show:", font=("Roboto", 10)).pack(side="left", padx=2)
        self.student_page_size_var = ctk.StringVar(value="10")
        ctk.CTkOptionMenu(page_size_frame, variable=self.student_page_size_var,
                          values=["5", "10", "20", "50"], width=60,
                          command=lambda x: self.on_student_page_size_change()).pack(side="left")

        nav_frame = ctk.CTkFrame(pagination_frame, fg_color="transparent")
        nav_frame.pack(side="right", padx=5)

        self.student_prev_btn = ctk.CTkButton(nav_frame, text="◀", width=30, command=self.student_prev_page)
        self.student_prev_btn.pack(side="left", padx=2)
        self.student_page_label = ctk.CTkLabel(nav_frame, text="Page 1 of 1", font=("Roboto", 10))
        self.student_page_label.pack(side="left", padx=10)
        self.student_next_btn = ctk.CTkButton(nav_frame, text="▶", width=30, command=self.student_next_page)
        self.student_next_btn.pack(side="left", padx=2)

        for col in ("ID", "First Name", "Last Name", "Program", "Year", "Gender"):
            self.student_tree.heading(col, text=col + " ↕", command=lambda c=col: self.sort_student_table(c, False))
            self.student_tree.column(col, width=100)

        self.student_tree.bind("<<TreeviewSelect>>", self.on_student_select)
        self.refresh_student_table()
        self.update_program_dropdown()
        self.update_all_record_counts()

    def add_student(self):
        try:
            sid = self.entry_stud_id.get().strip()
            fn = self.entry_stud_fname.get().strip()
            ln = self.entry_stud_lname.get().strip()
            pr = self.combo_stud_prog.get()
            yr = self.combo_stud_year.get()
            gn = self.combo_stud_gender.get()

            if not all([sid, fn, ln, pr, yr, gn]) or pr == "Select Program" or yr == "Select Year" or gn == "Select Gender":
                messagebox.showerror("Error", "All fields required!")
                return
            if not dh.student_db.validate_student_id(sid):
                messagebox.showerror("Error", "Format: YYYY-NNNN")
                return

            program_codes = [p['code'] for p in dh.program_db.load_data('programs')]
            if pr not in program_codes:
                messagebox.showerror("Error", f"Program '{pr}' does not exist! Please select from the dropdown.")
                return
            if dh.student_db.record_exists('students', 'id', sid):
                messagebox.showerror("Error", "ID exists!")
                return
            if dh.student_db.insert_record('students', {'id': sid, 'firstname': fn, 'lastname': ln, 'program_code': pr, 'year': yr, 'gender': gn}):
                self.refresh_student_table()
                self.update_all_record_counts()
                messagebox.showinfo("Student Added", "Student added successfully!")
                self.clear_student_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add student: {str(e)}")

    def update_student(self):
        sid = self.entry_stud_id.get().strip()
        fn = self.entry_stud_fname.get().strip()
        ln = self.entry_stud_lname.get().strip()
        pr = self.combo_stud_prog.get()
        yr = self.combo_stud_year.get()
        gn = self.combo_stud_gender.get()

        if not all([sid, fn, ln, pr, yr, gn]) or pr == "Select Program" or yr == "Select Year" or gn == "Select Gender":
            messagebox.showerror("Error", "All fields required!")
            return
        if not dh.student_db.validate_student_id(sid):
            messagebox.showerror("Error", "Format: YYYY-NNNN")
            return

        program_codes = [p['code'] for p in dh.program_db.load_data('programs')]
        if pr not in program_codes:
            messagebox.showerror("Error", f"Program '{pr}' does not exist! Please select from the dropdown.")
            return
        if not messagebox.askyesno("Confirm", f"Update student {sid}?"):
            return
        result = dh.student_db.update_record('students', {'firstname': fn, 'lastname': ln, 'program_code': pr, 'year': yr, 'gender': gn}, 'id', sid)
        if result > 0:
            self.refresh_student_table()
            self.update_all_record_counts()
            messagebox.showinfo("Student Updated", "Student updated successfully!")
        elif result == 0:
            messagebox.showinfo("No Changes", "Nothing was changed.")
        self.clear_student_fields()

    def delete_student(self):
        sid = self.entry_stud_id.get().strip()
        if not sid:
            return
        if messagebox.askyesno("Confirm", f"Delete student {sid}?"):
            if dh.student_db.delete_record('students', 'id', sid):
                self.refresh_student_table()
                self.update_all_record_counts()
                messagebox.showinfo("Student Deleted", "Student deleted successfully!")
                self.clear_student_fields()

    def on_student_page_size_change(self):
        self.student_page_size = int(self.student_page_size_var.get())
        self.student_current_page = 1
        self.student_current_sort = None
        self.student_current_reverse = False
        self.refresh_student_table_with_state()

    def student_prev_page(self):
        if self.student_current_page > 1:
            self.student_current_page -= 1
            self.student_current_sort = None
            self.student_current_reverse = False
            self.refresh_student_table_with_state()

    def student_next_page(self):
        if self.student_current_page < self.student_total_pages:
            self.student_current_page += 1
            self.student_current_sort = None
            self.student_current_reverse = False
            self.refresh_student_table_with_state()

    def update_student_pagination_info(self):
        self.student_total_pages = max(1, (self.student_total_count + self.student_page_size - 1) // self.student_page_size)
        self.student_page_label.configure(text=f"Page {self.student_current_page} of {self.student_total_pages}")
        self.student_prev_btn.configure(state="normal" if self.student_current_page > 1 else "disabled")
        self.student_next_btn.configure(state="normal" if self.student_current_page < self.student_total_pages else "disabled")

    def clear_student_fields(self):
        self.entry_stud_id.configure(state="normal")
        self.entry_stud_id.delete(0, 'end')
        self.entry_stud_fname.delete(0, 'end')
        self.entry_stud_lname.delete(0, 'end')
        self.combo_stud_prog.set('')
        self.combo_stud_prog.selected_value = ''
        self.combo_stud_year.set('Select Year')
        self.combo_stud_gender.set('Select Gender')

    def on_student_select(self, event):
        selected = self.student_tree.selection()
        if not selected:
            return
        val = self.student_tree.item(selected[0])['values']
        self.clear_student_fields()
        self.entry_stud_id.insert(0, val[0])
        self.entry_stud_id.configure(state="disabled")
        self.entry_stud_fname.insert(0, val[1])
        self.entry_stud_lname.insert(0, val[2])
        self.combo_stud_prog.set(val[3])
        self.combo_stud_year.set(str(val[4]))
        self.combo_stud_gender.set(val[5])

    def update_program_dropdown(self):
        codes = [p['code'] for p in dh.program_db.load_data('programs')]
        self.combo_stud_prog.set_items(codes if codes else ["No Programs"])

    def refresh_student_table_with_state(self, order_by=None):
        if self.student_filter_data is not None:
            self.apply_student_filters_with_pagination()
        elif self.student_search_where is not None:
            self.refresh_student_table(where_clause=self.student_search_where,
                                       params=self.student_search_params,
                                       order_by=order_by)
        else:
            self.refresh_student_table(order_by=order_by)

    def refresh_student_table(self, where_clause=None, params=None, order_by=None):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        self.student_total_count = dh.student_db.get_total_count('students', where_clause, params)
        students = dh.student_db.get_paginated_data('students',
                                                    page=self.student_current_page,
                                                    page_size=self.student_page_size,
                                                    order_by=order_by,
                                                    where_clause=where_clause,
                                                    params=params)
        for s in students:
            values = [val if val is not None else "None" for val in s.values()]
            self.student_tree.insert("", "end", values=values)

        self.update_student_pagination_info()

        if self.filtered_student_count is not None:
            self.student_count_label.configure(text=f"Showing: {self.filtered_student_count} / {self.student_total_count} records")
        else:
            self.student_count_label.configure(text=f"Total Records: {self.student_total_count}")

    def search_student(self, event):
        query = self.entry_search.get().lower()

        if query:
            conditions = [f"{field} LIKE %s" for field in ['id', 'firstname', 'lastname', 'program_code', 'year', 'gender']]
            params = [f"%{query}%"] * len(conditions)
            where_clause = " OR ".join(conditions)
            self.student_search_where = where_clause
            self.student_search_params = params
            self.student_filter_data = None
            self.student_current_page = 1
            self.filtered_student_count = None
            self.refresh_student_table(where_clause=where_clause, params=params)
            self.filtered_student_count = self.student_total_count
        else:
            self.student_search_where = None
            self.student_search_params = None
            self.student_filter_data = None
            self.filtered_student_count = None
            self.student_current_page = 1
            self.refresh_student_table()

        self.update_all_record_counts()

    def sort_student_table(self, col, reverse):
        col_mapping = {
            "ID": "id", "First Name": "firstname", "Last Name": "lastname",
            "Program": "program_code", "Year": "year", "Gender": "gender"
        }

        for header_col in col_mapping:
            self.student_tree.heading(header_col, text=header_col + " ↕")
        self.student_tree.heading(col, text=col + (" ▼" if reverse else " ▲"))

        self.student_current_sort = col
        self.student_current_reverse = reverse

        items = sorted(
            [(self.student_tree.set(child, col), child) for child in self.student_tree.get_children()],
            key=lambda x: x[0], reverse=reverse
        )
        for index, (_, child) in enumerate(items):
            self.student_tree.move(child, "", index)

        self.student_tree.heading(col, command=lambda: self.sort_student_table(col, not reverse))

    def open_filter_window_stud(self):
        if self.stud_filter_window and self.stud_filter_window.winfo_exists():
            self.stud_filter_window.lift()
            self.stud_filter_window.focus_set()
            return

        filter_window = Toplevel(self)
        filter_window.title("Filter Students")
        filter_window.geometry("380x350")
        filter_window.configure(bg='#2b2b2b')
        filter_window.resizable(False, False)
        filter_window.withdraw()

        def center_window():
            filter_window.update_idletasks()
            x = self.winfo_rootx() + (self.winfo_width() // 2) - 190
            y = self.winfo_rooty() + (self.winfo_height() // 2) - 175
            filter_window.geometry(f"380x350+{x}+{y}")
            filter_window.deiconify()

        filter_window.after(50, center_window)
        self.stud_filter_window = filter_window
        filter_window.protocol("WM_DELETE_WINDOW", lambda: self._close_filter(filter_window, 'stud'))

        if not hasattr(self, 'filter_vars'):
            self.filter_vars = {}

        main_frame = ctk.CTkFrame(filter_window)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        left_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", padx=10, pady=10)

        ltop_frame = ctk.CTkFrame(left_frame)
        ltop_frame.pack(fill="x", expand=True)

        gender_frame = ctk.CTkFrame(ltop_frame, fg_color="transparent")
        gender_frame.pack(side="left", fill="both")
        ctk.CTkLabel(gender_frame, text="Gender:", font=("Arial", 12, "bold")).pack(pady=(0, 10))

        for key in ['male', 'female']:
            if key not in self.filter_vars:
                self.filter_vars[key] = BooleanVar(value=False)
            ctk.CTkCheckBox(gender_frame, text=key.capitalize(), variable=self.filter_vars[key]).pack(pady=3)

        lbot_frame = ctk.CTkFrame(left_frame)
        lbot_frame.pack(fill="x", expand=True)

        year_frame = ctk.CTkFrame(lbot_frame, fg_color="transparent")
        year_frame.pack(fill="both")
        ctk.CTkLabel(year_frame, text="Year Level:", font=("Arial", 12, "bold")).pack(pady=(0, 10))

        year1_frame = ctk.CTkFrame(year_frame)
        year1_frame.pack(side="left", fill="both", expand=True)
        year2_frame = ctk.CTkFrame(year_frame)
        year2_frame.pack(side="right", fill="both", expand=True)

        for i, year in enumerate(["1st", "2nd", "3rd", "4th"]):
            var_name = f'year_{year}'
            if var_name not in self.filter_vars:
                self.filter_vars[var_name] = BooleanVar(value=False)
            frame = year1_frame if i < 2 else year2_frame
            ctk.CTkCheckBox(frame, text=year, variable=self.filter_vars[var_name]).pack(pady=1)

        right_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        college_frame = ctk.CTkFrame(right_frame)
        college_frame.pack(fill="both")
        ctk.CTkLabel(college_frame, text="College:", font=("Arial", 12, "bold")).pack(pady=(0, 10))

        for college in dh.college_db.load_data('colleges'):
            code = college['code']
            var_name = f'college_{code}'
            if var_name not in self.filter_vars:
                self.filter_vars[var_name] = BooleanVar(value=False)
            ctk.CTkCheckBox(college_frame, text=code, variable=self.filter_vars[var_name]).pack(pady=3)

        button_frame = ctk.CTkFrame(filter_window)
        button_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(button_frame, text="Apply Filters", command=lambda: self.apply_filters(filter_window), width=100).pack(side="left", padx=8)
        ctk.CTkButton(button_frame, text="Clear All", command=self.clear_all_filters, width=100).pack(side="left", padx=8)
        ctk.CTkButton(button_frame, text="Cancel", command=filter_window.destroy, width=100).pack(side="left", padx=8)

    def apply_student_filters_with_pagination(self):
        if not self.student_filter_data:
            return

        students = dh.student_db.load_data('students')
        programs = dh.program_db.load_data('programs')
        program_college_map = {prog['code']: prog['college_code'] for prog in programs}
        filter_data = self.student_filter_data
        filtered_students = []

        for student in students:
            gender_match = True
            if filter_data.get('male') or filter_data.get('female'):
                gender_match = (
                    (filter_data.get('male') and student['gender'].lower() == 'male') or
                    (filter_data.get('female') and student['gender'].lower() == 'female')
                )

            year_match = True
            if filter_data.get('year'):
                year_match = str(student['year']) in filter_data['year']

            college_match = True
            if filter_data.get('college'):
                student_college = program_college_map.get(student['program_code'])
                college_match = student_college and student_college in filter_data['college']

            if gender_match and year_match and college_match:
                filtered_students.append(student)

        start_idx = (self.student_current_page - 1) * self.student_page_size
        paginated_students = filtered_students[start_idx:start_idx + self.student_page_size]

        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        for student in paginated_students:
            self.student_tree.insert("", "end", values=list(student.values()))

        self.student_total_count = len(filtered_students)
        self.update_student_pagination_info()

        total_students = len(dh.student_db.load_data('students'))
        self.filtered_student_count = len(filtered_students)
        self.student_count_label.configure(text=f"Showing: {self.filtered_student_count} / {total_students} records")

    def apply_filters(self, filter_window=None):
        filter_data = {}
        any_filter_active = False

        if hasattr(self, 'filter_vars'):
            for key in ['male', 'female']:
                if self.filter_vars[key].get():
                    filter_data[key] = True
                    any_filter_active = True

            year_mapping = {'1st': '1', '2nd': '2', '3rd': '3', '4th': '4'}
            for year, num in year_mapping.items():
                if self.filter_vars[f'year_{year}'].get():
                    filter_data.setdefault('year', []).append(num)
                    any_filter_active = True

            for college in dh.college_db.load_data('colleges'):
                code = college['code']
                if self.filter_vars[f'college_{code}'].get():
                    filter_data.setdefault('college', []).append(code)
                    any_filter_active = True

        if any_filter_active:
            self.student_filter_data = filter_data
            self.student_search_where = None
            self.student_search_params = None
            self.student_current_page = 1
            self.student_current_sort = None
            self.student_current_reverse = False
            self.apply_student_filters_with_pagination()
        else:
            self.student_filter_data = None
            self.student_search_where = None
            self.student_search_params = None
            self.filtered_student_count = None
            self.student_current_page = 1
            self.student_current_sort = None
            self.student_current_reverse = False
            self.refresh_student_table()

        if filter_window:
            filter_window.destroy()
            self.stud_filter_window = None

    def clear_all_filters(self):
        if hasattr(self, 'filter_vars'):
            for var in self.filter_vars.values():
                var.set(False)

        self.student_filter_data = None
        self.student_search_where = None
        self.student_search_params = None
        self.filtered_student_count = None
        self.student_current_page = 1
        self.student_current_sort = None
        self.student_current_reverse = False
        self.refresh_student_table()
        self.update_all_record_counts()
