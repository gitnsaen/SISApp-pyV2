import customtkinter as ctk
from tkinter import ttk, messagebox, Toplevel, BooleanVar
import mysql_handler as dh


class ProgramUI:
    def setup_program_ui(self):
        self.prog_form = ctk.CTkFrame(self.program_tab)
        self.prog_form.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.prog_form, text="Program Information", font=("Roboto", 16, "bold")).pack(pady=10)

        self.entry_prog_code = ctk.CTkEntry(self.prog_form, placeholder_text="Program Code", width=200)
        self.entry_prog_code.pack(pady=5)
        self.entry_prog_name = ctk.CTkEntry(self.prog_form, placeholder_text="Program Name", width=200)
        self.entry_prog_name.pack(pady=5)

        self.combo_prog_college = ctk.CTkOptionMenu(self.prog_form, width=200, values=["Select College"],
                                                    command=lambda value: self.reset_focus_state())
        self.combo_prog_college.pack(pady=5)

        self.create_button_frame(self.prog_form, self.add_program, self.update_program,
                                 self.delete_program, self.clear_program_fields)

        table_frame = ctk.CTkFrame(self.program_tab)
        table_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        table_frame.grid_rowconfigure(0, weight=0)
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_rowconfigure(2, weight=0)
        table_frame.grid_rowconfigure(3, weight=0)
        table_frame.grid_columnconfigure(0, weight=1)

        sortFilter_frame = ctk.CTkFrame(table_frame)
        sortFilter_frame.grid(row=0, column=0, sticky="nsew")

        search_filter_frame = ctk.CTkFrame(sortFilter_frame, fg_color="transparent")
        search_filter_frame.pack()

        self.entry_prog_search = ctk.CTkEntry(search_filter_frame, placeholder_text="Search programs...", width=450)
        self.entry_prog_search.pack(side="left", padx=10, pady=10)
        self.entry_prog_search.bind("<KeyRelease>", self.search_program)

        ctk.CTkButton(search_filter_frame, text="Filter", command=self.open_filter_window_prog, width=50).pack(side="right", padx=10, pady=10)

        tree_container = ctk.CTkFrame(table_frame)
        tree_container.grid(row=1, column=0, sticky="nsew")

        self.program_tree = ttk.Treeview(tree_container, columns=("Program Code", "Program Name", "College Code"), show="headings")
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.program_tree.yview)
        self.program_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.program_tree.pack(side="left", fill="both", expand=True)

        self.program_count_label = ctk.CTkLabel(table_frame, text="Total Records: 0",
                                                font=("Roboto", 12, "bold"), text_color="#2a942a")
        self.program_count_label.grid(row=2, column=0, sticky="e", padx=5, pady=5)

        pagination_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        pagination_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        page_size_frame = ctk.CTkFrame(pagination_frame, fg_color="transparent")
        page_size_frame.pack(side="left", padx=5)
        ctk.CTkLabel(page_size_frame, text="Show:", font=("Roboto", 10)).pack(side="left", padx=2)
        self.program_page_size_var = ctk.StringVar(value="10")
        ctk.CTkOptionMenu(page_size_frame, variable=self.program_page_size_var,
                          values=["5", "10", "20", "50"], width=60,
                          command=lambda x: self.on_program_page_size_change()).pack(side="left")

        nav_frame = ctk.CTkFrame(pagination_frame, fg_color="transparent")
        nav_frame.pack(side="right", padx=5)

        self.program_prev_btn = ctk.CTkButton(nav_frame, text="◀", width=30, command=self.program_prev_page)
        self.program_prev_btn.pack(side="left", padx=2)
        self.program_page_label = ctk.CTkLabel(nav_frame, text="Page 1 of 1", font=("Roboto", 10))
        self.program_page_label.pack(side="left", padx=10)
        self.program_next_btn = ctk.CTkButton(nav_frame, text="▶", width=30, command=self.program_next_page)
        self.program_next_btn.pack(side="left", padx=2)

        for col in ("Program Code", "Program Name", "College Code"):
            self.program_tree.heading(col, text=col + " ↕", command=lambda c=col: self.sort_program_table(c, False))
            self.program_tree.column(col, width=100)

        self.program_tree.bind("<<TreeviewSelect>>", self.on_program_select)
        self.refresh_program_table()
        self.update_college_dropdown()
        self.update_all_record_counts()

    def add_program(self):
        try:
            code = self.entry_prog_code.get().strip().upper()
            name = self.entry_prog_name.get().strip()
            coll = self.combo_prog_college.get()

            if not all([code, name, coll]) or coll == "Select College":
                messagebox.showerror("Error", "All fields required!")
                return
            if not code.isalnum():
                messagebox.showerror("Error", "Program code must be alphanumeric!")
                return
            if dh.program_db.record_exists('programs', 'code', code):
                messagebox.showerror("Error", "Program Code exists!")
                return
            if dh.program_db.insert_record('programs', {'code': code, 'name': name, 'college_code': coll}):
                self.refresh_program_table()
                self.update_program_dropdown()
                self.update_all_record_counts()
                messagebox.showinfo("Program Added", "Program added successfully!")
                self.clear_program_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add program: {str(e)}")

    def update_program(self):
        code = self.entry_prog_code.get().strip()
        name = self.entry_prog_name.get().strip()
        coll = self.combo_prog_college.get()

        if not all([code, name, coll]) or coll == "Select College":
            messagebox.showerror("Error", "All fields required!")
            return
        if not messagebox.askyesno("Confirm", f"Update program {code}?"):
            return
        result = dh.program_db.update_record('programs', {'name': name, 'college_code': coll}, 'code', code)
        if result > 0:
            self.refresh_program_table()
            self.update_program_dropdown()
            self.update_all_record_counts()
            messagebox.showinfo("Program Updated", "Program updated successfully!")
        elif result == 0:
            messagebox.showinfo("No Changes", "Nothing was changed.")
        self.clear_program_fields()

    def delete_program(self):
        code = self.entry_prog_code.get().strip()
        if not code:
            return
        if messagebox.askyesno("Confirm", f"Delete program {code}?"):
            if dh.program_db.delete_record('programs', 'code', code):
                self.refresh_program_table()
                self.refresh_student_table()
                self.update_program_dropdown()
                self.update_all_record_counts()
                messagebox.showinfo("Program Deleted", "Program deleted successfully!")
                self.clear_program_fields()

    def on_program_page_size_change(self):
        self.program_page_size = int(self.program_page_size_var.get())
        self.program_current_page = 1
        self.program_current_sort = None
        self.program_current_reverse = False
        self.refresh_program_table_with_state()

    def program_prev_page(self):
        if self.program_current_page > 1:
            self.program_current_page -= 1
            self.program_current_sort = None
            self.program_current_reverse = False
            self.refresh_program_table_with_state()

    def program_next_page(self):
        if self.program_current_page < self.program_total_pages:
            self.program_current_page += 1
            self.program_current_sort = None
            self.program_current_reverse = False
            self.refresh_program_table_with_state()

    def update_program_pagination_info(self):
        self.program_total_pages = max(1, (self.program_total_count + self.program_page_size - 1) // self.program_page_size)
        self.program_page_label.configure(text=f"Page {self.program_current_page} of {self.program_total_pages}")
        self.program_prev_btn.configure(state="normal" if self.program_current_page > 1 else "disabled")
        self.program_next_btn.configure(state="normal" if self.program_current_page < self.program_total_pages else "disabled")

    def clear_program_fields(self):
        self.entry_prog_code.configure(state="normal")
        self.entry_prog_code.delete(0, 'end')
        self.entry_prog_name.delete(0, 'end')
        self.combo_prog_college.set('Select College')

    def on_program_select(self, event):
        selected = self.program_tree.selection()
        if not selected:
            return
        val = self.program_tree.item(selected[0])['values']
        self.clear_program_fields()
        self.entry_prog_code.insert(0, val[0])
        self.entry_prog_code.configure(state="disabled")
        self.entry_prog_name.insert(0, val[1])
        self.combo_prog_college.set(val[2])

    def update_college_dropdown(self):
        codes = [c['code'] for c in dh.college_db.load_data('colleges')]
        self.combo_prog_college.configure(values=codes if codes else ["No Colleges"])

    def refresh_program_table(self, where_clause=None, params=None, order_by=None):
        for item in self.program_tree.get_children():
            self.program_tree.delete(item)

        self.program_total_count = dh.program_db.get_total_count('programs', where_clause, params)
        programs = dh.program_db.get_paginated_data('programs',
                                                    page=self.program_current_page,
                                                    page_size=self.program_page_size,
                                                    order_by=order_by,
                                                    where_clause=where_clause,
                                                    params=params)
        for p in programs:
            values = [val if val is not None else "None" for val in p.values()]
            self.program_tree.insert("", "end", values=values)

        self.update_program_pagination_info()

        if self.filtered_program_count is not None:
            self.program_count_label.configure(text=f"Showing: {self.filtered_program_count} / {self.program_total_count} records")
        else:
            self.program_count_label.configure(text=f"Total Records: {self.program_total_count}")

    def refresh_program_table_with_state(self, order_by=None):
        if self.program_filter_data is not None:
            self.apply_program_filters_with_pagination()
        elif self.program_search_where is not None:
            self.refresh_program_table(where_clause=self.program_search_where,
                                       params=self.program_search_params,
                                       order_by=order_by)
        else:
            self.refresh_program_table(order_by=order_by)

    def search_program(self, event):
        query = self.entry_prog_search.get().lower()

        if query:
            conditions = [f"{field} LIKE %s" for field in ['code', 'name', 'college_code']]
            params = [f"%{query}%"] * len(conditions)
            where_clause = " OR ".join(conditions)
            self.program_search_where = where_clause
            self.program_search_params = params
            self.program_filter_data = None
            self.program_current_page = 1
            self.filtered_program_count = None
            self.refresh_program_table(where_clause=where_clause, params=params)
            self.filtered_program_count = self.program_total_count
        else:
            self.program_search_where = None
            self.program_search_params = None
            self.program_filter_data = None
            self.filtered_program_count = None
            self.program_current_page = 1
            self.refresh_program_table()

        self.update_all_record_counts()

    def sort_program_table(self, col, reverse):
        col_mapping = {
            "Program Code": "code",
            "Program Name": "name",
            "College Code": "college_code"
        }

        for header_col in col_mapping:
            self.program_tree.heading(header_col, text=header_col + " ↕")
        self.program_tree.heading(col, text=col + (" ▼" if reverse else " ▲"))

        self.program_current_sort = col
        self.program_current_reverse = reverse

        items = sorted(
            [(self.program_tree.set(child, col), child) for child in self.program_tree.get_children()],
            key=lambda x: x[0], reverse=reverse
        )
        for index, (_, child) in enumerate(items):
            self.program_tree.move(child, "", index)

        self.program_tree.heading(col, command=lambda: self.sort_program_table(col, not reverse))

    def open_filter_window_prog(self):
        if self.prog_filter_window and self.prog_filter_window.winfo_exists():
            self.prog_filter_window.lift()
            self.prog_filter_window.focus_set()
            return

        filter_window = Toplevel(self)
        filter_window.title("Filter Programs")
        filter_window.geometry("350x350")
        filter_window.configure(bg='#2b2b2b')
        filter_window.resizable(False, False)
        filter_window.withdraw()

        def center_window():
            filter_window.update_idletasks()
            x = self.winfo_rootx() + (self.winfo_width() // 2) - 175
            y = self.winfo_rooty() + (self.winfo_height() // 2) - 175
            filter_window.geometry(f"350x350+{x}+{y}")
            filter_window.deiconify()

        filter_window.after(50, center_window)
        self.prog_filter_window = filter_window
        filter_window.protocol("WM_DELETE_WINDOW", lambda: self._close_filter(filter_window, 'prog'))

        if not hasattr(self, 'prog_filter_vars'):
            self.prog_filter_vars = {}

        main_frame = ctk.CTkFrame(filter_window)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        college_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        college_frame.pack(fill="both")
        ctk.CTkLabel(college_frame, text="College:", font=("Arial", 12, "bold")).pack(pady=(0, 10))

        for college in dh.college_db.load_data('colleges'):
            code = college['code']
            var_name = f'prog_college_{code}'
            if var_name not in self.prog_filter_vars:
                self.prog_filter_vars[var_name] = BooleanVar(value=False)
            ctk.CTkCheckBox(college_frame, text=code, variable=self.prog_filter_vars[var_name]).pack(pady=3)

        button_frame = ctk.CTkFrame(filter_window)
        button_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(button_frame, text="Apply Filters", command=lambda: self.apply_prog_filters(filter_window), width=100).pack(side="left", padx=8)
        ctk.CTkButton(button_frame, text="Clear All", command=self.clear_prog_filters, width=100).pack(side="left", padx=8)
        ctk.CTkButton(button_frame, text="Cancel", command=filter_window.destroy, width=100).pack(side="left", padx=8)

    def apply_prog_filters(self, filter_window=None):
        filter_data = {}
        any_filter_active = False

        if hasattr(self, 'prog_filter_vars'):
            for college in dh.college_db.load_data('colleges'):
                code = college['code']
                if self.prog_filter_vars[f'prog_college_{code}'].get():
                    filter_data[code] = True
                    any_filter_active = True

        if any_filter_active:
            self.program_filter_data = filter_data
            self.program_search_where = None
            self.program_search_params = None
            self.program_current_page = 1
            self.program_current_sort = None
            self.program_current_reverse = False
            self.apply_program_filters_with_pagination()
        else:
            self.program_filter_data = None
            self.program_search_where = None
            self.program_search_params = None
            self.filtered_program_count = None
            self.program_current_page = 1
            self.program_current_sort = None
            self.program_current_reverse = False
            self.refresh_program_table()

        if filter_window:
            filter_window.destroy()
            self.prog_filter_window = None

    def clear_prog_filters(self):
        if hasattr(self, 'prog_filter_vars'):
            for var in self.prog_filter_vars.values():
                var.set(False)

        self.program_filter_data = None
        self.program_search_where = None
        self.program_search_params = None
        self.filtered_program_count = None
        self.program_current_page = 1
        self.program_current_sort = None
        self.program_current_reverse = False
        self.refresh_program_table()
        self.update_all_record_counts()

    def apply_program_filters_with_pagination(self):
        if not self.program_filter_data:
            return

        programs = dh.program_db.load_data('programs')
        active_college_filters = [code for code, active in self.program_filter_data.items() if active]
        filtered_programs = [p for p in programs if p['college_code'] in active_college_filters] if active_college_filters else programs

        start_idx = (self.program_current_page - 1) * self.program_page_size
        paginated_programs = filtered_programs[start_idx:start_idx + self.program_page_size]

        for item in self.program_tree.get_children():
            self.program_tree.delete(item)
        for program in paginated_programs:
            self.program_tree.insert("", "end", values=(program['code'], program['name'], program['college_code']))

        self.program_total_count = len(filtered_programs)
        self.update_program_pagination_info()

        total_programs = len(dh.program_db.load_data('programs'))
        self.filtered_program_count = len(filtered_programs)
        self.program_count_label.configure(text=f"Showing: {self.filtered_program_count} / {total_programs} records")
