"""
============================================================
  TO DO LIST MANAGER - Professional Edition
  Author: AI Assistant
  Language: Python 3 (Tkinter - built-in)
  Run: python todo_manager.py
============================================================
"""

import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime, date

# ---------------- CONFIGURATION ----------------
COLORS = {
    "bg":        "#0f172a",
    "panel":     "#1e293b",
    "panel2":    "#334155",
    "fg":        "#e2e8f0",
    "accent":    "#38bdf8",
    "success":   "#22c55e",
    "danger":    "#ef4444",
    "warning":   "#f59e0b",
    "muted":     "#94a3b8",
    "high":      "#ef4444",
    "medium":    "#f59e0b",
    "low":       "#22c55e",
}

CATEGORIES = ["Work", "Personal", "Shopping", "Other"]
DATA_FILE = "todo_data.json"


class TodoManager:
    def __init__(self, root):
        self.root = root
        self.root.title("✅ To Do List Manager")
        self.root.geometry("1100x750")
        self.root.minsize(1000, 700)
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(True, True)

        # Center the window
        self.root.update_idletasks()
        w, h = 1100, 750
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # Data
        self.tasks = []
        self.current_filter = "All"
        self.current_sort = "name"
        self.search_query = ""
        self.editing_task_id = None

        self._build_ui()
        self._load_data()
        self._refresh_task_list()
        self._update_stats()

        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.task_entry.focus_set())
        self.root.bind("<Control-f>", lambda e: self.search_entry.focus_set())
        self.root.bind("<Control-q>", lambda e: self.root.quit())

    # ---------------- UI BUILD ----------------
    def _build_ui(self):
        # Title
        title = tk.Label(
            self.root, text="✅ TO DO LIST MANAGER",
            font=("Segoe UI", 24, "bold"),
            bg=COLORS["bg"], fg=COLORS["accent"]
        )
        title.pack(pady=(15, 5))

        subtitle = tk.Label(
            self.root, text="Organize your life, one task at a time! 📋",
            font=("Segoe UI", 11),
            bg=COLORS["bg"], fg=COLORS["muted"]
        )
        subtitle.pack()

        # Main container
        main = tk.Frame(self.root, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=20, pady=10)

        # LEFT PANEL - Input & Controls
        left = tk.Frame(main, bg=COLORS["panel"], highlightbackground=COLORS["panel2"], highlightthickness=1)
        left.pack(side="left", fill="both", expand=False, padx=(0, 10))
        left.config(width=380)
        left.pack_propagate(False)

        # Task input section
        tk.Label(left, text="➕ Add New Task", font=("Segoe UI", 13, "bold"),
                 bg=COLORS["panel"], fg=COLORS["accent"]).pack(anchor="w", padx=15, pady=(15, 10))

        # Task name
        tk.Label(left, text="Task Name:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(anchor="w", padx=15)
        self.task_entry = tk.Entry(left, font=("Segoe UI", 11),
                                   bg=COLORS["panel2"], fg=COLORS["fg"],
                                   insertbackground=COLORS["fg"],
                                   relief="flat", bd=5)
        self.task_entry.pack(fill="x", padx=15, pady=(0, 10))
        self.task_entry.bind("<Return>", lambda e: self._add_task())

        # Priority
        tk.Label(left, text="Priority:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(anchor="w", padx=15)
        self.priority_var = tk.StringVar(value="Medium")
        priority_frame = tk.Frame(left, bg=COLORS["panel"])
        priority_frame.pack(fill="x", padx=15, pady=(0, 10))
        for p in ["High", "Medium", "Low"]:
            rb = tk.Radiobutton(
                priority_frame, text=p, variable=self.priority_var, value=p,
                font=("Segoe UI", 10), bg=COLORS["panel"], fg=COLORS["fg"],
                selectcolor=COLORS["panel2"], activebackground=COLORS["panel"],
                activeforeground=COLORS["accent"]
            )
            rb.pack(side="left", padx=5)

        # Category
        tk.Label(left, text="Category:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(anchor="w", padx=15)
        self.category_var = tk.StringVar(value="Work")
        category_menu = tk.OptionMenu(left, self.category_var, *CATEGORIES)
        category_menu.config(font=("Segoe UI", 10), bg=COLORS["panel2"], fg=COLORS["fg"],
                             activebackground=COLORS["accent"], relief="flat")
        category_menu.pack(fill="x", padx=15, pady=(0, 10))

        # Due date
        tk.Label(left, text="Due Date (YYYY-MM-DD, optional):", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(anchor="w", padx=15)
        self.date_entry = tk.Entry(left, font=("Segoe UI", 11),
                                   bg=COLORS["panel2"], fg=COLORS["fg"],
                                   insertbackground=COLORS["fg"],
                                   relief="flat", bd=5)
        self.date_entry.pack(fill="x", padx=15, pady=(0, 10))

        # Add/Update button
        self.add_btn = tk.Button(
            left, text="➕ Add Task", font=("Segoe UI", 12, "bold"),
            bg=COLORS["success"], fg="white", activebackground="#16a34a",
            relief="flat", pady=10, cursor="hand2",
            command=self._add_task
        )
        self.add_btn.pack(fill="x", padx=15, pady=(0, 10))

        # Cancel edit button (hidden initially)
        self.cancel_btn = tk.Button(
            left, text="❌ Cancel Edit", font=("Segoe UI", 11, "bold"),
            bg=COLORS["danger"], fg="white", activebackground="#b91c1c",
            relief="flat", pady=8, cursor="hand2",
            command=self._cancel_edit
        )

        # Filters
        tk.Label(left, text="🔍 Filter & Search", font=("Segoe UI", 13, "bold"),
                 bg=COLORS["panel"], fg=COLORS["accent"]).pack(anchor="w", padx=15, pady=(15, 10))

        # Search
        self.search_entry = tk.Entry(left, font=("Segoe UI", 11),
                                     bg=COLORS["panel2"], fg=COLORS["fg"],
                                     insertbackground=COLORS["fg"],
                                     relief="flat", bd=5)
        self.search_entry.pack(fill="x", padx=15, pady=(0, 10))
        self.search_entry.insert(0, "Search tasks...")
        self.search_entry.bind("<FocusIn>", self._clear_search_placeholder)
        self.search_entry.bind("<FocusOut>", self._restore_search_placeholder)
        self.search_entry.bind("<KeyRelease>", lambda e: self._on_search())

        # Filter buttons
        filter_frame = tk.Frame(left, bg=COLORS["panel"])
        filter_frame.pack(fill="x", padx=15, pady=(0, 10))
        self.filter_buttons = {}
        for f in ["All", "Active", "Completed"]:
            btn = tk.Button(
                filter_frame, text=f, font=("Segoe UI", 10, "bold"),
                bg=COLORS["panel2"], fg=COLORS["fg"],
                activebackground=COLORS["accent"], relief="flat",
                padx=10, pady=5, cursor="hand2",
                command=lambda f=f: self._set_filter(f)
            )
            btn.pack(side="left", padx=2, expand=True, fill="x")
            self.filter_buttons[f] = btn
        self._update_filter_buttons()

        # Sort
        tk.Label(left, text="Sort by:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(anchor="w", padx=15)
        self.sort_var = tk.StringVar(value="name")
        sort_menu = tk.OptionMenu(left, self.sort_var, "name", "priority", "date", command=self._on_sort_change)
        sort_menu.config(font=("Segoe UI", 10), bg=COLORS["panel2"], fg=COLORS["fg"],
                         activebackground=COLORS["accent"], relief="flat")
        sort_menu.pack(fill="x", padx=15, pady=(0, 10))

        # Clear completed
        clear_btn = tk.Button(
            left, text="🗑️ Clear Completed", font=("Segoe UI", 11, "bold"),
            bg=COLORS["warning"], fg="white", activebackground="#d97706",
            relief="flat", pady=8, cursor="hand2",
            command=self._clear_completed
        )
        clear_btn.pack(fill="x", padx=15, pady=(10, 10))

        # Statistics
        tk.Label(left, text="📊 Statistics", font=("Segoe UI", 13, "bold"),
                 bg=COLORS["panel"], fg=COLORS["accent"]).pack(anchor="w", padx=15, pady=(10, 5))

        stats_frame = tk.Frame(left, bg=COLORS["panel2"])
        stats_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.stats_labels = {}
        stats_data = [
            ("total", "Total:"),
            ("completed", "Completed:"),
            ("pending", "Pending:"),
            ("rate", "Progress:"),
        ]
        for key, label_text in stats_data:
            row = tk.Frame(stats_frame, bg=COLORS["panel2"])
            row.pack(fill="x", padx=10, pady=3)
            tk.Label(row, text=label_text, font=("Segoe UI", 10),
                     bg=COLORS["panel2"], fg=COLORS["fg"], anchor="w").pack(side="left")
            lbl = tk.Label(row, text="0", font=("Segoe UI", 10, "bold"),
                           bg=COLORS["panel2"], fg=COLORS["success"], anchor="e")
            lbl.pack(side="right")
            self.stats_labels[key] = lbl

        # Progress bar
        self.progress_canvas = tk.Canvas(left, height=20, bg=COLORS["panel2"],
                                         highlightthickness=0)
        self.progress_canvas.pack(fill="x", padx=15, pady=(0, 15))

        # RIGHT PANEL - Task List
        right = tk.Frame(main, bg=COLORS["panel"], highlightbackground=COLORS["panel2"], highlightthickness=1)
        right.pack(side="right", fill="both", expand=True)

        # Task list header
        tk.Label(right, text="📋 Your Tasks", font=("Segoe UI", 14, "bold"),
                 bg=COLORS["panel"], fg=COLORS["accent"]).pack(anchor="w", padx=15, pady=(15, 10))

        # Task list container
        list_frame = tk.Frame(right, bg=COLORS["panel2"])
        list_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Scrollable canvas for tasks
        self.canvas = tk.Canvas(list_frame, bg=COLORS["panel2"], highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS["panel2"])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel binding
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Empty state
        self.empty_label = tk.Label(self.scrollable_frame, text="📝 No tasks yet!\nAdd your first task to get started.",
                                    font=("Segoe UI", 12), bg=COLORS["panel2"], fg=COLORS["muted"])
        self.empty_label.pack(pady=50)

        # Status bar
        self.status = tk.Label(self.root, text="Ready! Press Ctrl+N to add task, Ctrl+F to search, Ctrl+Q to quit.",
                               font=("Segoe UI", 10), bg=COLORS["bg"], fg=COLORS["muted"],
                               anchor="w", padx=20)
        self.status.pack(side="bottom", fill="x", pady=5)

    # ---------------- TASK MANAGEMENT ----------------
    def _add_task(self):
        task_name = self.task_entry.get().strip()
        if not task_name:
            messagebox.showwarning("⚠️ Error", "Task name cannot be empty!")
            return

        priority = self.priority_var.get()
        category = self.category_var.get()
        due_date_str = self.date_entry.get().strip()

        # Validate date
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                if due_date < date.today():
                    messagebox.showwarning("⚠️ Warning", "Due date cannot be in the past!")
                    return
            except ValueError:
                messagebox.showerror("⚠️ Error", "Invalid date format! Use YYYY-MM-DD")
                return

        if self.editing_task_id is not None:
            # Update existing task
            for task in self.tasks:
                if task["id"] == self.editing_task_id:
                    task["name"] = task_name
                    task["priority"] = priority
                    task["category"] = category
                    task["due_date"] = due_date.isoformat() if due_date else None
                    break
            self._cancel_edit()
            self.status.config(text=f"Task updated: {task_name}")
        else:
            # Add new task
            task = {
                "id": len(self.tasks) + 1 if not self.tasks else max(t["id"] for t in self.tasks) + 1,
                "name": task_name,
                "priority": priority,
                "category": category,
                "due_date": due_date.isoformat() if due_date else None,
                "completed": False,
                "created_at": datetime.now().isoformat()
            }
            self.tasks.append(task)
            self.status.config(text=f"Task added: {task_name}")

        # Clear inputs
        self.task_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.priority_var.set("Medium")
        self.category_var.set("Work")

        self._save_data()
        self._refresh_task_list()
        self._update_stats()
        self.task_entry.focus_set()

    def _toggle_complete(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = not task["completed"]
                status = "completed" if task["completed"] else "pending"
                self.status.config(text=f"Task marked as {status}: {task['name']}")
                break
        self._save_data()
        self._refresh_task_list()
        self._update_stats()

    def _edit_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                self.editing_task_id = task_id
                self.task_entry.delete(0, tk.END)
                self.task_entry.insert(0, task["name"])
                self.priority_var.set(task["priority"])
                self.category_var.set(task["category"])
                self.date_entry.delete(0, tk.END)
                if task["due_date"]:
                    self.date_entry.insert(0, task["due_date"])
                self.add_btn.config(text="✔ Update Task", bg=COLORS["accent"])
                self.cancel_btn.pack(fill="x", padx=15, pady=(0, 10))
                self.status.config(text=f"Editing task: {task['name']}")
                break

    def _cancel_edit(self):
        self.editing_task_id = None
        self.task_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.priority_var.set("Medium")
        self.category_var.set("Work")
        self.add_btn.config(text="➕ Add Task", bg=COLORS["success"])
        self.cancel_btn.pack_forget()
        self.status.config(text="Edit cancelled")

    def _delete_task(self, task_id):
        task_name = next((t["name"] for t in self.tasks if t["id"] == task_id), "")
        if messagebox.askyesno("🗑️ Delete Task", f"Are you sure you want to delete:\n\n{task_name}?"):
            self.tasks = [t for t in self.tasks if t["id"] != task_id]
            self._save_data()
            self._refresh_task_list()
            self._update_stats()
            self.status.config(text=f"Task deleted: {task_name}")

    def _clear_completed(self):
        completed_count = sum(1 for t in self.tasks if t["completed"])
        if completed_count == 0:
            messagebox.showinfo("ℹ️ Info", "No completed tasks to clear!")
            return
        if messagebox.askyesno("🗑️ Clear Completed", f"Are you sure you want to delete {completed_count} completed task(s)?"):
            self.tasks = [t for t in self.tasks if not t["completed"]]
            self._save_data()
            self._refresh_task_list()
            self._update_stats()
            self.status.config(text=f"Cleared {completed_count} completed task(s)")

    # ---------------- FILTER & SORT ----------------
    def _set_filter(self, filter_type):
        self.current_filter = filter_type
        self._update_filter_buttons()
        self._refresh_task_list()
        self.status.config(text=f"Filter: {filter_type}")

    def _update_filter_buttons(self):
        for f, btn in self.filter_buttons.items():
            if f == self.current_filter:
                btn.config(bg=COLORS["accent"], fg="#0f172a")
            else:
                btn.config(bg=COLORS["panel2"], fg=COLORS["fg"])

    def _on_sort_change(self, value):
        self.current_sort = value
        self._refresh_task_list()
        self.status.config(text=f"Sorted by: {value}")

    def _clear_search_placeholder(self, event):
        if self.search_entry.get() == "Search tasks...":
            self.search_entry.delete(0, tk.END)

    def _restore_search_placeholder(self, event):
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search tasks...")

    def _on_search(self):
        query = self.search_entry.get().strip()
        if query == "Search tasks...":
            query = ""
        self.search_query = query.lower()
        self._refresh_task_list()

    # ---------------- DISPLAY ----------------
    def _refresh_task_list(self):
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Filter tasks
        filtered = self.tasks[:]
        if self.current_filter == "Active":
            filtered = [t for t in filtered if not t["completed"]]
        elif self.current_filter == "Completed":
            filtered = [t for t in filtered if t["completed"]]

        # Search
        if self.search_query:
            filtered = [t for t in filtered if self.search_query in t["name"].lower()]

        # Sort
        if self.current_sort == "name":
            filtered.sort(key=lambda t: t["name"].lower())
        elif self.current_sort == "priority":
            priority_order = {"High": 0, "Medium": 1, "Low": 2}
            filtered.sort(key=lambda t: priority_order[t["priority"]])
        elif self.current_sort == "date":
            filtered.sort(key=lambda t: t["due_date"] or "9999-12-31")

        # Show empty state or tasks
        if not filtered:
            self.empty_label = tk.Label(self.scrollable_frame, text="📝 No tasks found!",
                                        font=("Segoe UI", 12), bg=COLORS["panel2"], fg=COLORS["muted"])
            self.empty_label.pack(pady=50)
        else:
            for task in filtered:
                self._create_task_widget(task)

    def _create_task_widget(self, task):
        # Task frame
        task_frame = tk.Frame(self.scrollable_frame, bg=COLORS["panel"],
                              highlightbackground=COLORS["panel2"], highlightthickness=1)
        task_frame.pack(fill="x", padx=5, pady=5)

        # Priority indicator
        priority_color = COLORS[task["priority"].lower()]
        priority_bar = tk.Frame(task_frame, bg=priority_color, width=5)
        priority_bar.pack(side="left", fill="y")

        # Content frame
        content = tk.Frame(task_frame, bg=COLORS["panel"])
        content.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Checkbox and name
        check_frame = tk.Frame(content, bg=COLORS["panel"])
        check_frame.pack(fill="x")

        var = tk.BooleanVar(value=task["completed"])
        checkbox = tk.Checkbutton(check_frame, variable=var,
                                  command=lambda t=task["id"]: self._toggle_complete(t),
                                  bg=COLORS["panel"], activebackground=COLORS["panel"],
                                  selectcolor=COLORS["panel2"])
        checkbox.pack(side="left")

        name_label = tk.Label(check_frame, text=task["name"],
                              font=("Segoe UI", 12, "bold" if not task["completed"] else "normal"),
                              bg=COLORS["panel"], fg=COLORS["fg"] if not task["completed"] else COLORS["muted"],
                              anchor="w")
        if task["completed"]:
            name_label.config(text=f"✓ {task['name']}")
        name_label.pack(side="left", padx=(5, 0))

        # Metadata
        meta_frame = tk.Frame(content, bg=COLORS["panel"])
        meta_frame.pack(fill="x", pady=(5, 0))

        # Priority badge
        priority_badge = tk.Label(meta_frame, text=f"● {task['priority']}",
                                  font=("Segoe UI", 9), bg=priority_color, fg="white",
                                  padx=5, pady=2)
        priority_badge.pack(side="left", padx=(0, 5))

        # Category
        category_label = tk.Label(meta_frame, text=f"📁 {task['category']}",
                                  font=("Segoe UI", 9), bg=COLORS["panel"], fg=COLORS["muted"])
        category_label.pack(side="left", padx=(0, 10))

        # Due date
        if task["due_date"]:
            due_date = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
            days_left = (due_date - date.today()).days
            if days_left < 0:
                date_text = f"⚠️ Overdue ({abs(days_left)} days)"
                date_color = COLORS["danger"]
            elif days_left == 0:
                date_text = "⚠️ Due today!"
                date_color = COLORS["warning"]
            elif days_left <= 3:
                date_text = f"📅 Due in {days_left} day(s)"
                date_color = COLORS["warning"]
            else:
                date_text = f"📅 {task['due_date']}"
                date_color = COLORS["muted"]

            date_label = tk.Label(meta_frame, text=date_text,
                                  font=("Segoe UI", 9), bg=COLORS["panel"], fg=date_color)
            date_label.pack(side="left")

        # Action buttons
        btn_frame = tk.Frame(task_frame, bg=COLORS["panel"])
        btn_frame.pack(side="right", padx=10)

        edit_btn = tk.Button(btn_frame, text="✏️", font=("Segoe UI", 10),
                             bg=COLORS["accent"], fg="white", relief="flat",
                             padx=8, pady=3, cursor="hand2",
                             command=lambda t=task["id"]: self._edit_task(t))
        edit_btn.pack(side="left", padx=2)

        delete_btn = tk.Button(btn_frame, text="🗑️", font=("Segoe UI", 10),
                               bg=COLORS["danger"], fg="white", relief="flat",
                               padx=8, pady=3, cursor="hand2",
                               command=lambda t=task["id"]: self._delete_task(t))
        delete_btn.pack(side="left", padx=2)

    def _update_stats(self):
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t["completed"])
        pending = total - completed
        rate = (completed / total * 100) if total > 0 else 0

        self.stats_labels["total"].config(text=str(total))
        self.stats_labels["completed"].config(text=str(completed))
        self.stats_labels["pending"].config(text=str(pending))
        self.stats_labels["rate"].config(text=f"{rate:.1f}%")

        # Update progress bar
        self.progress_canvas.delete("all")
        w = self.progress_canvas.winfo_width() or 350
        h = 20
        fill_ratio = completed / total if total > 0 else 0
        color = COLORS["success"] if rate >= 70 else COLORS["warning"] if rate >= 40 else COLORS["danger"]
        self.progress_canvas.create_rectangle(0, 0, w * fill_ratio, h, fill=color, outline="")

    # ---------------- DATA PERSISTENCE ----------------
    def _save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("⚠️ Error", f"Failed to save data:\n{e}")

    def _load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.tasks = json.load(f)
            except Exception as e:
                messagebox.showerror("⚠️ Error", f"Failed to load data:\n{e}")
                self.tasks = []

    # ---------------- UTILITIES ----------------
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap(default="")
    except Exception:
        pass
    app = TodoManager(root)
    root.mainloop()