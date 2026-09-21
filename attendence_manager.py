import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import csv
from datetime import datetime, date

DATA_FILE = "attendance_data.json"

class AttendanceSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Attendance System - Professional")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)
        self.root.configure(bg="#f5f7fa")

        # Color palette
        self.colors = {
            "bg": "#f5f7fa",
            "sidebar": "#1e293b",
            "sidebar_active": "#3b82f6",
            "card": "#ffffff",
            "primary": "#3b82f6",
            "primary_dark": "#2563eb",
            "accent": "#8b5cf6",
            "success": "#10b981",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "text": "#1e293b",
            "muted": "#64748b",
            "border": "#e2e8f0",
            "input_bg": "#f8fafc",
        }

        # Data
        self.students = []       # [{id, name, roll_no, class_name, contact, added_date}]
        self.attendance = []     # [{date, student_id, status}]  status: P/A/L
        self.current_page = "dashboard"

        self._setup_styles()
        self._build_ui()
        self.load_data()
        self._show_page("dashboard")

    # ---------------- STYLES ----------------
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("TLabel", background=self.colors["card"],
                        foreground=self.colors["text"],
                        font=("Segoe UI", 10))
        style.configure("TEntry", padding=6, font=("Segoe UI", 10))
        style.configure("TCombobox", padding=6, font=("Segoe UI", 10))
        style.configure("Treeview",
                        background="white",
                        foreground=self.colors["text"],
                        rowheight=28,
                        fieldbackground="white",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        font=("Segoe UI", 10, "bold"),
                        background=self.colors["primary"],
                        foreground="white")
        style.map("Treeview",
                  background=[("selected", self.colors["primary"])],
                  foreground=[("selected", "white")])

    # ---------------- UI ----------------
    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.colors["primary"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="ATTENDANCE MANAGER",
                 font=("Segoe UI", 16, "bold"),
                 bg=self.colors["primary"], fg="white").pack(side="left", padx=20, pady=15)

        self.date_label = tk.Label(header, text="",
                                   font=("Segoe UI", 10),
                                   bg=self.colors["primary"], fg="#dbeafe")
        self.date_label.pack(side="right", padx=20)
        self._update_date()

        # Main container
        main = tk.Frame(self.root, bg=self.colors["bg"])
        main.pack(fill="both", expand=True, padx=15, pady=15)

        # Sidebar
        sidebar = tk.Frame(main, bg=self.colors["sidebar"], width=200)
        sidebar.pack(side="left", fill="y", padx=(0, 15))
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="NAVIGATION",
                 font=("Segoe UI", 10, "bold"),
                 bg=self.colors["sidebar"], fg="#94a3b8").pack(pady=(15, 10))

        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "Dashboard"),
            ("students", "Students"),
            ("mark", "Mark Attendance"),
            ("reports", "Reports"),
        ]
        for key, label in nav_items:
            btn = tk.Button(sidebar, text=label,
                            font=("Segoe UI", 11),
                            bg=self.colors["sidebar"], fg="white",
                            activebackground=self.colors["sidebar_active"],
                            activeforeground="white",
                            bd=0, anchor="w", padx=20, pady=12,
                            cursor="hand2",
                            command=lambda k=key: self._show_page(k))
            btn.pack(fill="x", padx=8, pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#334155") if b.cget("bg") != self.colors["sidebar_active"] else None)
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.colors["sidebar"]) if b.cget("bg") != self.colors["sidebar_active"] else None)
            self.nav_buttons[key] = btn

        # Info section
        tk.Label(sidebar, text="INFO",
                 font=("Segoe UI", 10, "bold"),
                 bg=self.colors["sidebar"], fg="#94a3b8").pack(pady=(30, 10))
        tk.Label(sidebar, text="Data auto-saved\nto JSON file.\n\nExport reports\nas CSV.",
                 font=("Segoe UI", 9),
                 bg=self.colors["sidebar"], fg="#cbd5e1",
                 justify="left").pack(padx=20, anchor="w")

        # Content area
        self.content = tk.Frame(main, bg=self.colors["bg"])
        self.content.pack(side="left", fill="both", expand=True)

        # Status bar
        self.status = tk.Label(self.root, text="Ready",
                               bg=self.colors["primary"], fg="white",
                               font=("Segoe UI", 9), anchor="w")
        self.status.pack(side="bottom", fill="x")

    def _update_date(self):
        try:
            now = datetime.now().strftime("%A, %d %B %Y")
            self.date_label.config(text=now)
        except Exception:
            pass
        self.root.after(60000, self._update_date)

    # ---------------- NAVIGATION ----------------
    def _show_page(self, page):
        try:
            self.current_page = page
            for k, b in self.nav_buttons.items():
                if k == page:
                    b.config(bg=self.colors["sidebar_active"])
                else:
                    b.config(bg=self.colors["sidebar"])

            for widget in self.content.winfo_children():
                widget.destroy()

            if page == "dashboard":
                self._build_dashboard()
            elif page == "students":
                self._build_students()
            elif page == "mark":
                self._build_mark_attendance()
            elif page == "reports":
                self._build_reports()

            self.status.config(text=f"Viewing: {page.title()}")
        except Exception as e:
            print(f"Error showing page: {e}")
            messagebox.showerror("Error", f"Failed to load page: {e}")

    # ---------------- DATA ----------------
    def load_data(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.students = data.get("students", [])
                self.attendance = data.get("attendance", [])
                self.status.config(text=f"Loaded {len(self.students)} students, {len(self.attendance)} attendance records")
        except (json.JSONDecodeError, IOError) as e:
            messagebox.showwarning("Data Error", f"Could not read data file. Starting fresh.\n{e}")
            self.students = []
            self.attendance = []

    def save_data(self):
        try:
            data = {"students": self.students, "attendance": self.attendance}
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            messagebox.showerror("Save Error", f"Could not save data:\n{e}")

    # ---------------- DASHBOARD ----------------
    def _build_dashboard(self):
        try:
            title = tk.Label(self.content, text="DASHBOARD",
                             font=("Segoe UI", 18, "bold"),
                             bg=self.colors["bg"], fg=self.colors["text"])
            title.pack(anchor="w", pady=(0, 15))

            # Stats cards
            cards = tk.Frame(self.content, bg=self.colors["bg"])
            cards.pack(fill="x", pady=(0, 20))

            today = date.today().isoformat()
            total_students = len(self.students)
            today_records = [a for a in self.attendance if a.get("date") == today]
            present = sum(1 for a in today_records if a.get("status") == "P")
            absent = sum(1 for a in today_records if a.get("status") == "A")
            late = sum(1 for a in today_records if a.get("status") == "L")
            marked = len(today_records)
            unmarked = total_students - marked

            self._make_stat_card(cards, "Total Students", str(total_students), self.colors["primary"])
            self._make_stat_card(cards, "Present Today", str(present), self.colors["success"])
            self._make_stat_card(cards, "Absent Today", str(absent), self.colors["danger"])
            self._make_stat_card(cards, "Late Today", str(late), self.colors["warning"])
            self._make_stat_card(cards, "Not Marked", str(unmarked), self.colors["muted"])

            # Recent activity
            activity_card = tk.Frame(self.content, bg=self.colors["card"],
                                     highlightbackground=self.colors["border"],
                                     highlightthickness=1)
            activity_card.pack(fill="both", expand=True)

            tk.Label(activity_card, text="RECENT ATTENDANCE RECORDS",
                     font=("Segoe UI", 12, "bold"),
                     bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", padx=20, pady=(15, 10))

            table_frame = tk.Frame(activity_card, bg=self.colors["card"])
            table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

            tree = ttk.Treeview(table_frame, columns=("date", "name", "roll", "status"),
                                show="headings", selectmode="browse")
            tree.heading("date", text="Date")
            tree.heading("name", text="Student Name")
            tree.heading("roll", text="Roll No")
            tree.heading("status", text="Status")
            tree.column("date", width=120)
            tree.column("name", width=250)
            tree.column("roll", width=100)
            tree.column("status", width=100)

            vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            tree.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")

            # Tags for status colors
            tree.tag_configure("P", background="#dcfce7", foreground="#166534")
            tree.tag_configure("A", background="#fee2e2", foreground="#991b1b")
            tree.tag_configure("L", background="#fef3c7", foreground="#92400e")

            recent = sorted(self.attendance, key=lambda x: x.get("date", ""), reverse=True)[:50]
            for rec in recent:
                student = next((s for s in self.students if s.get("id") == rec.get("student_id")), None)
                if not student:
                    continue
                status_text = {"P": "Present", "A": "Absent", "L": "Late"}.get(rec.get("status"), "?")
                tree.insert("", "end", values=(
                    rec.get("date", ""),
                    student.get("name", ""),
                    student.get("roll_no", ""),
                    status_text
                ), tags=(rec.get("status"),))

            if not recent:
                tk.Label(activity_card, text="No attendance records yet. Start by marking attendance!",
                         font=("Segoe UI", 11, "italic"),
                         bg=self.colors["card"], fg=self.colors["muted"],
                         pady=30).pack(fill="x")

        except Exception as e:
            print(f"Dashboard error: {e}")

    def _make_stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=self.colors["card"],
                        highlightbackground=self.colors["border"],
                        highlightthickness=1)
        card.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(card, text=value,
                 font=("Segoe UI", 26, "bold"),
                 bg=self.colors["card"], fg=color).pack(pady=(20, 5))
        tk.Label(card, text=title,
                 font=("Segoe UI", 10, "bold"),
                 bg=self.colors["card"], fg=self.colors["muted"]).pack(pady=(0, 20))

    # ---------------- STUDENTS ----------------
    def _build_students(self):
        try:
            title = tk.Label(self.content, text="STUDENT MANAGEMENT",
                             font=("Segoe UI", 18, "bold"),
                             bg=self.colors["bg"], fg=self.colors["text"])
            title.pack(anchor="w", pady=(0, 15))

            # Top bar: search + add button
            top = tk.Frame(self.content, bg=self.colors["card"],
                           highlightbackground=self.colors["border"],
                           highlightthickness=1)
            top.pack(fill="x", pady=(0, 15))

            inner = tk.Frame(top, bg=self.colors["card"])
            inner.pack(fill="x", padx=15, pady=12)

            tk.Label(inner, text="Search:",
                     font=("Segoe UI", 10, "bold"),
                     bg=self.colors["card"], fg=self.colors["muted"]).pack(side="left")

            self.student_search_var = tk.StringVar()
            search_entry = tk.Entry(inner, textvariable=self.student_search_var,
                                    font=("Segoe UI", 10),
                                    bg=self.colors["input_bg"], bd=1, relief="solid")
            search_entry.pack(side="left", fill="x", expand=True, padx=10, ipady=4)
            self.student_search_var.trace_add("write", lambda *a: self._refresh_student_table())

            tk.Button(inner, text="+ Add Student",
                      font=("Segoe UI", 10, "bold"),
                      bg=self.colors["success"], fg="white",
                      activebackground="#059669",
                      bd=0, padx=15, pady=6, cursor="hand2",
                      command=self._add_student_dialog).pack(side="right")

            # Table
            table_frame = tk.Frame(self.content, bg=self.colors["card"],
                                   highlightbackground=self.colors["border"],
                                   highlightthickness=1)
            table_frame.pack(fill="both", expand=True)

            cols = ("id", "roll_no", "name", "class_name", "contact", "added_date")
            self.student_tree = ttk.Treeview(table_frame, columns=cols,
                                             show="headings", selectmode="browse")
            self.student_tree.heading("id", text="ID")
            self.student_tree.heading("roll_no", text="Roll No")
            self.student_tree.heading("name", text="Name")
            self.student_tree.heading("class_name", text="Class")
            self.student_tree.heading("contact", text="Contact")
            self.student_tree.heading("added_date", text="Added On")
            self.student_tree.column("id", width=50)
            self.student_tree.column("roll_no", width=90)
            self.student_tree.column("name", width=220)
            self.student_tree.column("class_name", width=120)
            self.student_tree.column("contact", width=140)
            self.student_tree.column("added_date", width=120)

            vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.student_tree.yview)
            self.student_tree.configure(yscrollcommand=vsb.set)
            self.student_tree.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")

            # Action buttons
            actions = tk.Frame(self.content, bg=self.colors["bg"])
            actions.pack(fill="x", pady=(10, 0))

            tk.Button(actions, text="Edit Selected",
                      font=("Segoe UI", 10, "bold"),
                      bg=self.colors["primary"], fg="white",
                      activebackground=self.colors["primary_dark"],
                      bd=0, padx=15, pady=6, cursor="hand2",
                      command=self._edit_student_dialog).pack(side="left", padx=(0, 8))

            tk.Button(actions, text="Delete Selected",
                      font=("Segoe UI", 10, "bold"),
                      bg=self.colors["danger"], fg="white",
                      activebackground="#dc2626",
                      bd=0, padx=15, pady=6, cursor="hand2",
                      command=self._delete_student).pack(side="left")

            self.student_count_label = tk.Label(actions, text="",
                                                font=("Segoe UI", 10),
                                                bg=self.colors["bg"],
                                                fg=self.colors["muted"])
            self.student_count_label.pack(side="right")

            self._refresh_student_table()
        except Exception as e:
            print(f"Students page error: {e}")

    def _refresh_student_table(self):
        try:
            for row in self.student_tree.get_children():
                self.student_tree.delete(row)

            search = self.student_search_var.get().lower().strip()
            count = 0
            for s in self.students:
                if search:
                    hay = f"{s.get('name', '')} {s.get('roll_no', '')} {s.get('class_name', '')}".lower()
                    if search not in hay:
                        continue
                self.student_tree.insert("", "end", values=(
                    s.get("id", ""),
                    s.get("roll_no", ""),
                    s.get("name", ""),
                    s.get("class_name", ""),
                    s.get("contact", ""),
                    s.get("added_date", "")
                ))
                count += 1
            self.student_count_label.config(text=f"Showing {count} of {len(self.students)} students")
        except Exception as e:
            print(f"Refresh error: {e}")

    def _student_dialog(self, title, existing=None):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("420x360")
        dialog.configure(bg=self.colors["card"])
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text=title,
                 font=("Segoe UI", 14, "bold"),
                 bg=self.colors["card"], fg=self.colors["text"]).pack(pady=(15, 15))

        fields = {}
        field_defs = [
            ("Name", "name"),
            ("Roll Number", "roll_no"),
            ("Class", "class_name"),
            ("Contact", "contact"),
        ]
        for label_text, key in field_defs:
            row = tk.Frame(dialog, bg=self.colors["card"])
            row.pack(fill="x", padx=30, pady=5)
            tk.Label(row, text=label_text + ":",
                     font=("Segoe UI", 10, "bold"),
                     bg=self.colors["card"], fg=self.colors["text"],
                     width=12, anchor="w").pack(side="left")
            entry = tk.Entry(row, font=("Segoe UI", 10),
                             bg=self.colors["input_bg"], bd=1, relief="solid")
            entry.pack(side="left", fill="x", expand=True, ipady=4)
            fields[key] = entry
            if existing:
                entry.insert(0, existing.get(key, ""))

        result = {"data": None}

        def on_save():
            try:
                data = {k: e.get().strip() for k, e in fields.items()}
                if not data["name"]:
                    messagebox.showwarning("Validation", "Name is required.", parent=dialog)
                    return
                if not data["roll_no"]:
                    messagebox.showwarning("Validation", "Roll number is required.", parent=dialog)
                    return
                # Check duplicate roll_no
                for s in self.students:
                    if s.get("roll_no") == data["roll_no"] and (not existing or s.get("id") != existing.get("id")):
                        messagebox.showwarning("Validation",
                                               f"Roll number '{data['roll_no']}' already exists.",
                                               parent=dialog)
                        return
                result["data"] = data
                dialog.destroy()
            except Exception as e:
                print(f"Dialog save error: {e}")

        btn_frame = tk.Frame(dialog, bg=self.colors["card"])
        btn_frame.pack(fill="x", padx=30, pady=20)

        tk.Button(btn_frame, text="Save",
                  font=("Segoe UI", 10, "bold"),
                  bg=self.colors["success"], fg="white",
                  activebackground="#059669",
                  bd=0, padx=20, pady=6, cursor="hand2",
                  command=on_save).pack(side="left", expand=True)

        tk.Button(btn_frame, text="Cancel",
                  font=("Segoe UI", 10, "bold"),
                  bg=self.colors["muted"], fg="white",
                  activebackground="#475569",
                  bd=0, padx=20, pady=6, cursor="hand2",
                  command=dialog.destroy).pack(side="right", expand=True)

        dialog.wait_window()
        return result["data"]

    def _add_student_dialog(self):
        try:
            data = self._student_dialog("Add New Student")
            if not data:
                return
            new_id = max([s.get("id", 0) for s in self.students], default=0) + 1
            data["id"] = new_id
            data["added_date"] = datetime.now().strftime("%d-%m-%Y")
            self.students.append(data)
            self.save_data()
            self._refresh_student_table()
            self.status.config(text=f"Added student: {data['name']}")
        except Exception as e:
            print(f"Add student error: {e}")

    def _edit_student_dialog(self):
        try:
            sel = self.student_tree.selection()
            if not sel:
                messagebox.showwarning("Selection", "Please select a student to edit.")
                return
            item = self.student_tree.item(sel[0])
            sid = item["values"][0]
            student = next((s for s in self.students if s.get("id") == sid), None)
            if not student:
                return
            data = self._student_dialog("Edit Student", existing=student)
            if not data:
                return
            student.update(data)
            self.save_data()
            self._refresh_student_table()
            self.status.config(text=f"Updated: {data['name']}")
        except Exception as e:
            print(f"Edit student error: {e}")

    def _delete_student(self):
        try:
            sel = self.student_tree.selection()
            if not sel:
                messagebox.showwarning("Selection", "Please select a student to delete.")
                return
            item = self.student_tree.item(sel[0])
            sid = item["values"][0]
            name = item["values"][2]
            if not messagebox.askyesno("Confirm Delete",
                                       f"Delete student '{name}'?\n\nThis will also delete all their attendance records."):
                return
            self.students = [s for s in self.students if s.get("id") != sid]
            self.attendance = [a for a in self.attendance if a.get("student_id") != sid]
            self.save_data()
            self._refresh_student_table()
            self.status.config(text=f"Deleted: {name}")
        except Exception as e:
            print(f"Delete student error: {e}")

    # ---------------- MARK ATTENDANCE ----------------
    def _build_mark_attendance(self):
        try:
            title = tk.Label(self.content, text="MARK ATTENDANCE",
                             font=("Segoe UI", 18, "bold"),
                             bg=self.colors["bg"], fg=self.colors["text"])
            title.pack(anchor="w", pady=(0, 15))

            if not self.students:
                tk.Label(self.content, text="No students added yet. Add students first!",
                         font=("Segoe UI", 12, "italic"),
                         bg=self.colors["card"], fg=self.colors["muted"],
                         pady=50).pack(fill="x")
                return

            # Date selector
            date_frame = tk.Frame(self.content, bg=self.colors["card"],
                                  highlightbackground=self.colors["border"],
                                  highlightthickness=1)
            date_frame.pack(fill="x", pady=(0, 15))

            inner = tk.Frame(date_frame, bg=self.colors["card"])
            inner.pack(fill="x", padx=15, pady=12)

            tk.Label(inner, text="Date:",
                     font=("Segoe UI", 10, "bold"),
                     bg=self.colors["card"], fg=self.colors["text"]).pack(side="left")

            self.att_date_var = tk.StringVar(value=date.today().isoformat())
            date_entry = tk.Entry(inner, textvariable=self.att_date_var,
                                  font=("Segoe UI", 10),
                                  bg=self.colors["input_bg"], bd=1, relief="solid",
                                  width=15)
            date_entry.pack(side="left", padx=10, ipady=4)
            tk.Label(inner, text="(YYYY-MM-DD)",
                     font=("Segoe UI", 9),
                     bg=self.colors["card"], fg=self.colors["muted"]).pack(side="left")

            tk.Button(inner, text="Load",
                      font=("Segoe UI", 10, "bold"),
                      bg=self.colors["primary"], fg="white",
                      activebackground=self.colors["primary_dark"],
                      bd=0, padx=15, pady=4, cursor="hand2",
                      command=self._load_attendance_for_date).pack(side="left", padx=10)

            tk.Button(inner, text="Save All",
                      font=("Segoe UI", 10, "bold"),
                      bg=self.colors["success"], fg="white",
                      activebackground="#059669",
                      bd=0, padx=15, pady=4, cursor="hand2",
                      command=self._save_attendance).pack(side="right")

            tk.Button(inner, text="Mark All Present",
                      font=("Segoe UI", 10, "bold"),
                      bg=self.colors["accent"], fg="white",
                      activebackground="#7c3aed",
                      bd=0, padx=15, pady=4, cursor="hand2",
                      command=lambda: self._bulk_mark("P")).pack(side="right", padx=5)

            # Student list with radio buttons for status
            list_frame = tk.Frame(self.content, bg=self.colors["card"],
                                  highlightbackground=self.colors["border"],
                                  highlightthickness=1)
            list_frame.pack(fill="both", expand=True)

            header = tk.Frame(list_frame, bg=self.colors["primary"])
            header.pack(fill="x")

            tk.Label(header, text="Roll No",
                     font=("Segoe UI", 10, "bold"),
                     bg=self.colors["primary"], fg="white",
                     width=10, anchor="w").pack(side="left", padx=10, pady=8)
            tk.Label(header, text="Student Name",
                     font=("Segoe UI", 10, "bold"),
                     bg=self.colors["primary"], fg="white",
                     width=30, anchor="w").pack(side="left", padx=10, pady=8)
            tk.Label(header, text="Class",
                     font=("Segoe UI", 10, "bold"),
                     bg=self.colors["primary"], fg="white",
                     width=12, anchor="w").pack(side="left", padx=10, pady=8)
            tk.Label(header, text="Status",
                     font=("Segoe UI", 10, "bold"),
                     bg=self.colors["primary"], fg="white",
                     width=30, anchor="w").pack(side="left", padx=10, pady=8)

            scroll_frame = tk.Frame(list_frame, bg=self.colors["card"])
            scroll_frame.pack(fill="both", expand=True)

            canvas = tk.Canvas(scroll_frame, bg=self.colors["card"], highlightthickness=0)
            sb = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
            self.att_inner = tk.Frame(canvas, bg=self.colors["card"])

            self.att_inner.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=self.att_inner, anchor="nw")
            canvas.configure(yscrollcommand=sb.set)
            canvas.pack(side="left", fill="both", expand=True)
            sb.pack(side="right", fill="y")

            canvas.bind_all("<MouseWheel>",
                            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"),
                            add="+")

            self.att_vars = {}
            sorted_students = sorted(self.students, key=lambda s: (s.get("class_name", ""), s.get("roll_no", "")))
            for student in sorted_students:
                self._make_attendance_row(self.att_inner, student)

        except Exception as e:
            print(f"Mark attendance page error: {e}")

    def _make_attendance_row(self, parent, student):
        try:
            row = tk.Frame(parent, bg=self.colors["card"],
                           highlightbackground=self.colors["border"],
                           highlightthickness=1)
            row.pack(fill="x", padx=10, pady=3)

            tk.Label(row, text=student.get("roll_no", ""),
                     font=("Segoe UI", 10),
                     bg=self.colors["card"], fg=self.colors["text"],
                     width=10, anchor="w").pack(side="left", padx=10, pady=8)
            tk.Label(row, text=student.get("name", ""),
                     font=("Segoe UI", 10, "bold"),
                     bg=self.colors["card"], fg=self.colors["text"],
                     width=30, anchor="w").pack(side="left", padx=10, pady=8)
            tk.Label(row, text=student.get("class_name", ""),
                     font=("Segoe UI", 10),
                     bg=self.colors["card"], fg=self.colors["muted"],
                     width=12, anchor="w").pack(side="left", padx=10, pady=8)

            var = tk.StringVar(value="A")  # Default absent
            self.att_vars[student["id"]] = var

            status_frame = tk.Frame(row, bg=self.colors["card"])
            status_frame.pack(side="left", padx=10, pady=8)

            tk.Radiobutton(status_frame, text="Present", variable=var, value="P",
                           bg=self.colors["card"], activebackground=self.colors["card"],
                           selectcolor=self.colors["card"],
                           fg=self.colors["success"], activeforeground=self.colors["success"],
                           font=("Segoe UI", 9, "bold")).pack(side="left", padx=3)
            tk.Radiobutton(status_frame, text="Absent", variable=var, value="A",
                           bg=self.colors["card"], activebackground=self.colors["card"],
                           selectcolor=self.colors["card"],
                           fg=self.colors["danger"], activeforeground=self.colors["danger"],
                           font=("Segoe UI", 9, "bold")).pack(side="left", padx=3)
            tk.Radiobutton(status_frame, text="Late", variable=var, value="L",
                           bg=self.colors["card"], activebackground=self.colors["card"],
                           selectcolor=self.colors["card"],
                           fg=self.colors["warning"], activeforeground=self.colors["warning"],
                           font=("Segoe UI", 9, "bold")).pack(side="left", padx=3)
        except Exception as e:
            print(f"Row error: {e}")

    def _load_attendance_for_date(self):
        try:
            date_str = self.att_date_var.get().strip()
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Invalid Date", "Please enter date in YYYY-MM-DD format.")
                return

            count = 0
            for rec in self.attendance:
                if rec.get("date") == date_str:
                    sid = rec.get("student_id")
                    if sid in self.att_vars:
                        self.att_vars[sid].set(rec.get("status", "A"))
                        count += 1
            self.status.config(text=f"Loaded {count} records for {date_str}")
        except Exception as e:
            print(f"Load attendance error: {e}")

    def _bulk_mark(self, status):
        try:
            for var in self.att_vars.values():
                var.set(status)
            self.status.config(text=f"All marked as {status}")
        except Exception as e:
            print(f"Bulk mark error: {e}")

    def _save_attendance(self):
        try:
            date_str = self.att_date_var.get().strip()
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning("Invalid Date", "Please enter date in YYYY-MM-DD format.")
                return

            # Remove existing records for this date
            self.attendance = [a for a in self.attendance if a.get("date") != date_str]

            # Add new records
            for sid, var in self.att_vars.items():
                self.attendance.append({
                    "date": date_str,
                    "student_id": sid,
                    "status": var.get()
                })

            self.save_data()
            count = len(self.att_vars)
            self.status.config(text=f"Saved attendance for {count} students on {date_str}")
            messagebox.showinfo("Success", f"Attendance saved for {count} students on {date_str}.")
        except Exception as e:
            print(f"Save attendance error: {e}")
            messagebox.showerror("Error", f"Could not save attendance: {e}")

    # ---------------- REPORTS ----------------
    def _build_reports(self):
        try:
            title = tk.Label(self.content, text="ATTENDANCE REPORTS",
                             font=("Segoe UI", 18, "bold"),
                             bg=self.colors["bg"], fg=self.colors["text"])
            title.pack(anchor="w", pady=(0, 15))

            # Tabs
            tabs = tk.Frame(self.content, bg=self.colors["card"],
                            highlightbackground=self.colors["border"],
                            highlightthickness=1)
            tabs.pack(fill="x", pady=(0, 15))

            tab_inner = tk.Frame(tabs, bg=self.colors["card"])
            tab_inner.pack(fill="x", padx=15, pady=10)

            self.report_type_var = tk.StringVar(value="date")

            tk.Radiobutton(tab_inner, text="By Date", variable=self.report_type_var, value="date",
                           bg=self.colors["card"], activebackground=self.colors["card"],
                           selectcolor=self.colors["card"],
                           font=("Segoe UI", 10, "bold"),
                           command=self._refresh_report).pack(side="left", padx=10)

            tk.Radiobutton(tab_inner, text="By Student", variable=self.report_type_var, value="student",
                           bg=self.colors["card"], activebackground=self.colors["card"],
                           selectcolor=self.colors["card"],
                           font=("Segoe UI", 10, "bold"),
                           command=self._refresh_report).pack(side="left", padx=10)

            tk.Button(tab_inner, text="Export CSV",
                      font=("Segoe UI", 10, "bold"),
                      bg=self.colors["success"], fg="white",
                      activebackground="#059669",
                      bd=0, padx=15, pady=4, cursor="hand2",
                      command=self._export_report_csv).pack(side="right")

            # Filter
            filter_frame = tk.Frame(self.content, bg=self.colors["card"],
                                    highlightbackground=self.colors["border"],
                                    highlightthickness=1)
            filter_frame.pack(fill="x", pady=(0, 15))

            self.report_filter_var = tk.StringVar()
            filter_entry = tk.Entry(filter_frame, textvariable=self.report_filter_var,
                                    font=("Segoe UI", 10),
                                    bg=self.colors["input_bg"], bd=0, relief="flat")
            filter_entry.pack(fill="x", padx=15, ipady=8)
            self.report_filter_var.trace_add("write", lambda *a: self._refresh_report())

            self.filter_hint = tk.Label(filter_frame, text="Enter date (YYYY-MM-DD) to filter",
                                        font=("Segoe UI", 9),
                                        bg=self.colors["card"], fg=self.colors["muted"])
            self.filter_hint.pack(anchor="w", padx=15, pady=(0, 8))

            # Report table
            table_frame = tk.Frame(self.content, bg=self.colors["card"],
                                   highlightbackground=self.colors["border"],
                                   highlightthickness=1)
            table_frame.pack(fill="both", expand=True)

            self.report_tree = ttk.Treeview(table_frame, show="headings", selectmode="browse")
            vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.report_tree.yview)
            self.report_tree.configure(yscrollcommand=vsb.set)
            self.report_tree.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")

            self.report_tree.tag_configure("P", background="#dcfce7", foreground="#166534")
            self.report_tree.tag_configure("A", background="#fee2e2", foreground="#991b1b")
            self.report_tree.tag_configure("L", background="#fef3c7", foreground="#92400e")

            # Summary
            self.report_summary = tk.Label(self.content, text="",
                                           font=("Segoe UI", 10, "bold"),
                                           bg=self.colors["bg"], fg=self.colors["text"])
            self.report_summary.pack(fill="x", pady=(10, 0))

            self._refresh_report()
        except Exception as e:
            print(f"Reports page error: {e}")

    def _refresh_report(self):
        try:
            for col in self.report_tree["columns"]:
                self.report_tree.heading(col, text="")
            self.report_tree["columns"] = ()

            report_type = self.report_type_var.get()
            filter_text = self.report_filter_var.get().strip().lower()

            if report_type == "date":
                self.filter_hint.config(text="Enter date (YYYY-MM-DD) or student name to filter")
                self.report_tree["columns"] = ("date", "roll_no", "name", "class_name", "status")
                self.report_tree.heading("date", text="Date")
                self.report_tree.heading("roll_no", text="Roll No")
                self.report_tree.heading("name", text="Name")
                self.report_tree.heading("class_name", text="Class")
                self.report_tree.heading("status", text="Status")
                self.report_tree.column("date", width=120)
                self.report_tree.column("roll_no", width=90)
                self.report_tree.column("name", width=220)
                self.report_tree.column("class_name", width=120)
                self.report_tree.column("status", width=100)

                rows = []
                for rec in self.attendance:
                    student = next((s for s in self.students if s.get("id") == rec.get("student_id")), None)
                    if not student:
                        continue
                    if filter_text:
                        hay = f"{rec.get('date', '')} {student.get('name', '')} {student.get('roll_no', '')}".lower()
                        if filter_text not in hay:
                            continue
                    status_text = {"P": "Present", "A": "Absent", "L": "Late"}.get(rec.get("status"), "?")
                    rows.append((
                        rec.get("date", ""),
                        student.get("roll_no", ""),
                        student.get("name", ""),
                        student.get("class_name", ""),
                        status_text,
                        rec.get("status")
                    ))

                rows.sort(key=lambda x: x[0], reverse=True)

                for row in self.report_tree.get_children():
                    self.report_tree.delete(row)
                for r in rows:
                    self.report_tree.insert("", "end", values=r[:5], tags=(r[5],))

                present = sum(1 for r in rows if r[5] == "P")
                absent = sum(1 for r in rows if r[5] == "A")
                late = sum(1 for r in rows if r[5] == "L")
                self.report_summary.config(
                    text=f"Total: {len(rows)}  |  Present: {present}  |  Absent: {absent}  |  Late: {late}"
                )

            else:  # student
                self.filter_hint.config(text="Enter student name or roll number to filter")
                self.report_tree["columns"] = ("roll_no", "name", "class_name", "total", "present", "absent", "late", "percent")
                self.report_tree.heading("roll_no", text="Roll No")
                self.report_tree.heading("name", text="Name")
                self.report_tree.heading("class_name", text="Class")
                self.report_tree.heading("total", text="Total Days")
                self.report_tree.heading("present", text="Present")
                self.report_tree.heading("absent", text="Absent")
                self.report_tree.heading("late", text="Late")
                self.report_tree.heading("percent", text="Attendance %")
                for c in ("roll_no", "name", "class_name", "total", "present", "absent", "late", "percent"):
                    self.report_tree.column(c, width=110 if c in ("name", "class_name") else 90)

                for row in self.report_tree.get_children():
                    self.report_tree.delete(row)

                count = 0
                for student in self.students:
                    if filter_text:
                        hay = f"{student.get('name', '')} {student.get('roll_no', '')}".lower()
                        if filter_text not in hay:
                            continue
                    recs = [a for a in self.attendance if a.get("student_id") == student.get("id")]
                    total = len(recs)
                    present = sum(1 for a in recs if a.get("status") == "P")
                    absent = sum(1 for a in recs if a.get("status") == "A")
                    late = sum(1 for a in recs if a.get("status") == "L")
                    percent = ((present + late) / total * 100) if total > 0 else 0
                    self.report_tree.insert("", "end", values=(
                        student.get("roll_no", ""),
                        student.get("name", ""),
                        student.get("class_name", ""),
                        total, present, absent, late,
                        f"{percent:.1f}%"
                    ))
                    count += 1

                self.report_summary.config(text=f"Showing {count} students")

        except Exception as e:
            print(f"Refresh report error: {e}")

    def _export_report_csv(self):
        try:
            if not self.report_tree.get_children():
                messagebox.showinfo("Export", "No data to export.")
                return

            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            if not path:
                return

            cols = self.report_tree["columns"]
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                for row_id in self.report_tree.get_children():
                    writer.writerow(self.report_tree.item(row_id)["values"])

            messagebox.showinfo("Success", f"Report exported to:\n{path}")
            self.status.config(text=f"Exported to {os.path.basename(path)}")
        except IOError as e:
            messagebox.showerror("Export Error", f"Could not export:\n{e}")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = AttendanceSystem(root)
        root.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()