"""
============================================================
  PERSONAL EXPENSE TRACKER - Professional Edition
  Author: AI Assistant
  Language: Python 3 (Tkinter - built-in)
  Run: python expense_tracker.py
============================================================
"""

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os
import csv
from datetime import datetime, date

# ==================== CONFIGURATION ====================
COLORS = {
    "bg":       "#0f172a",
    "panel":    "#1e293b",
    "panel2":   "#334155",
    "panel3":   "#475569",
    "fg":       "#e2e8f0",
    "accent":   "#38bdf8",
    "accent2":  "#818cf8",
    "success":  "#22c55e",
    "danger":   "#ef4444",
    "warning":  "#f59e0b",
    "muted":    "#94a3b8",
    "income":   "#22c55e",
    "expense":  "#ef4444",
    "balance":  "#38bdf8",
}

CATEGORIES = {
    "Food":          {"icon": "🍔", "color": "#f97316"},
    "Transport":     {"icon": "🚗", "color": "#3b82f6"},
    "Shopping":      {"icon": "🛍️", "color": "#ec4899"},
    "Bills":         {"icon": "💡", "color": "#f59e0b"},
    "Entertainment": {"icon": "🎬", "color": "#a855f7"},
    "Health":        {"icon": "💊", "color": "#14b8a6"},
    "Salary":        {"icon": "💼", "color": "#22c55e"},
    "Other":         {"icon": "📦", "color": "#64748b"},
}

DATA_FILE = "expenses_data.json"


