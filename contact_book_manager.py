"""
============================================================
  CONTACT BOOK MANAGER - Professional Edition
  Author: AI Assistant
  Language: Python 3 (Tkinter - built-in)
  Run: python contact_book.py
============================================================
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import re
from datetime import datetime

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
    "family":   "#f472b6",
    "friends":  "#34d399",
    "work":     "#60a5fa",
    "other":    "#a78bfa",
}

CATEGORIES = ["Family", "Friends", "Work", "Other"]
CAT_COLORS = {
    "Family":  COLORS["family"],
    "Friends": COLORS["friends"],
    "Work":    COLORS["work"],
    "Other":   COLORS["other"],
}
DATA_FILE = "contacts_data.json"

PHONE_RE = re.compile(r"^[\d\s\+\-\(\)]{7,20}$")
EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


# ==================== MAIN APPLICATION ====================
class ContactBook:
    def __init__(self, root):
        self.root = root
        self.root.title("📇 Contact Book Manager")
        self.root.geometry("1150x750")
        self.root.minsize(1050, 700)
        self.root.configure(bg=COLORS["bg"])

        # Center window
        self.root.update_idletasks()
        w, h = 1150, 750
        sx = self.root.winfo_screenwidth()
        sy = self.root.winfo_screenheight()
        x = (sx // 2) - (w // 2)
        y = (sy // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # State
        self.contacts = []
        self.current_filter = "All"
        self.search_query = ""
        self.editing_id = None
        self.sort_by = "name"

        self._build_ui()
        self._load_data()
        self._refresh_list()
        self._update_stats()

        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self._focus_name())
        self.root.bind("<Control-f>", lambda e: self._focus_search())
        self.root.bind("<Escape>", lambda e: self._cancel_edit())
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ==================== UI BUILD ====================
    def _build_ui(self):
        # ---------- TITLE ----------
        tk.Label(
            self.root, text="📇 CONTACT BOOK MANAGER",
            font=("Segoe UI", 24, "bold"),
            bg=COLORS["bg"], fg=COLORS["accent"]
        ).pack(pady=(12, 2))

        tk.Label(
            self.root, text="Manage your contacts like a pro! 🚀",
            font=("Segoe UI", 11), bg=COLORS["bg"], fg=COLORS["muted"]
        ).pack()

        # ---------- MAIN CONTAINER ----------
        main = tk.Frame(self.root, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=15, pady=10)

        # ===== LEFT PANEL =====
        left = tk.Frame(main, bg=COLORS["panel"],
                        highlightbackground=COLORS["panel2"], highlightthickness=1)
        left.pack(side="left", fill="both", padx=(0, 10))
        left.pack_propagate(False)
        left.config(width=370)

        # Make left panel scrollable too (for smaller screens)
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

        # --- Search ---
        tk.Label(left_inner, text="🔍 Search", font=("Segoe UI", 12, "bold"),
                 bg=COLORS["panel"], fg=COLORS["accent"]).pack(anchor="w", padx=12, pady=(12, 5))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            left_inner, textvariable=self.search_var, font=("Segoe UI", 11),
            bg=COLORS["panel2"], fg=COLORS["fg"], insertbackground=COLORS["fg"],
            relief="flat", bd=5
        )
        self.search_entry.pack(fill="x", padx=12, pady=(0, 8))
        self.search_var.trace_add("write", lambda *_: self._on_search())

        # --- Filters ---
        tk.Label(left_inner, text="📁 Filter", font=("Segoe UI", 12, "bold"),
                 bg=COLORS["panel"], fg=COLORS["accent"]).pack(anchor="w", padx=12, pady=(5, 5))

        filter_frame = tk.Frame(left_inner, bg=COLORS["panel"])
        filter_frame.pack(fill="x", padx=12, pady=(0, 5))

        self.filter_btns = {}
        filters = ["All", "⭐ Favs", "Family", "Friends", "Work", "Other"]
        for i, f in enumerate(filters):
            btn = tk.Button(
                filter_frame, text=f, font=("Segoe UI", 9, "bold"),
                bg=COLORS["panel2"], fg=COLORS["fg"],
                activebackground=COLORS["accent"], relief="flat",
                padx=6, pady=4, cursor="hand2",
                command=lambda f=f: self._set_filter(f)
            )
            btn.grid(row=i // 3, column=i % 3, padx=2, pady=2, sticky="ew")
            filter_frame.columnconfigure(i % 3, weight=1)
            self.filter_btns[f] = btn
        self._highlight_filter()

        # --- Sort ---
        sort_frame = tk.Frame(left_inner, bg=COLORS["panel"])
        sort_frame.pack(fill="x", padx=12, pady=(5, 8))
        tk.Label(sort_frame, text="Sort:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(side="left")
        self.sort_var = tk.StringVar(value="Name")
        sort_menu = tk.OptionMenu(sort_frame, self.sort_var,
                                  "Name", "Date Added", "Category",
                                  command=lambda _: self._refresh_list())
        sort_menu.config(font=("Segoe UI", 10), bg=COLORS["panel2"], fg=COLORS["fg"],
                         activebackground=COLORS["accent"], relief="flat")
        sort_menu.pack(side="left", padx=5, fill="x", expand=True)

        # --- Separator ---
        tk.Frame(left_inner, bg=COLORS["panel2"], height=2).pack(fill="x", padx=12, pady=5)

        # --- Add / Edit Form ---
        self.form_title = tk.Label(left_inner, text="➕ Add New Contact",
                                   font=("Segoe UI", 12, "bold"),
                                   bg=COLORS["panel"], fg=COLORS["accent"])
        self.form_title.pack(anchor="w", padx=12, pady=(8, 5))

        # Name
        tk.Label(left_inner, text="Name *:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(anchor="w", padx=12)
        self.name_entry = tk.Entry(left_inner, font=("Segoe UI", 11),
                                   bg=COLORS["panel2"], fg=COLORS["fg"],
                                   insertbackground=COLORS["fg"], relief="flat", bd=5)
        self.name_entry.pack(fill="x", padx=12, pady=(0, 6))

        # Phone
        tk.Label(left_inner, text="Phone *:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(anchor="w", padx=12)
        self.phone_entry = tk.Entry(left_inner, font=("Segoe UI", 11),
                                    bg=COLORS["panel2"], fg=COLORS["fg"],
                                    insertbackground=COLORS["fg"], relief="flat", bd=5)
        self.phone_entry.pack(fill="x", padx=12, pady=(0, 6))

        # Email
        tk.Label(left_inner, text="Email:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(anchor="w", padx=12)
        self.email_entry = tk.Entry(left_inner, font=("Segoe UI", 11),
                                    bg=COLORS["panel2"], fg=COLORS["fg"],
                                    insertbackground=COLORS["fg"], relief="flat", bd=5)
        self.email_entry.pack(fill="x", padx=12, pady=(0, 6))

        # Category
        tk.Label(left_inner, text="Category:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(anchor="w", padx=12)
        self.cat_var = tk.StringVar(value="Friends")
        cat_menu = tk.OptionMenu(left_inner, self.cat_var, *CATEGORIES)
        cat_menu.config(font=("Segoe UI", 10), bg=COLORS["panel2"], fg=COLORS["fg"],
                        activebackground=COLORS["accent"], relief="flat")
        cat_menu.pack(fill="x", padx=12, pady=(0, 6))

        # Address
        tk.Label(left_inner, text="Address:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(anchor="w", padx=12)
        self.addr_entry = tk.Entry(left_inner, font=("Segoe UI", 11),
                                   bg=COLORS["panel2"], fg=COLORS["fg"],
                                   insertbackground=COLORS["fg"], relief="flat", bd=5)
        self.addr_entry.pack(fill="x", padx=12, pady=(0, 6))

        # Notes
        tk.Label(left_inner, text="Notes:", font=("Segoe UI", 10),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(anchor="w", padx=12)
        self.notes_text = tk.Text(left_inner, font=("Segoe UI", 10), height=3,
                                  bg=COLORS["panel2"], fg=COLORS["fg"],
                                  insertbackground=COLORS["fg"], relief="flat", bd=5)
        self.notes_text.pack(fill="x", padx=12, pady=(0, 8))

        # Buttons
        btn_frame = tk.Frame(left_inner, bg=COLORS["panel"])
        btn_frame.pack(fill="x", padx=12, pady=(0, 5))

        self.save_btn = tk.Button(
            btn_frame, text="➕ Add Contact", font=("Segoe UI", 11, "bold"),
            bg=COLORS["success"], fg="white", activebackground="#16a34a",
            relief="flat", pady=8, cursor="hand2", command=self._save_contact
        )
        self.save_btn.pack(fill="x", pady=(0, 4))

        self.cancel_btn = tk.Button(
            btn_frame, text="❌ Cancel Edit", font=("Segoe UI", 11, "bold"),
            bg=COLORS["danger"], fg="white", activebackground="#b91c1c",
            relief="flat", pady=6, cursor="hand2", command=self._cancel_edit
        )
        # Not packed initially

        # --- Separator ---
        tk.Frame(left_inner, bg=COLORS["panel2"], height=2).pack(fill="x", padx=12, pady=8)

        # --- Statistics ---
        tk.Label(left_inner, text="📊 Statistics", font=("Segoe UI", 12, "bold"),
                 bg=COLORS["panel"], fg=COLORS["accent"]).pack(anchor="w", padx=12, pady=(0, 5))

        stats_frame = tk.Frame(left_inner, bg=COLORS["panel2"])
        stats_frame.pack(fill="x", padx=12, pady=(0, 8))

        self.stat_labels = {}
        for key, label in [("total", "Total:"), ("favs", "Favorites:"),
                           ("family", "Family:"), ("friends", "Friends:"),
                           ("work", "Work:"), ("other", "Other:")]:
            row = tk.Frame(stats_frame, bg=COLORS["panel2"])
            row.pack(fill="x", padx=8, pady=2)
            tk.Label(row, text=label, font=("Segoe UI", 10),
                     bg=COLORS["panel2"], fg=COLORS["fg"]).pack(side="left")
            lbl = tk.Label(row, text="0", font=("Segoe UI", 10, "bold"),
                           bg=COLORS["panel2"], fg=COLORS["accent"])
            lbl.pack(side="right")
            self.stat_labels[key] = lbl

        # Export button
        tk.Button(
            left_inner, text="📤 Export Contacts", font=("Segoe UI", 10, "bold"),
            bg=COLORS["accent2"], fg="white", activebackground="#6366f1",
            relief="flat", pady=6, cursor="hand2", command=self._export_contacts
        ).pack(fill="x", padx=12, pady=(5, 12))

        # ===== RIGHT PANEL =====
        right = tk.Frame(main, bg=COLORS["panel"],
                         highlightbackground=COLORS["panel2"], highlightthickness=1)
        right.pack(side="right", fill="both", expand=True)

        # Header
        header = tk.Frame(right, bg=COLORS["panel"])
        header.pack(fill="x", padx=15, pady=(12, 8))

        self.list_title = tk.Label(header, text="📋 All Contacts (0)",
                                   font=("Segoe UI", 14, "bold"),
                                   bg=COLORS["panel"], fg=COLORS["accent"])
        self.list_title.pack(side="left")

        # Contact list (scrollable)
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

        # Resize inner frame to match canvas width
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Mouse wheel for right panel
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        # Empty state label
        self.empty_label = tk.Label(
            self.scroll_frame,
            text="📝 No contacts yet!\n\nClick 'Add Contact' to get started.",
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
                json.dump(self.contacts, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save data:\n{e}")

    def _load_data(self):
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self.contacts = data
        except Exception:
            self.contacts = []

    # ==================== VALIDATION ====================
    def _validate(self, name, phone, email):
        if not name or len(name.strip()) < 2:
            messagebox.showwarning("⚠️ Validation", "Name must be at least 2 characters!")
            return False
        if not phone or not PHONE_RE.match(phone.strip()):
            messagebox.showwarning("⚠️ Validation",
                                   "Invalid phone number!\nUse 7-20 digits, spaces, +, -, (, )")
            return False
        if email and not EMAIL_RE.match(email.strip()):
            messagebox.showwarning("⚠️ Validation", "Invalid email format!\nExample: user@email.com")
            return False
        return True

    # ==================== CRUD OPERATIONS ====================
    def _save_contact(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        category = self.cat_var.get()
        address = self.addr_entry.get().strip()
        notes = self.notes_text.get("1.0", tk.END).strip()

        if not self._validate(name, phone, email):
            return

        if self.editing_id is not None:
            # UPDATE
            for c in self.contacts:
                if c["id"] == self.editing_id:
                    c["name"] = name
                    c["phone"] = phone
                    c["email"] = email
                    c["category"] = category
                    c["address"] = address
                    c["notes"] = notes
                    break
            self._cancel_edit()
            self._set_status(f"Contact updated: {name}")
        else:
            # ADD
            new_id = max((c["id"] for c in self.contacts), default=0) + 1
            contact = {
                "id": new_id,
                "name": name,
                "phone": phone,
                "email": email,
                "category": category,
                "address": address,
                "notes": notes,
                "favorite": False,
                "created_at": datetime.now().isoformat()
            }
            self.contacts.append(contact)
            self._clear_form()
            self._set_status(f"Contact added: {name}")

        self._save_data()
        self._refresh_list()
        self._update_stats()

    def _delete_contact(self, contact_id):
        contact = next((c for c in self.contacts if c["id"] == contact_id), None)
        if not contact:
            return
        if not messagebox.askyesno("🗑️ Delete", f"Delete contact '{contact['name']}'?\nThis cannot be undone!"):
            return
        self.contacts = [c for c in self.contacts if c["id"] != contact_id]
        if self.editing_id == contact_id:
            self._cancel_edit()
        self._save_data()
        self._refresh_list()
        self._update_stats()
        self._set_status(f"Contact deleted: {contact['name']}")

    def _toggle_favorite(self, contact_id):
        for c in self.contacts:
            if c["id"] == contact_id:
                c["favorite"] = not c["favorite"]
                status = "added to" if c["favorite"] else "removed from"
                self._set_status(f"'{c['name']}' {status} favorites")
                break
        self._save_data()
        self._refresh_list()
        self._update_stats()

    def _start_edit(self, contact_id):
        contact = next((c for c in self.contacts if c["id"] == contact_id), None)
        if not contact:
            return
        self.editing_id = contact_id
        self._clear_form()
        self.name_entry.insert(0, contact["name"])
        self.phone_entry.insert(0, contact["phone"])
        self.email_entry.insert(0, contact.get("email", ""))
        self.cat_var.set(contact.get("category", "Other"))
        self.addr_entry.insert(0, contact.get("address", ""))
        self.notes_text.insert("1.0", contact.get("notes", ""))

        self.form_title.config(text="✏️ Edit Contact")
        self.save_btn.config(text="✔ Update Contact", bg=COLORS["accent"])
        self.cancel_btn.pack(fill="x", pady=(0, 4))
        self.name_entry.focus_set()
        self._set_status(f"Editing: {contact['name']}")

    def _cancel_edit(self):
        self.editing_id = None
        self._clear_form()
        self.form_title.config(text="➕ Add New Contact")
        self.save_btn.config(text="➕ Add Contact", bg=COLORS["success"])
        self.cancel_btn.pack_forget()
        self._set_status("Edit cancelled")

    def _clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.addr_entry.delete(0, tk.END)
        self.notes_text.delete("1.0", tk.END)
        self.cat_var.set("Friends")

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

    def _get_filtered_contacts(self):
        result = self.contacts[:]

        # Filter
        if self.current_filter == "⭐ Favs":
            result = [c for c in result if c.get("favorite")]
        elif self.current_filter in CATEGORIES:
            result = [c for c in result if c.get("category") == self.current_filter]

        # Search
        if self.search_query:
            q = self.search_query
            result = [
                c for c in result
                if q in c["name"].lower()
                or q in c["phone"].lower()
                or q in c.get("email", "").lower()
            ]

        # Sort
        sort = self.sort_var.get()
        if sort == "Name":
            result.sort(key=lambda c: c["name"].lower())
        elif sort == "Date Added":
            result.sort(key=lambda c: c.get("created_at", ""), reverse=True)
        elif sort == "Category":
            result.sort(key=lambda c: c.get("category", "Other"))

        return result

    # ==================== DISPLAY ====================
    def _refresh_list(self):
        # Clear all children
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        filtered = self._get_filtered_contacts()

        # Update header
        filter_name = self.current_filter
        self.list_title.config(text=f"📋 {filter_name} Contacts ({len(filtered)})")

        if not filtered:
            self.empty_label = tk.Label(
                self.scroll_frame,
                text="📝 No contacts found!\n\nTry a different filter or add a new contact.",
                font=("Segoe UI", 13), bg=COLORS["panel2"], fg=COLORS["muted"],
                justify="center"
            )
            self.empty_label.pack(pady=80)
            return

        for contact in filtered:
            self._create_contact_card(contact)

    def _create_contact_card(self, contact):
        # Card frame
        card = tk.Frame(self.scroll_frame, bg=COLORS["panel"],
                        highlightbackground=COLORS["panel2"], highlightthickness=1)
        card.pack(fill="x", padx=5, pady=4)

        # --- Avatar (initials in colored circle) ---
        avatar_size = 48
        avatar_canvas = tk.Canvas(card, width=avatar_size, height=avatar_size,
                                  bg=COLORS["panel"], highlightthickness=0)
        avatar_canvas.pack(side="left", padx=(10, 8), pady=10)

        cat_color = CAT_COLORS.get(contact.get("category", "Other"), COLORS["other"])
        avatar_canvas.create_oval(2, 2, avatar_size - 2, avatar_size - 2,
                                  fill=cat_color, outline="")

        initials = self._get_initials(contact["name"])
        avatar_canvas.create_text(avatar_size // 2, avatar_size // 2,
                                  text=initials, font=("Segoe UI", 14, "bold"),
                                  fill="white")

        # --- Info ---
        info = tk.Frame(card, bg=COLORS["panel"])
        info.pack(side="left", fill="both", expand=True, pady=8)

        # Name row
        name_row = tk.Frame(info, bg=COLORS["panel"])
        name_row.pack(fill="x")

        fav_star = "⭐ " if contact.get("favorite") else ""
        tk.Label(name_row, text=f"{fav_star}{contact['name']}",
                 font=("Segoe UI", 13, "bold"),
                 bg=COLORS["panel"], fg=COLORS["fg"]).pack(side="left")

        # Category badge
        badge_color = CAT_COLORS.get(contact.get("category", "Other"), COLORS["other"])
        tk.Label(name_row, text=f"  {contact.get('category', 'Other')}  ",
                 font=("Segoe UI", 9, "bold"),
                 bg=badge_color, fg="white", padx=4, pady=1).pack(side="left", padx=8)

        # Details row
        detail_row = tk.Frame(info, bg=COLORS["panel"])
        detail_row.pack(fill="x", pady=(3, 0))

        tk.Label(detail_row, text=f"📞 {contact['phone']}",
                 font=("Segoe UI", 10), bg=COLORS["panel"], fg=COLORS["muted"]).pack(side="left")

        if contact.get("email"):
            tk.Label(detail_row, text=f"   ✉️ {contact['email']}",
                     font=("Segoe UI", 10), bg=COLORS["panel"], fg=COLORS["muted"]).pack(side="left")

        if contact.get("address"):
            tk.Label(detail_row, text=f"   📍 {contact['address']}",
                     font=("Segoe UI", 10), bg=COLORS["panel"], fg=COLORS["muted"]).pack(side="left")

        # --- Action Buttons ---
        actions = tk.Frame(card, bg=COLORS["panel"])
        actions.pack(side="right", padx=10, pady=10)

        # Favorite toggle
        fav_text = "⭐" if contact.get("favorite") else "☆"
        fav_fg = COLORS["warning"] if contact.get("favorite") else COLORS["muted"]
        tk.Button(actions, text=fav_text, font=("Segoe UI", 14),
                  bg=COLORS["panel"], fg=fav_fg, activebackground=COLORS["panel2"],
                  relief="flat", cursor="hand2",
                  command=lambda cid=contact["id"]: self._toggle_favorite(cid)
                  ).pack(side="left", padx=2)

        # Edit
        tk.Button(actions, text="✏️", font=("Segoe UI", 11),
                  bg=COLORS["accent"], fg="white", activebackground="#0ea5e9",
                  relief="flat", padx=6, pady=3, cursor="hand2",
                  command=lambda cid=contact["id"]: self._start_edit(cid)
                  ).pack(side="left", padx=2)

        # Delete
        tk.Button(actions, text="🗑️", font=("Segoe UI", 11),
                  bg=COLORS["danger"], fg="white", activebackground="#b91c1c",
                  relief="flat", padx=6, pady=3, cursor="hand2",
                  command=lambda cid=contact["id"]: self._delete_contact(cid)
                  ).pack(side="left", padx=2)

    def _get_initials(self, name):
        parts = name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        elif len(parts) == 1 and parts[0]:
            return parts[0][:2].upper()
        return "?"

    def _update_stats(self):
        total = len(self.contacts)
        favs = sum(1 for c in self.contacts if c.get("favorite"))
        counts = {cat: 0 for cat in CATEGORIES}
        for c in self.contacts:
            cat = c.get("category", "Other")
            if cat in counts:
                counts[cat] += 1

        self.stat_labels["total"].config(text=str(total))
        self.stat_labels["favs"].config(text=str(favs))
        self.stat_labels["family"].config(text=str(counts["Family"]))
        self.stat_labels["friends"].config(text=str(counts["Friends"]))
        self.stat_labels["work"].config(text=str(counts["Work"]))
        self.stat_labels["other"].config(text=str(counts["Other"]))

    # ==================== EXPORT ====================
    def _export_contacts(self):
        if not self.contacts:
            messagebox.showinfo("ℹ️ Info", "No contacts to export!")
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Export Contacts"
        )
        if not filepath:
            return
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("       CONTACT BOOK EXPORT\n")
                f.write(f"       Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                f.write(f"       Total Contacts: {len(self.contacts)}\n")
                f.write("=" * 60 + "\n\n")

                for i, c in enumerate(self.contacts, 1):
                    fav = " [FAVORITE]" if c.get("favorite") else ""
                    f.write(f"--- Contact #{i}{fav} ---\n")
                    f.write(f"  Name:     {c['name']}\n")
                    f.write(f"  Phone:    {c['phone']}\n")
                    f.write(f"  Email:    {c.get('email', 'N/A')}\n")
                    f.write(f"  Category: {c.get('category', 'N/A')}\n")
                    f.write(f"  Address:  {c.get('address', 'N/A')}\n")
                    f.write(f"  Notes:    {c.get('notes', 'N/A')}\n")
                    f.write(f"  Added:    {c.get('created_at', 'N/A')}\n\n")

            self._set_status(f"Exported {len(self.contacts)} contacts to {filepath}")
            messagebox.showinfo("✅ Success", f"Contacts exported successfully!\n\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export:\n{e}")

    # ==================== UTILITIES ====================
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _focus_name(self):
        self.name_entry.focus_set()

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
    app = ContactBook(root)
    root.mainloop()