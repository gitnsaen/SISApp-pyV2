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
        table_frame.grid_rowconfigure(0, weight=0)
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_rowconfigure(2, weight=0)
        table_frame.grid_rowconfigure(3, weight=0)
        table_frame.grid_columnconfigure(0, weight=1)

        sortFilter_frame = ctk.CTkFrame(table_frame)
        sortFilter_frame.grid(row=0, column=0, sticky="nsew")

        search_filter_frame = ctk.CTkFrame(sortFilter_frame, fg_color="transparent")
        search_filter_frame.pack()

        self.entry_college_search = ctk.CTkEntry(search_filter_frame, placeholder_text="Search colleges...", width=450)
        self.entry_college_search.pack(side="left", padx=10, pady=10)
        self.entry_college_search.bind("<KeyRelease>", self.search_college)

        tree_container = ctk.CTkFrame(table_frame)
        tree_container.grid(row=1, column=0, sticky="nsew")

        self.college_tree = ttk.Treeview(tree_container, columns=("Code", "Name"), show="headings")
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.college_tree.yview)
        self.college_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.college_tree.pack(side="left", fill="both", expand=True)

        self.college_count_label = ctk.CTkLabel(table_frame, text="Total Records: 0",
                                                font=("Roboto", 12, "bold"), text_color="#2a942a")
        self.college_count_label.grid(row=2, column=0, sticky="e", padx=5, pady=5)

        pagination_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        pagination_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        page_size_frame = ctk.CTkFrame(pagination_frame, fg_color="transparent")
        page_size_frame.pack(side="left", padx=5)
        ctk.CTkLabel(page_size_frame, text="Show:", font=("Roboto", 10)).pack(side="left", padx=2)
        self.college_page_size_var = ctk.StringVar(value="10")
        ctk.CTkOptionMenu(page_size_frame, variable=self.college_page_size_var,
                          values=["5", "10", "20", "50"], width=60,
                          command=lambda x: self.on_college_page_size_change()).pack(side="left")

        nav_frame = ctk.CTkFrame(pagination_frame, fg_color="transparent")
        nav_frame.pack(side="right", padx=5)

        self.college_prev_btn = ctk.CTkButton(nav_frame, text="◀", width=30, command=self.college_prev_page)
        self.college_prev_btn.pack(side="left", padx=2)
        self.college_page_label = ctk.CTkLabel(nav_frame, text="Page 1 of 1", font=("Roboto", 10))
        self.college_page_label.pack(side="left", padx=10)
        self.college_next_btn = ctk.CTkButton(nav_frame, text="▶", width=30, command=self.college_next_page)
        self.college_next_btn.pack(side="left", padx=2)

        for col in ("Code", "Name"):
            self.college_tree.heading(col, text=col + " ↕", command=lambda c=col: self.sort_college_table(c, False))
            self.college_tree.column(col, width=100)

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

    def on_college_page_size_change(self):
        self.college_page_size = int(self.college_page_size_var.get())
        self.college_current_page = 1
        self.college_current_sort = None
        self.college_current_reverse = False
        self.refresh_college_table_with_state()

    def college_prev_page(self):
        if self.college_current_page > 1:
            self.college_current_page -= 1
            self.college_current_sort = None
            self.college_current_reverse = False
            self.refresh_college_table_with_state()

    def college_next_page(self):
        if self.college_current_page < self.college_total_pages:
            self.college_current_page += 1
            self.college_current_sort = None
            self.college_current_reverse = False
            self.refresh_college_table_with_state()

    def update_college_pagination_info(self):
        self.college_total_pages = max(1, (self.college_total_count + self.college_page_size - 1) // self.college_page_size)
        self.college_page_label.configure(text=f"Page {self.college_current_page} of {self.college_total_pages}")
        self.college_prev_btn.configure(state="normal" if self.college_current_page > 1 else "disabled")
        self.college_next_btn.configure(state="normal" if self.college_current_page < self.college_total_pages else "disabled")

    def refresh_college_table_with_state(self, order_by=None):
        if self.college_search_where is not None:
            self.refresh_college_table(where_clause=self.college_search_where,
                                       params=self.college_search_params,
                                       order_by=order_by)
        else:
            self.refresh_college_table(order_by=order_by)

    def refresh_college_table(self, where_clause=None, params=None, order_by=None):
        for item in self.college_tree.get_children():
            self.college_tree.delete(item)

        self.college_total_count = dh.college_db.get_total_count('colleges', where_clause, params)
        colleges = dh.college_db.get_paginated_data('colleges',
                                                    page=self.college_current_page,
                                                    page_size=self.college_page_size,
                                                    order_by=order_by,
                                                    where_clause=where_clause,
                                                    params=params)
        for c in colleges:
            values = [val if val is not None else "None" for val in c.values()]
            self.college_tree.insert("", "end", values=values)

        self.update_college_pagination_info()

        if self.filtered_college_count is not None:
            self.college_count_label.configure(text=f"Showing: {self.filtered_college_count} / {self.college_total_count} records")
        else:
            self.college_count_label.configure(text=f"Total Records: {self.college_total_count}")

    def search_college(self, event):
        query = self.entry_college_search.get().lower()

        if query:
            conditions = [f"{field} LIKE %s" for field in ['code', 'name']]
            params = [f"%{query}%"] * len(conditions)
            where_clause = " OR ".join(conditions)
            self.college_search_where = where_clause
            self.college_search_params = params
            self.college_current_page = 1
            self.filtered_college_count = None
            self.refresh_college_table(where_clause=where_clause, params=params)
            self.filtered_college_count = self.college_total_count
        else:
            self.college_search_where = None
            self.college_search_params = None
            self.filtered_college_count = None
            self.college_current_page = 1
            self.refresh_college_table()

        self.update_all_record_counts()

    def sort_college_table(self, col, reverse):
        col_mapping = {
            "Code": "code",
            "Name": "name"
        }

        for header_col in col_mapping:
            self.college_tree.heading(header_col, text=header_col + " ↕")
        self.college_tree.heading(col, text=col + (" ▼" if reverse else " ▲"))

        self.college_current_sort = col
        self.college_current_reverse = reverse

        items = sorted(
            [(self.college_tree.set(child, col), child) for child in self.college_tree.get_children()],
            key=lambda x: x[0], reverse=reverse
        )
        for index, (_, child) in enumerate(items):
            self.college_tree.move(child, "", index)

        self.college_tree.heading(col, command=lambda: self.sort_college_table(col, not reverse))