# ==================== MAIN APPLICATION ====================
class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Personal Expense Tracker")
        self.root.geometry("1200x780")
        self.root.minsize(1100, 720)
        self.root.configure(bg=COLORS["bg"])

        # Center window
        self.root.update_idletasks()
        w, h = 1200, 780
        sx = self.root.winfo_screenwidth()
        sy = self.root.winfo_screenheight()
        x = (sx // 2) - (w // 2)
        y = (sy // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # State
        self.transactions = []
        self.current_filter = "All"
        self.search_query = ""
        self.editing_id = None
        self.sort_by = "date"

        self._build_ui()
        self._load_data()
        self._refresh_list()
        self._update_stats()
        self._draw_chart()

        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self._focus_desc())
        self.root.bind("<Control-f>", lambda e: self._focus_search())
        self.root.bind("<Escape>", lambda e: self._cancel_edit())
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ==================== UI BUILD ====================
    def _build_ui(self):
        # ---------- TITLE ----------
        tk.Label(
            self.root, text="💰 PERSONAL EXPENSE TRACKER",
            font=("Segoe UI", 24, "bold"),
            bg=COLORS["bg"], fg=COLORS["accent"]
        ).pack(pady=(10, 2))

        tk.Label(
            self.root, text="Track every rupee, build your wealth! 💎",
            font=("Segoe UI", 11), bg=COLORS["bg"], fg=COLORS["muted"]
        ).pack()

        # ---------- BALANCE CARD (TOP) ----------
        balance_frame = tk.Frame(self.root, bg=COLORS["panel"],
                                 highlightbackground=COLORS["panel2"], highlightthickness=1)
        balance_frame.pack(fill="x", padx=15, pady=(8, 5))

        cards = tk.Frame(balance_frame, bg=COLORS["panel"])
        cards.pack(fill="x", padx=20, pady=15)

        self.balance_cards = {}
        card_data = [
            ("income",  "💵 INCOME",   COLORS["income"],  "+"),
            ("expense", "💸 EXPENSE",  COLORS["expense"], "-"),
            ("balance", "💳 BALANCE",  COLORS["balance"], "="),
        ]
        for i, (key, title, color, sign) in enumerate(card_data):
            card = tk.Frame(cards, bg=COLORS["panel2"],
                            highlightbackground=color, highlightthickness=2)
            card.grid(row=0, column=i, padx=10, sticky="nsew")
            cards.columnconfigure(i, weight=1)

            tk.Label(card, text=title, font=("Segoe UI", 11, "bold"),
                     bg=COLORS["panel2"], fg=color).pack(pady=(10, 2))
            lbl = tk.Label(card, text="₹0.00", font=("Segoe UI", 22, "bold"),
                           bg=COLORS["panel2"], fg=color)
            lbl.pack(pady=(0, 10))
            self.balance_cards[key] = lbl

        # ---------- MAIN CONTAINER ----------
        main = tk.Frame(self.root, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=15, pady=5)

        # ===== LEFT PANEL =====
        left = tk.Frame(main, bg=COLORS["panel"],
                        highlightbackground=COLORS["panel2"], highlightthickness=1)
        left.pack(side="left", fill="both", padx=(0, 10))
        left.pack_propagate(False)
        left.config(width=380)

        # Make left panel scrollable
        left_canvas = tk.Canvas(left, bg=COLORS["panel"], highlightthickness=0)
        left_scroll = tk.Scrollbar(left, orient="vertical", command=left_canvas.yview)
        left_inner = tk.Frame(left_canvas, bg=COLORS["panel"])
        left_inner.bind("<Configure>",
                        lambda e: left_canvas.configure(scrollregion=left_canvas.bbox("all")))
        left_canvas.create_window((0, 0), window=left_inner, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scroll.set)
        left_canvas.pack(side="left", fill="both", expand=True)
        left_scroll.pack(side="right", fill="y")

        def _left_mousewheel(event):
            left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        left_canvas.bind_all("<MouseWheel>", _left_mousewheel, add="+")

        # --- Type Selection ---
        tk.Label(left_inner, text="💱 Transaction Type", font=("Segoe UI", 12, "bold"),
                 bg=COLORS["panel"], fg=COLORS["accent"]).pack(anchor="w", padx=12, pady=(12, 5))

        type_frame = tk.Frame(left_inner, bg=COLORS["panel"])
        type_frame.pack(fill="x", padx=12, pady=(0, 8))

        self.type_var = tk.StringVar(value="Expense")
        self.income_btn = tk.Radiobutton(
            type_frame, text="💵 Income", variable=self.type_var, value="Income",
            font=("Segoe UI", 11, "bold"), bg=COLORS["panel2"], fg=COLORS["income"],
            selectcolor=COLORS["panel2"], activebackground=COLORS["panel2"],
            activeforeground=COLORS["income"], indicatoron=0,
            width=10, pady=6, cursor="hand2", relief="flat",
            command=self._on_type_change
        )
        self.income_btn.pack(side="left", padx=(0, 5), fill="x", expand=True)

        self.expense_btn = tk.Radiobutton(
            type_frame, text="💸 Expense", variable=self.type_var, value="Expense",
            font=("Segoe UI", 11, "bold"), bg=COLORS["danger"], fg="white",
            selectcolor=COLORS["danger"], activebackground=COLORS["danger"],
            activeforeground="white", indicatoron=0,
            width=10, pady=6, cursor="hand2", relief="flat",
            command=self._on_type_change
        )
        self.expense_btn.pack(side="left", padx=(5, 0), fill="x", expand=True)

        # --- Amount ---
        tk.Label(left_inner, text="Amount (₹) *:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(anchor="w", padx=12)
        self.amount_entry = tk.Entry(left_inner, font=("Segoe UI", 14, "bold"),
                                     bg=COLORS["panel2"], fg=COLORS["fg"],
                                     insertbackground=COLORS["fg"], relief="flat", bd=5)
        self.amount_entry.pack(fill="x", padx=12, pady=(0, 6))

        # --- Description ---
        tk.Label(left_inner, text="Description *:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(anchor="w", padx=12)
        self.desc_entry = tk.Entry(left_inner, font=("Segoe UI", 11),
                                   bg=COLORS["panel2"], fg=COLORS["fg"],
                                   insertbackground=COLORS["fg"], relief="flat", bd=5)
        self.desc_entry.pack(fill="x", padx=12, pady=(0, 6))

        # --- Category ---
        tk.Label(left_inner, text="Category:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(anchor="w", padx=12)
        self.cat_var = tk.StringVar(value="Food")
        cat_menu = tk.OptionMenu(left_inner, self.cat_var, *CATEGORIES.keys())
        cat_menu.config(font=("Segoe UI", 10), bg=COLORS["panel2"], fg=COLORS["fg"],
                        activebackground=COLORS["accent"], relief="flat")
        cat_menu.pack(fill="x", padx=12, pady=(0, 6))

        # --- Date ---
        tk.Label(left_inner, text="Date (YYYY-MM-DD):", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(anchor="w", padx=12)
        self.date_entry = tk.Entry(left_inner, font=("Segoe UI", 11),
                                   bg=COLORS["panel2"], fg=COLORS["fg"],
                                   insertbackground=COLORS["fg"], relief="flat", bd=5)
        self.date_entry.pack(fill="x", padx=12, pady=(0, 6))
        self.date_entry.insert(0, date.today().isoformat())

        # --- Save/Cancel Buttons ---
        btn_frame = tk.Frame(left_inner, bg=COLORS["panel"])
        btn_frame.pack(fill="x", padx=12, pady=(8, 5))

        self.save_btn = tk.Button(
            btn_frame, text="➕ Add Transaction", font=("Segoe UI", 11, "bold"),
            bg=COLORS["success"], fg="white", activebackground="#16a34a",
            relief="flat", pady=8, cursor="hand2", command=self._save_transaction
        )
        self.save_btn.pack(fill="x", pady=(0, 4))

        self.cancel_btn = tk.Button(
            btn_frame, text="❌ Cancel Edit", font=("Segoe UI", 11, "bold"),
            bg=COLORS["danger"], fg="white", activebackground="#b91c1c",
            relief="flat", pady=6, cursor="hand2", command=self._cancel_edit
        )

        # --- Separator ---
        tk.Frame(left_inner, bg=COLORS["panel2"], height=2).pack(fill="x", padx=12, pady=8)

        # --- Search & Filter ---
        tk.Label(left_inner, text="🔍 Search & Filter", font=("Segoe UI", 12, "bold"),
                 bg=COLORS["panel"], fg=COLORS["accent"]).pack(anchor="w", padx=12, pady=(0, 5))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            left_inner, textvariable=self.search_var, font=("Segoe UI", 11),
            bg=COLORS["panel2"], fg=COLORS["fg"], insertbackground=COLORS["fg"],
            relief="flat", bd=5
        )
        self.search_entry.pack(fill="x", padx=12, pady=(0, 6))
        self.search_var.trace_add("write", lambda *_: self._on_search())

        # Filter buttons
        filter_frame = tk.Frame(left_inner, bg=COLORS["panel"])
        filter_frame.pack(fill="x", padx=12, pady=(0, 6))

        self.filter_btns = {}
        filters = ["All", "Income", "Expense"]
        for f in filters:
            btn = tk.Button(
                filter_frame, text=f, font=("Segoe UI", 10, "bold"),
                bg=COLORS["panel2"], fg=COLORS["fg"],
                activebackground=COLORS["accent"], relief="flat",
                padx=8, pady=4, cursor="hand2",
                command=lambda f=f: self._set_filter(f)
            )
            btn.pack(side="left", padx=2, fill="x", expand=True)
            self.filter_btns[f] = btn
        self._highlight_filter()

        # Month filter
        month_frame = tk.Frame(left_inner, bg=COLORS["panel"])
        month_frame.pack(fill="x", padx=12, pady=(0, 6))
        tk.Label(month_frame, text="Month:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(side="left")
        self.month_var = tk.StringVar(value="All")
        months = ["All"] + [datetime.now().replace(month=m, day=1).strftime("%B %Y")
                            for m in range(1, 13)]
        month_menu = tk.OptionMenu(month_frame, self.month_var, *months,
                                   command=lambda _: self._refresh_list())
        month_menu.config(font=("Segoe UI", 10), bg=COLORS["panel2"], fg=COLORS["fg"],
                          activebackground=COLORS["accent"], relief="flat")
        month_menu.pack(side="left", padx=5, fill="x", expand=True)

        # Sort
        sort_frame = tk.Frame(left_inner, bg=COLORS["panel"])
        sort_frame.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(sort_frame, text="Sort:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(side="left")
        self.sort_var = tk.StringVar(value="Date (Newest)")
        sort_menu = tk.OptionMenu(sort_frame, self.sort_var,
                                  "Date (Newest)", "Date (Oldest)", "Amount (High-Low)",
                                  "Amount (Low-High)",
                                  command=lambda _: self._refresh_list())
        sort_menu.config(font=("Segoe UI", 10), bg=COLORS["panel2"], fg=COLORS["fg"],
                         activebackground=COLORS["accent"], relief="flat")
        sort_menu.pack(side="left", padx=5, fill="x", expand=True)

        # --- Separator ---
        tk.Frame(left_inner, bg=COLORS["panel2"], height=2).pack(fill="x", padx=12, pady=5)

        # --- Chart ---
        tk.Label(left_inner, text="📊 Category Breakdown (Expenses)",
                 font=("Segoe UI", 12, "bold"),
                 bg=COLORS["panel"], fg=COLORS["accent"]).pack(anchor="w", padx=12, pady=(5, 5))

        self.chart_canvas = tk.Canvas(left_inner, height=180, bg=COLORS["panel2"],
                                      highlightthickness=0)
        self.chart_canvas.pack(fill="x", padx=12, pady=(0, 8))

        # --- Export ---
        tk.Button(
            left_inner, text="📤 Export to CSV", font=("Segoe UI", 10, "bold"),
            bg=COLORS["accent2"], fg="white", activebackground="#6366f1",
            relief="flat", pady=6, cursor="hand2", command=self._export_csv
        ).pack(fill="x", padx=12, pady=(0, 12))

        # ===== RIGHT PANEL =====
        right = tk.Frame(main, bg=COLORS["panel"],
                         highlightbackground=COLORS["panel2"], highlightthickness=1)
        right.pack(side="right", fill="both", expand=True)

        # Header
        header = tk.Frame(right, bg=COLORS["panel"])
        header.pack(fill="x", padx=15, pady=(10, 5))

        self.list_title = tk.Label(header, text="📋 All Transactions (0)",
                                   font=("Segoe UI", 14, "bold"),
                                   bg=COLORS["panel"], fg=COLORS["accent"])
        self.list_title.pack(side="left")

        # Transaction list (scrollable)
        list_container = tk.Frame(right, bg=COLORS["panel2"])
        list_container.pack(fill="both", expand=True, padx=15, pady=(0, 12))

        self.canvas = tk.Canvas(list_container, bg=COLORS["panel2"], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=COLORS["panel2"])

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        # Empty state
        self.empty_label = tk.Label(
            self.scroll_frame,
            text="📝 No transactions yet!\n\nAdd your first income or expense.",
            font=("Segoe UI", 13), bg=COLORS["panel2"], fg=COLORS["muted"],
            justify="center"
        )
        self.empty_label.pack(pady=80)

        # ---------- STATUS BAR ----------
        self.status = tk.Label(
            self.root,
            text="Ready!  Ctrl+N = New  |  Ctrl+F = Search  |  Esc = Cancel",
            font=("Segoe UI", 10), bg=COLORS["bg"], fg=COLORS["muted"],
            anchor="w", padx=20
        )
        self.status.pack(side="bottom", fill="x", pady=4)

    # ==================== DATA PERSISTENCE ====================
    def _save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.transactions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save data:\n{e}")

    def _load_data(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self.transactions = data
        except Exception:
            self.transactions = []

    # ==================== VALIDATION ====================
    def _validate(self, amount_str, desc, date_str):
        if not amount_str:
            messagebox.showwarning("⚠️ Validation", "Amount cannot be empty!")
            return False
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showwarning("⚠️ Validation", "Amount must be greater than 0!")
                return False
        except ValueError:
            messagebox.showwarning("⚠️ Validation", "Invalid amount! Use numbers only.")
            return False

        if not desc or len(desc.strip()) < 2:
            messagebox.showwarning("⚠️ Validation", "Description must be at least 2 characters!")
            return False

        if not date_str:
            messagebox.showwarning("⚠️ Validation", "Date cannot be empty!")
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("⚠️ Validation", "Invalid date format! Use YYYY-MM-DD")
            return False

        return True

    # ==================== CRUD OPERATIONS ====================
    def _save_transaction(self):
        amount_str = self.amount_entry.get().strip()
        desc = self.desc_entry.get().strip()
        category = self.cat_var.get()
        date_str = self.date_entry.get().strip()
        ttype = self.type_var.get()

        if not self._validate(amount_str, desc, date_str):
            return

        amount = float(amount_str)

        if self.editing_id is not None:
            for t in self.transactions:
                if t["id"] == self.editing_id:
                    t["amount"] = amount
                    t["description"] = desc
                    t["category"] = category
                    t["date"] = date_str
                    t["type"] = ttype
                    break
            self._cancel_edit()
            self._set_status(f"Transaction updated: {desc}")
        else:
            new_id = max((t["id"] for t in self.transactions), default=0) + 1
            transaction = {
                "id": new_id,
                "type": ttype,
                "amount": amount,
                "description": desc,
                "category": category,
                "date": date_str,
                "created_at": datetime.now().isoformat()
            }
            self.transactions.append(transaction)
            self._clear_form()
            self._set_status(f"Transaction added: {desc}")

        self._save_data()
        self._refresh_list()
        self._update_stats()
        self._draw_chart()

    def _delete_transaction(self, tid):
        t = next((x for x in self.transactions if x["id"] == tid), None)
        if not t:
            return
        if not messagebox.askyesno("🗑️ Delete",
                                   f"Delete this transaction?\n\n"
                                   f"{t['type']}: ₹{t['amount']:.2f}\n{t['description']}"):
            return
        self.transactions = [x for x in self.transactions if x["id"] != tid]
        if self.editing_id == tid:
            self._cancel_edit()
        self._save_data()
        self._refresh_list()
        self._update_stats()
        self._draw_chart()
        self._set_status(f"Transaction deleted: {t['description']}")

    def _start_edit(self, tid):
        t = next((x for x in self.transactions if x["id"] == tid), None)
        if not t:
            return
        self.editing_id = tid
        self._clear_form()
        self.type_var.set(t["type"])
        self._on_type_change()
        self.amount_entry.insert(0, str(t["amount"]))
        self.desc_entry.insert(0, t["description"])
        self.cat_var.set(t["category"])
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, t["date"])

        self.save_btn.config(text="✔ Update Transaction", bg=COLORS["accent"])
        self.cancel_btn.pack(fill="x", padx=12, pady=(0, 5))
        self.amount_entry.focus_set()
        self._set_status(f"Editing: {t['description']}")

    def _cancel_edit(self):
        self.editing_id = None
        self._clear_form()
        self.save_btn.config(text="➕ Add Transaction", bg=COLORS["success"])
        self.cancel_btn.pack_forget()

    def _clear_form(self):
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().isoformat())
        self.cat_var.set("Food")
        self.type_var.set("Expense")
        self._on_type_change()

    def _on_type_change(self):
        if self.type_var.get() == "Income":
            self.income_btn.config(bg=COLORS["income"], fg="white",
                                   activebackground=COLORS["income"])
            self.expense_btn.config(bg=COLORS["panel2"], fg=COLORS["danger"],
                                    activebackground=COLORS["panel2"])
        else:
            self.expense_btn.config(bg=COLORS["danger"], fg="white",
                                    activebackground=COLORS["danger"])
            self.income_btn.config(bg=COLORS["panel2"], fg=COLORS["income"],
                                   activebackground=COLORS["panel2"])

    # ==================== FILTER / SEARCH / SORT ====================
    def _set_filter(self, f):
        self.current_filter = f
        self._highlight_filter()
        self._refresh_list()
        self._set_status(f"Filter: {f}")

    def _highlight_filter(self):
        for f, btn in self.filter_btns.items():
            if f == self.current_filter:
                btn.config(bg=COLORS["accent"], fg="#0f172a")
            else:
                btn.config(bg=COLORS["panel2"], fg=COLORS["fg"])

    def _on_search(self):
        self.search_query = self.search_var.get().strip().lower()
        self._refresh_list()

    def _get_filtered_transactions(self):
        result = self.transactions[:]

        # Type filter
        if self.current_filter == "Income":
            result = [t for t in result if t["type"] == "Income"]
        elif self.current_filter == "Expense":
            result = [t for t in result if t["type"] == "Expense"]

        # Month filter
        month = self.month_var.get()
        if month != "All":
            try:
                month_date = datetime.strptime(month, "%B %Y")
                result = [t for t in result
                          if datetime.strptime(t["date"], "%Y-%m-%d").month == month_date.month
                          and datetime.strptime(t["date"], "%Y-%m-%d").year == month_date.year]
            except ValueError:
                pass

        # Search
        if self.search_query:
            q = self.search_query
            result = [t for t in result
                      if q in t["description"].lower()
                      or q in t["category"].lower()]

        # Sort
        sort = self.sort_var.get()
        if sort == "Date (Newest)":
            result.sort(key=lambda t: t["date"], reverse=True)
        elif sort == "Date (Oldest)":
            result.sort(key=lambda t: t["date"])
        elif sort == "Amount (High-Low)":
            result.sort(key=lambda t: t["amount"], reverse=True)
        elif sort == "Amount (Low-High)":
            result.sort(key=lambda t: t["amount"])

        return result

    # ==================== DISPLAY ====================
    def _refresh_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        filtered = self._get_filtered_transactions()
        self.list_title.config(text=f"📋 {self.current_filter} Transactions ({len(filtered)})")

        if not filtered:
            self.empty_label = tk.Label(
                self.scroll_frame,
                text="📝 No transactions found!\n\nTry a different filter or add new.",
                font=("Segoe UI", 13), bg=COLORS["panel2"], fg=COLORS["muted"],
                justify="center"
            )
            self.empty_label.pack(pady=80)
            return

        for t in filtered:
            self._create_transaction_card(t)

    def _create_transaction_card(self, t):
        is_income = t["type"] == "Income"
        accent = COLORS["income"] if is_income else COLORS["expense"]
        icon = "💵" if is_income else "💸"
        sign = "+" if is_income else "-"
        cat_info = CATEGORIES.get(t["category"], CATEGORIES["Other"])

        # Card
        card = tk.Frame(self.scroll_frame, bg=COLORS["panel"],
                        highlightbackground=COLORS["panel2"], highlightthickness=1)
        card.pack(fill="x", padx=5, pady=4)

        # Color bar
        tk.Frame(card, bg=accent, width=5).pack(side="left", fill="y")

        # Category icon
        icon_label = tk.Label(card, text=cat_info["icon"],
                              font=("Segoe UI", 22), bg=COLORS["panel"])
        icon_label.pack(side="left", padx=(10, 8), pady=10)

        # Info
        info = tk.Frame(card, bg=COLORS["panel"])
        info.pack(side="left", fill="both", expand=True, pady=8)

        # Top row: description + badge
        top_row = tk.Frame(info, bg=COLORS["panel"])
        top_row.pack(fill="x")

        tk.Label(top_row, text=t["description"],
                 font=("Segoe UI", 12, "bold"),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(side="left")

        tk.Label(top_row, text=f"  {t['category']}  ",
                 font=("Segoe UI", 9, "bold"),
                 bg=cat_info["color"], fg="white", padx=4, pady=1).pack(side="left", padx=8)

        # Bottom row: date + type
        bottom_row = tk.Frame(info, bg=COLORS["panel"])
        bottom_row.pack(fill="x", pady=(3, 0))

        try:
            dt = datetime.strptime(t["date"], "%Y-%m-%d")
            date_display = dt.strftime("%d %b %Y")
        except ValueError:
            date_display = t["date"]

        tk.Label(bottom_row, text=f"📅 {date_display}",
                 font=("Segoe UI", 10), bg=COLORS["panel"], fg=COLORS["muted"]).pack(side="left")

        # Amount
        tk.Label(card, text=f"{sign}₹{t['amount']:,.2f}",
                 font=("Segoe UI", 16, "bold"),
                 bg=COLORS["panel"], fg=accent).pack(side="right", padx=(10, 5), pady=10)

        # Actions
        actions = tk.Frame(card, bg=COLORS["panel"])
        actions.pack(side="right", padx=5, pady=10)

        tk.Button(actions, text="✏️", font=("Segoe UI", 11),
                  bg=COLORS["accent"], fg="white", activebackground="#0ea5e9",
                  relief="flat", padx=6, pady=3, cursor="hand2",
                  command=lambda tid=t["id"]: self._start_edit(tid)
                  ).pack(side="left", padx=2)

        tk.Button(actions, text="🗑️", font=("Segoe UI", 11),
                  bg=COLORS["danger"], fg="white", activebackground="#b91c1c",
                  relief="flat", padx=6, pady=3, cursor="hand2",
                  command=lambda tid=t["id"]: self._delete_transaction(tid)
                  ).pack(side="left", padx=2)

    # ==================== STATS & CHART ====================
    def _update_stats(self):
        income = sum(t["amount"] for t in self.transactions if t["type"] == "Income")
        expense = sum(t["amount"] for t in self.transactions if t["type"] == "Expense")
        balance = income - expense

        self.balance_cards["income"].config(text=f"₹{income:,.2f}")
        self.balance_cards["expense"].config(text=f"₹{expense:,.2f}")
        self.balance_cards["balance"].config(text=f"₹{balance:,.2f}")

    def _draw_chart(self):
        self.chart_canvas.delete("all")
        w = self.chart_canvas.winfo_width() or 340
        h = 180

        # Calculate expense by category
        cat_totals = {cat: 0.0 for cat in CATEGORIES}
        for t in self.transactions:
            if t["type"] == "Expense" and t["category"] in cat_totals:
                cat_totals[t["category"]] += t["amount"]

        # Filter non-zero
        data = [(cat, val) for cat, val in cat_totals.items() if val > 0]
        if not data:
            self.chart_canvas.create_text(
                w // 2, h // 2, text="No expense data yet",
                font=("Segoe UI", 11), fill=COLORS["muted"]
            )
            return

        max_val = max(v for _, v in data)
        n = len(data)
        padding = 15
        bar_area_w = w - 2 * padding
        bar_area_h = h - 40
        bar_width = min(40, (bar_area_w // n) - 8)
        spacing = (bar_area_w - n * bar_width) / (n + 1)

        # Draw bars
        for i, (cat, val) in enumerate(data):
            x = padding + spacing * (i + 1) + bar_width * i
            bar_h = (val / max_val) * bar_area_h if max_val > 0 else 0
            y_top = 10 + (bar_area_h - bar_h)
            y_bottom = 10 + bar_area_h

            color = CATEGORIES[cat]["color"]
            self.chart_canvas.create_rectangle(
                x, y_top, x + bar_width, y_bottom,
                fill=color, outline=""
            )

            # Category icon below
            self.chart_canvas.create_text(
                x + bar_width / 2, h - 10,
                text=CATEGORIES[cat]["icon"],
                font=("Segoe UI", 10)
            )

            # Value on top
            self.chart_canvas.create_text(
                x + bar_width / 2, y_top - 8,
                text=f"₹{val:.0f}",
                font=("Segoe UI", 8, "bold"),
                fill=COLORS["fg"]
            )

    # ==================== EXPORT ====================
    def _export_csv(self):
        if not self.transactions:
            messagebox.showinfo("ℹ️ Info", "No transactions to export!")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export Transactions"
        )
        if not filepath:
            return
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Type", "Amount", "Description",
                                 "Category", "Date", "Created At"])
                for t in self.transactions:
                    writer.writerow([
                        t["id"], t["type"], t["amount"], t["description"],
                        t["category"], t["date"], t.get("created_at", "")
                    ])
            self._set_status(f"Exported {len(self.transactions)} transactions to {filepath}")
            messagebox.showinfo("✅ Success", f"Exported successfully!\n\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export:\n{e}")

    # ==================== UTILITIES ====================
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _focus_desc(self):
        self.desc_entry.focus_set()

    def _focus_search(self):
        self.search_entry.focus_set()

    def _set_status(self, msg):
        self.status.config(text=msg)

    def _on_close(self):
        self._save_data()
        self.root.destroy()


# ==================== ENTRY POINT ====================
if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap(default="")
    except Exception:
        pass
    app = ExpenseTracker(root)
    root.mainloop()