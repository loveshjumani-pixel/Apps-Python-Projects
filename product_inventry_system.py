import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import csv
from datetime import datetime

DATA_FILE = "inventory_data.json"

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📦 Product Inventory Management System")
        self.root.geometry("1150x700")
        self.root.minsize(1000, 600)
        self.root.configure(bg="#f0f4f8")

        # Color palette
        self.colors = {
            "primary": "#2c3e50",
            "secondary": "#3498db",
            "accent": "#e74c3c",
            "success": "#27ae60",
            "warning": "#f39c12",
            "bg": "#f0f4f8",
            "card": "#ffffff",
            "text": "#2c3e50",
            "muted": "#7f8c8d"
        }

        self.products = []
        self.selected_item = None

        self._setup_styles()
        self._build_ui()
        self.load_data()
        self.refresh_table()
        self.update_dashboard()

    # ---------- Styling ----------
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=self.colors["bg"])
        style.configure("Card.TFrame", background=self.colors["card"])
        style.configure("TLabel", background=self.colors["card"],
                        foreground=self.colors["text"],
                        font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"),
                        foreground=self.colors["primary"],
                        background=self.colors["card"])
        style.configure("Stat.TLabel", font=("Segoe UI", 22, "bold"),
                        foreground=self.colors["secondary"],
                        background=self.colors["card"])
        style.configure("StatCard.TFrame", background=self.colors["card"])

        style.configure("TButton", font=("Segoe UI", 10, "bold"),
                        padding=8, background=self.colors["secondary"])
        style.map("TButton",
                  background=[("active", self.colors["primary"])],
                  foreground=[("active", "white")])

        style.configure("Accent.TButton", background=self.colors["accent"])
        style.map("Accent.TButton",
                  background=[("active", "#c0392b")])

        style.configure("Success.TButton", background=self.colors["success"])
        style.map("Success.TButton",
                  background=[("active", "#1e8449")])

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
                  background=[("selected", self.colors["secondary"])],
                  foreground=[("selected", "white")])

        style.configure("TEntry", padding=6, font=("Segoe UI", 10))
        style.configure("TCombobox", padding=6, font=("Segoe UI", 10))

    # ---------- UI Building ----------
    def _build_ui(self):
        # Top header
        header = tk.Frame(self.root, bg=self.colors["primary"], height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="📦 PRODUCT INVENTORY SYSTEM",
                 font=("Segoe UI", 18, "bold"),
                 bg=self.colors["primary"], fg="white").pack(side="left", padx=20, pady=15)

        self.clock_label = tk.Label(header, text="",
                                    font=("Segoe UI", 11),
                                    bg=self.colors["primary"], fg="white")
        self.clock_label.pack(side="right", padx=20)
        self._update_clock()

        # Main container
        main = tk.Frame(self.root, bg=self.colors["bg"])
        main.pack(fill="both", expand=True, padx=15, pady=15)

        # Dashboard cards
        dash = tk.Frame(main, bg=self.colors["bg"])
        dash.pack(fill="x", pady=(0, 15))

        self.card_total = self._make_stat_card(dash, "Total Products", "0", "📦", 0)
        self.card_stock = self._make_stat_card(dash, "Total Stock", "0", "📊", 1)
        self.card_value = self._make_stat_card(dash, "Inventory Value", "₹0", "💰", 2)
        self.card_low = self._make_stat_card(dash, "Low Stock Items", "0", "⚠️", 3)

        # Middle: Form + Table
        mid = tk.Frame(main, bg=self.colors["bg"])
        mid.pack(fill="both", expand=True)
        mid.columnconfigure(1, weight=1)
        mid.rowconfigure(0, weight=1)

        # Left form
        form_frame = tk.Frame(mid, bg=self.colors["card"], width=280, relief="flat", bd=0)
        form_frame.grid(row=0, column=0, sticky="n", padx=(0, 15))
        form_frame.pack_propagate(False)

        tk.Label(form_frame, text="Product Details",
                 font=("Segoe UI", 13, "bold"),
                 bg=self.colors["card"], fg=self.colors["primary"]).pack(pady=15)

        fields_frame = tk.Frame(form_frame, bg=self.colors["card"])
        fields_frame.pack(fill="x", padx=15)

        self.fields = {}
        field_defs = [
            ("Product Name", "name"),
            ("Category", "category"),
            ("Price (₹)", "price"),
            ("Quantity", "quantity"),
            ("Supplier", "supplier"),
            ("SKU Code", "sku")
        ]

        for label_text, key in field_defs:
            tk.Label(fields_frame, text=label_text,
                     font=("Segoe UI", 9, "bold"),
                     bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w", pady=(8, 2))
            if key == "category":
                var = tk.StringVar()
                w = ttk.Combobox(fields_frame, textvariable=var,
                                 values=["Electronics", "Clothing", "Food",
                                         "Furniture", "Books", "Toys", "Other"],
                                 state="readonly")
                w.set("Select Category")
                w.pack(fill="x")
                self.fields[key] = var
            else:
                w = ttk.Entry(fields_frame)
                w.pack(fill="x")
                self.fields[key] = w

        # Buttons
        btn_frame = tk.Frame(form_frame, bg=self.colors["card"])
        btn_frame.pack(fill="x", padx=15, pady=20)

        ttk.Button(btn_frame, text="➕ Add Product",
                   command=self.add_product).pack(fill="x", pady=4)
        ttk.Button(btn_frame, text="✏️ Update Selected",
                   command=self.update_product).pack(fill="x", pady=4)
        ttk.Button(btn_frame, text="🗑️ Delete Selected",
                   style="Accent.TButton",
                   command=self.delete_product).pack(fill="x", pady=4)
        ttk.Button(btn_frame, text="🔄 Clear Form",
                   command=self.clear_form).pack(fill="x", pady=4)

        # Right: Table
        right = tk.Frame(mid, bg=self.colors["card"])
        right.grid(row=0, column=1, sticky="nsew")

        # Search bar
        search_frame = tk.Frame(right, bg=self.colors["card"])
        search_frame.pack(fill="x", padx=15, pady=(15, 10))

        tk.Label(search_frame, text="🔍", font=("Segoe UI", 14),
                 bg=self.colors["card"]).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self.refresh_table())
        ttk.Entry(search_frame, textvariable=self.search_var,
                  width=30).pack(side="left", padx=8)

        tk.Label(search_frame, text="Category:",
                 bg=self.colors["card"],
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(20, 5))
        self.filter_var = tk.StringVar(value="All")
        self.filter_var.trace_add("write", lambda *a: self.refresh_table())
        ttk.Combobox(search_frame, textvariable=self.filter_var,
                     values=["All", "Electronics", "Clothing", "Food",
                             "Furniture", "Books", "Toys", "Other"],
                     state="readonly", width=15).pack(side="left")

        ttk.Button(search_frame, text="📤 Export CSV",
                   style="Success.TButton",
                   command=self.export_csv).pack(side="right")

        # Table
        table_frame = tk.Frame(right, bg=self.colors["card"])
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        cols = ("id", "name", "category", "price", "quantity", "supplier", "sku", "added")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        headings = {
            "id": ("ID", 50), "name": ("Product Name", 170),
            "category": ("Category", 110), "price": ("Price (₹)", 90),
            "quantity": ("Qty", 70), "supplier": ("Supplier", 140),
            "sku": ("SKU", 90), "added": ("Added On", 120)
        }
        for c, (text, width) in headings.items():
            self.tree.heading(c, text=text,
                              command=lambda col=c: self._sort_column(col))
            self.tree.column(c, width=width, anchor="w")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Tag for low stock
        self.tree.tag_configure("lowstock", background="#ffe5e5", foreground="#c0392b")

        # Status bar
        self.status = tk.Label(self.root, text="Ready",
                               bg=self.colors["primary"], fg="white",
                               font=("Segoe UI", 9), anchor="w")
        self.status.pack(side="bottom", fill="x")

    def _make_stat_card(self, parent, title, value, icon, idx):
        card = tk.Frame(parent, bg=self.colors["card"],
                        highlightbackground="#dfe6e9",
                        highlightthickness=1)
        card.pack(side="left", fill="both", expand=True, padx=6)

        tk.Label(card, text=f"{icon}  {title}",
                 font=("Segoe UI", 10, "bold"),
                 bg=self.colors["card"],
                 fg=self.colors["muted"]).pack(pady=(15, 5))
        lbl = tk.Label(card, text=value,
                       font=("Segoe UI", 22, "bold"),
                       bg=self.colors["card"],
                       fg=self.colors["secondary"])
        lbl.pack(pady=(0, 15))
        return lbl

    # ---------- Clock ----------
    def _update_clock(self):
        now = datetime.now().strftime("%A, %d %b %Y  |  %I:%M:%S %p")
        self.clock_label.config(text=now)
        self.root.after(1000, self._update_clock)

    # ---------- Data Handling ----------
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.products = json.load(f)
                self.status.config(text=f"✅ Loaded {len(self.products)} products from {DATA_FILE}")
            except (json.JSONDecodeError, IOError):
                self.products = []
                messagebox.showwarning("Data Error",
                                       "Could not read data file. Starting fresh.")
        else:
            self.products = []

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.products, f, indent=2, ensure_ascii=False)
        except IOError as e:
            messagebox.showerror("Save Error", f"Could not save data:\n{e}")

    # ---------- Table ----------
    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        search = self.search_var.get().lower().strip()
        cat = self.filter_var.get()

        for p in self.products:
            if cat != "All" and p.get("category") != cat:
                continue
            if search:
                haystack = " ".join(str(v).lower() for v in p.values())
                if search not in haystack:
                    continue

            qty = p.get("quantity", 0)
            tags = ("lowstock",) if isinstance(qty, (int, float)) and qty <= 5 else ()

            self.tree.insert("", "end", values=(
                p.get("id", ""),
                p.get("name", ""),
                p.get("category", ""),
                f"₹{p.get('price', 0):.2f}",
                p.get("quantity", 0),
                p.get("supplier", ""),
                p.get("sku", ""),
                p.get("added", "")
            ), tags=tags)

        self.update_dashboard()

    def _sort_column(self, col):
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            items.sort(key=lambda t: float(t[0].replace("₹", "").replace(",", "")))
        except ValueError:
            items.sort(key=lambda t: t[0])

        # Toggle order
        if getattr(self, "_sort_reverse", False) and getattr(self, "_sort_col", None) == col:
            items.reverse()
            self._sort_reverse = False
        else:
            self._sort_reverse = True
        self._sort_col = col

        for idx, (_, k) in enumerate(items):
            self.tree.move(k, "", idx)

    # ---------- Dashboard ----------
    def update_dashboard(self):
        total = len(self.products)
        stock = sum(p.get("quantity", 0) for p in self.products)
        value = sum(p.get("quantity", 0) * p.get("price", 0) for p in self.products)
        low = sum(1 for p in self.products if p.get("quantity", 0) <= 5)

        self.card_total.config(text=str(total))
        self.card_stock.config(text=str(stock))
        self.card_value.config(text=f"₹{value:,.2f}")
        self.card_low.config(text=str(low),
                             fg=self.colors["accent"] if low > 0 else self.colors["secondary"])

    # ---------- Form ----------
    def get_form_data(self):
        name = self.fields["name"].get().strip()
        category = self.fields["category"].get()
        price = self.fields["price"].get().strip()
        quantity = self.fields["quantity"].get().strip()
        supplier = self.fields["supplier"].get().strip()
        sku = self.fields["sku"].get().strip()

        if not name:
            messagebox.showwarning("Validation", "Product name is required.")
            return None
        if category == "Select Category":
            messagebox.showwarning("Validation", "Please select a category.")
            return None
        try:
            price = float(price) if price else 0.0
            if price < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Price must be a non-negative number.")
            return None
        try:
            quantity = int(quantity) if quantity else 0
            if quantity < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Validation", "Quantity must be a non-negative integer.")
            return None

        return {
            "name": name, "category": category,
            "price": price, "quantity": quantity,
            "supplier": supplier, "sku": sku
        }

    def add_product(self):
        data = self.get_form_data()
        if not data:
            return
        new_id = max([p.get("id", 0) for p in self.products], default=0) + 1
        data["id"] = new_id
        data["added"] = datetime.now().strftime("%d-%m-%Y")
        self.products.append(data)
        self.save_data()
        self.refresh_table()
        self.clear_form()
        self.status.config(text=f"✅ Added: {data['name']} (ID: {new_id})")
        if data["quantity"] <= 5:
            messagebox.showinfo("Low Stock Alert",
                                f"'{data['name']}' added with low stock ({data['quantity']}).")

    def update_product(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Please select a product to update.")
            return
        data = self.get_form_data()
        if not data:
            return
        item = self.tree.item(sel[0])
        pid = item["values"][0]
        for p in self.products:
            if p.get("id") == pid:
                p.update(data)
                break
        self.save_data()
        self.refresh_table()
        self.clear_form()
        self.status.config(text=f"✏️ Updated product ID {pid}")

    def delete_product(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection", "Please select a product to delete.")
            return
        item = self.tree.item(sel[0])
        pid = item["values"][0]
        name = item["values"][1]
        if not messagebox.askyesno("Confirm Delete",
                                   f"Delete '{name}' (ID: {pid})?\nThis cannot be undone."):
            return
        self.products = [p for p in self.products if p.get("id") != pid]
        self.save_data()
        self.refresh_table()
        self.clear_form()
        self.status.config(text=f"🗑️ Deleted: {name}")

    def clear_form(self):
        self.fields["name"].delete(0, tk.END)
        self.fields["category"].set("Select Category")
        self.fields["price"].delete(0, tk.END)
        self.fields["quantity"].delete(0, tk.END)
        self.fields["supplier"].delete(0, tk.END)
        self.fields["sku"].delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection()) if self.tree.selection() else None

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        vals = item["values"]
        pid = vals[0]
        prod = next((p for p in self.products if p.get("id") == pid), None)
        if not prod:
            return
        self.fields["name"].delete(0, tk.END)
        self.fields["name"].insert(0, prod.get("name", ""))
        self.fields["category"].set(prod.get("category", "Select Category"))
        self.fields["price"].delete(0, tk.END)
        self.fields["price"].insert(0, prod.get("price", ""))
        self.fields["quantity"].delete(0, tk.END)
        self.fields["quantity"].insert(0, prod.get("quantity", ""))
        self.fields["supplier"].delete(0, tk.END)
        self.fields["supplier"].insert(0, prod.get("supplier", ""))
        self.fields["sku"].delete(0, tk.END)
        self.fields["sku"].insert(0, prod.get("sku", ""))
        self.status.config(text=f"Selected: {prod.get('name')} (ID: {pid})")

    # ---------- Export ----------
    def export_csv(self):
        if not self.products:
            messagebox.showinfo("Export", "No products to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "id", "name", "category", "price",
                    "quantity", "supplier", "sku", "added"
                ])
                writer.writeheader()
                writer.writerows(self.products)
            messagebox.showinfo("Success", f"Exported {len(self.products)} products to:\n{path}")
            self.status.config(text=f"📤 Exported to {os.path.basename(path)}")
        except IOError as e:
            messagebox.showerror("Export Error", f"Could not export:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()