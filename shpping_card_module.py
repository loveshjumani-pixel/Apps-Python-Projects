import tkinter as tk
from tkinter import ttk, messagebox

class ShoppingCart:
    def __init__(self, root):
        self.root = root
        self.root.title("Shopping Cart - Professional")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)
        self.root.configure(bg="#f5f7fa")

        # Color palette
        self.colors = {
            "bg": "#f5f7fa",
            "sidebar": "#1f2937",
            "sidebar_active": "#3b82f6",
            "card": "#ffffff",
            "primary": "#3b82f6",
            "primary_dark": "#2563eb",
            "accent": "#f59e0b",
            "success": "#10b981",
            "danger": "#ef4444",
            "text": "#1f2937",
            "muted": "#6b7280",
            "border": "#e5e7eb",
            "input_bg": "#f9fafb",
            "price": "#dc2626",
        }

        # Products catalog
        self.products = [
            # Electronics
            {"id": 1, "name": "Wireless Headphones", "category": "Electronics", "price": 2499, "stock": 15, "icon": "[H]"},
            {"id": 2, "name": "Smart Watch", "category": "Electronics", "price": 4999, "stock": 8, "icon": "[W]"},
            {"id": 3, "name": "Bluetooth Speaker", "category": "Electronics", "price": 1799, "stock": 20, "icon": "[S]"},
            {"id": 4, "name": "USB-C Cable", "category": "Electronics", "price": 299, "stock": 50, "icon": "[C]"},
            # Clothing
            {"id": 5, "name": "Cotton T-Shirt", "category": "Clothing", "price": 599, "stock": 30, "icon": "[T]"},
            {"id": 6, "name": "Denim Jeans", "category": "Clothing", "price": 1499, "stock": 18, "icon": "[J]"},
            {"id": 7, "name": "Running Shoes", "category": "Clothing", "price": 2799, "stock": 12, "icon": "[R]"},
            {"id": 8, "name": "Winter Jacket", "category": "Clothing", "price": 3499, "stock": 7, "icon": "[K]"},
            # Food
            {"id": 9, "name": "Organic Coffee 500g", "category": "Food", "price": 449, "stock": 25, "icon": "[F]"},
            {"id": 10, "name": "Dark Chocolate", "category": "Food", "price": 199, "stock": 40, "icon": "[D]"},
            {"id": 11, "name": "Green Tea Pack", "category": "Food", "price": 249, "stock": 35, "icon": "[G]"},
            {"id": 12, "name": "Mixed Nuts 1kg", "category": "Food", "price": 699, "stock": 15, "icon": "[N]"},
            # Books
            {"id": 13, "name": "Python Programming", "category": "Books", "price": 599, "stock": 22, "icon": "[P]"},
            {"id": 14, "name": "Fiction Novel", "category": "Books", "price": 349, "stock": 28, "icon": "[B]"},
            {"id": 15, "name": "Self Help Guide", "category": "Books", "price": 299, "stock": 19, "icon": "[S]"},
            {"id": 16, "name": "Science Encyclopedia", "category": "Books", "price": 899, "stock": 10, "icon": "[E]"},
            # Home
            {"id": 17, "name": "LED Desk Lamp", "category": "Home", "price": 1299, "stock": 14, "icon": "[L]"},
            {"id": 18, "name": "Cushion Set (4)", "category": "Home", "price": 999, "stock": 16, "icon": "[U]"},
            {"id": 19, "name": "Wall Clock", "category": "Home", "price": 749, "stock": 21, "icon": "[O]"},
            {"id": 20, "name": "Bed Sheet Set", "category": "Home", "price": 1599, "stock": 9, "icon": "[B]"},
        ]

        self.cart = {}  # {product_id: quantity}
        self.current_category = "All"
        self.search_var = tk.StringVar()
        self.coupon_var = tk.StringVar()
        self.discount_percent = 0

        self._setup_styles()
        self._build_ui()
        self._bind_events()
        self._refresh_products()
        self._refresh_cart()

    # ---------------- STYLES ----------------
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("TLabel", background=self.colors["card"],
                        foreground=self.colors["text"],
                        font=("Segoe UI", 10))
        style.configure("TEntry", padding=6, font=("Segoe UI", 10))

    # ---------------- UI ----------------
    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.colors["primary"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="SHOPPY",
                 font=("Segoe UI", 18, "bold"),
                 bg=self.colors["primary"], fg="white").pack(side="left", padx=20, pady=15)

        tk.Label(header, text="Your One-Stop Shop",
                 font=("Segoe UI", 10, "italic"),
                 bg=self.colors["primary"], fg="#dbeafe").pack(side="left", padx=5)

        self.cart_count_label = tk.Label(header, text="Cart: 0 items",
                                         font=("Segoe UI", 11, "bold"),
                                         bg=self.colors["accent"], fg="white",
                                         padx=15, pady=6)
        self.cart_count_label.pack(side="right", padx=20, pady=12)

        # Main container
        main = tk.Frame(self.root, bg=self.colors["bg"])
        main.pack(fill="both", expand=True, padx=15, pady=15)

        # Left: Categories
        sidebar = tk.Frame(main, bg=self.colors["sidebar"], width=180)
        sidebar.pack(side="left", fill="y", padx=(0, 15))
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="CATEGORIES",
                 font=("Segoe UI", 10, "bold"),
                 bg=self.colors["sidebar"], fg="#9ca3af").pack(pady=(15, 10))

        self.cat_buttons = {}
        categories = ["All", "Electronics", "Clothing", "Food", "Books", "Home"]
        for cat in categories:
            btn = tk.Button(sidebar, text=cat,
                            font=("Segoe UI", 11),
                            bg=self.colors["sidebar"], fg="white",
                            activebackground=self.colors["sidebar_active"],
                            activeforeground="white",
                            bd=0, padx=15, pady=10,
                            cursor="hand2",
                            command=lambda c=cat: self._select_category(c))
            btn.pack(fill="x", padx=8, pady=2)
            self.cat_buttons[cat] = btn

        # Coupons info
        tk.Label(sidebar, text="COUPONS",
                 font=("Segoe UI", 10, "bold"),
                 bg=self.colors["sidebar"], fg="#9ca3af").pack(pady=(25, 10))
        tk.Label(sidebar, text="SAVE10  = 10% off\nSAVE20  = 20% off\nWELCOME50 = 50% off",
                 font=("Segoe UI", 9),
                 bg=self.colors["sidebar"], fg="#d1d5db",
                 justify="left").pack(padx=15, anchor="w")

        self._select_category("All", init=True)

        # Middle: Products
        middle = tk.Frame(main, bg=self.colors["bg"])
        middle.pack(side="left", fill="both", expand=True)

        # Search bar
        search_frame = tk.Frame(middle, bg=self.colors["card"],
                                highlightbackground=self.colors["border"],
                                highlightthickness=1)
        search_frame.pack(fill="x", pady=(0, 15))

        tk.Label(search_frame, text="Search:",
                 font=("Segoe UI", 10, "bold"),
                 bg=self.colors["card"], fg=self.colors["muted"]).pack(side="left", padx=15, pady=12)

        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                     font=("Segoe UI", 11),
                                     bg=self.colors["input_bg"],
                                     fg=self.colors["text"],
                                     bd=0, relief="flat")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10, ipady=6)
        self.search_var.trace_add("write", lambda *a: self._refresh_products())

        self.product_count_label = tk.Label(search_frame, text="0 products",
                                            font=("Segoe UI", 10),
                                            bg=self.colors["card"],
                                            fg=self.colors["muted"])
        self.product_count_label.pack(side="right", padx=15)

        # Products grid (using canvas for scrolling)
        products_container = tk.Frame(middle, bg=self.colors["bg"])
        products_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(products_container, bg=self.colors["bg"],
                                highlightthickness=0)
        scrollbar = ttk.Scrollbar(products_container, orient="vertical",
                                  command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=self.colors["bg"])

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mouse wheel scroll
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # Right: Cart
        cart_panel = tk.Frame(main, bg=self.colors["card"], width=320,
                              highlightbackground=self.colors["border"],
                              highlightthickness=1)
        cart_panel.pack(side="right", fill="y", padx=(15, 0))
        cart_panel.pack_propagate(False)

        tk.Label(cart_panel, text="YOUR CART",
                 font=("Segoe UI", 12, "bold"),
                 bg=self.colors["card"], fg=self.colors["text"]).pack(pady=(15, 10))

        # Cart items list
        cart_list_frame = tk.Frame(cart_panel, bg=self.colors["card"])
        cart_list_frame.pack(fill="both", expand=True, padx=10)

        self.cart_canvas = tk.Canvas(cart_list_frame, bg=self.colors["card"],
                                     highlightthickness=0)
        cart_sb = ttk.Scrollbar(cart_list_frame, orient="vertical",
                                command=self.cart_canvas.yview)
        self.cart_scroll_frame = tk.Frame(self.cart_canvas, bg=self.colors["card"])

        self.cart_scroll_frame.bind(
            "<Configure>",
            lambda e: self.cart_canvas.configure(scrollregion=self.cart_canvas.bbox("all"))
        )

        self.cart_canvas.create_window((0, 0), window=self.cart_scroll_frame, anchor="nw")
        self.cart_canvas.configure(yscrollcommand=cart_sb.set)

        self.cart_canvas.pack(side="left", fill="both", expand=True)
        cart_sb.pack(side="right", fill="y")

        # Coupon input
        coupon_frame = tk.Frame(cart_panel, bg=self.colors["card"])
        coupon_frame.pack(fill="x", padx=10, pady=5)

        tk.Entry(coupon_frame, textvariable=self.coupon_var,
                 font=("Segoe UI", 10),
                 bg=self.colors["input_bg"],
                 bd=1, relief="solid").pack(side="left", fill="x", expand=True, ipady=4)

        tk.Button(coupon_frame, text="Apply",
                  font=("Segoe UI", 9, "bold"),
                  bg=self.colors["primary"], fg="white",
                  activebackground=self.colors["primary_dark"],
                  bd=0, padx=10, cursor="hand2",
                  command=self._apply_coupon).pack(side="right", padx=(5, 0))

        # Totals
        totals_frame = tk.Frame(cart_panel, bg=self.colors["input_bg"],
                                highlightbackground=self.colors["border"],
                                highlightthickness=1)
        totals_frame.pack(fill="x", padx=10, pady=10)

        self.subtotal_label = tk.Label(totals_frame, text="Subtotal:    Rs.0.00",
                                       font=("Segoe UI", 10),
                                       bg=self.colors["input_bg"],
                                       fg=self.colors["text"],
                                       anchor="w")
        self.subtotal_label.pack(fill="x", padx=15, pady=(10, 2))

        self.tax_label = tk.Label(totals_frame, text="GST (18%):   Rs.0.00",
                                  font=("Segoe UI", 10),
                                  bg=self.colors["input_bg"],
                                  fg=self.colors["text"],
                                  anchor="w")
        self.tax_label.pack(fill="x", padx=15, pady=2)

        self.discount_label = tk.Label(totals_frame, text="Discount:    -Rs.0.00",
                                       font=("Segoe UI", 10),
                                       bg=self.colors["input_bg"],
                                       fg=self.colors["success"],
                                       anchor="w")
        self.discount_label.pack(fill="x", padx=15, pady=2)

        tk.Frame(totals_frame, bg=self.colors["border"], height=1).pack(fill="x", padx=15, pady=5)

        self.total_label = tk.Label(totals_frame, text="TOTAL:       Rs.0.00",
                                    font=("Segoe UI", 13, "bold"),
                                    bg=self.colors["input_bg"],
                                    fg=self.colors["price"],
                                    anchor="w")
        self.total_label.pack(fill="x", padx=15, pady=(2, 10))

        # Checkout button
        self.checkout_btn = tk.Button(cart_panel, text="CHECKOUT",
                                      font=("Segoe UI", 12, "bold"),
                                      bg=self.colors["success"], fg="white",
                                      activebackground="#059669",
                                      activeforeground="white",
                                      bd=0, pady=12, cursor="hand2",
                                      command=self._checkout)
        self.checkout_btn.pack(fill="x", padx=10, pady=(0, 15))

        # Status bar
        self.status = tk.Label(self.root, text="Ready | Add items to cart to begin",
                               bg=self.colors["primary"], fg="white",
                               font=("Segoe UI", 9), anchor="w")
        self.status.pack(side="bottom", fill="x")

    # ---------------- EVENTS ----------------
    def _bind_events(self):
        self.root.bind("<Control-f>", lambda e: self.search_entry.focus_set())

    # ---------------- CATEGORY ----------------
    def _select_category(self, cat, init=False):
        self.current_category = cat
        for n, b in self.cat_buttons.items():
            if n == cat:
                b.config(bg=self.colors["sidebar_active"])
            else:
                b.config(bg=self.colors["sidebar"])
        if not init:
            self._refresh_products()

    # ---------------- PRODUCTS ----------------
    def _refresh_products(self):
        # Clear existing widgets
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        search = self.search_var.get().lower().strip()
        filtered = []
        for p in self.products:
            if self.current_category != "All" and p["category"] != self.current_category:
                continue
            if search and search not in p["name"].lower():
                continue
            filtered.append(p)

        self.product_count_label.config(text=f"{len(filtered)} products")

        # Create product cards in grid (3 columns)
        cols = 3
        for idx, product in enumerate(filtered):
            row = idx // cols
            col = idx % cols
            self._make_product_card(self.scroll_frame, product, row, col)

        # Make columns expand equally
        for c in range(cols):
            self.scroll_frame.columnconfigure(c, weight=1, uniform="col")

        if not filtered:
            tk.Label(self.scroll_frame, text="No products found",
                     font=("Segoe UI", 12, "italic"),
                     bg=self.colors["bg"], fg=self.colors["muted"]).grid(
                row=0, column=0, columnspan=cols, pady=50)

    def _make_product_card(self, parent, product, row, col):
        card = tk.Frame(parent, bg=self.colors["card"],
                        highlightbackground=self.colors["border"],
                        highlightthickness=1)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        # Icon area
        icon_frame = tk.Frame(card, bg=self.colors["input_bg"], height=80)
        icon_frame.pack(fill="x")
        icon_frame.pack_propagate(False)

        tk.Label(icon_frame, text=product["icon"],
                 font=("Segoe UI", 28, "bold"),
                 bg=self.colors["input_bg"],
                 fg=self.colors["primary"]).pack(expand=True)

        # Info
        info = tk.Frame(card, bg=self.colors["card"])
        info.pack(fill="x", padx=10, pady=(8, 0))

        tk.Label(info, text=product["name"],
                 font=("Segoe UI", 10, "bold"),
                 bg=self.colors["card"], fg=self.colors["text"],
                 anchor="w", wraplength=200, justify="left").pack(fill="x")

        tk.Label(info, text=product["category"],
                 font=("Segoe UI", 8),
                 bg=self.colors["card"], fg=self.colors["muted"],
                 anchor="w").pack(fill="x")

        # Price + Stock
        price_frame = tk.Frame(card, bg=self.colors["card"])
        price_frame.pack(fill="x", padx=10, pady=(5, 0))

        tk.Label(price_frame, text=f"Rs.{product['price']:,}",
                 font=("Segoe UI", 13, "bold"),
                 bg=self.colors["card"], fg=self.colors["price"],
                 anchor="w").pack(side="left")

        stock_color = self.colors["success"] if product["stock"] > 5 else self.colors["accent"]
        tk.Label(price_frame, text=f"{product['stock']} left",
                 font=("Segoe UI", 9),
                 bg=self.colors["card"], fg=stock_color).pack(side="right")

        # Add button
        btn = tk.Button(card, text="ADD TO CART",
                        font=("Segoe UI", 9, "bold"),
                        bg=self.colors["primary"], fg="white",
                        activebackground=self.colors["primary_dark"],
                        activeforeground="white",
                        bd=0, pady=6, cursor="hand2",
                        command=lambda p=product: self._add_to_cart(p["id"]))
        btn.pack(fill="x", padx=10, pady=10)

        # Disable if out of stock
        if product["stock"] == 0:
            btn.config(state="disabled", bg="#9ca3af", text="OUT OF STOCK")

    # ---------------- CART ----------------
    def _add_to_cart(self, product_id):
        try:
            product = next((p for p in self.products if p["id"] == product_id), None)
            if not product:
                return

            current_qty = self.cart.get(product_id, 0)
            if current_qty >= product["stock"]:
                messagebox.showwarning("Stock Limit",
                                       f"Only {product['stock']} units of '{product['name']}' available.")
                return

            self.cart[product_id] = current_qty + 1
            self._refresh_cart()
            self.status.config(text=f"Added: {product['name']}")
        except Exception as e:
            print(f"Error adding to cart: {e}")

    def _change_quantity(self, product_id, delta):
        try:
            product = next((p for p in self.products if p["id"] == product_id), None)
            if not product:
                return

            current = self.cart.get(product_id, 0)
            new_qty = current + delta

            if new_qty <= 0:
                self._remove_from_cart(product_id)
                return

            if new_qty > product["stock"]:
                messagebox.showwarning("Stock Limit",
                                       f"Only {product['stock']} units available.")
                return

            self.cart[product_id] = new_qty
            self._refresh_cart()
        except Exception as e:
            print(f"Error changing quantity: {e}")

    def _remove_from_cart(self, product_id):
        try:
            if product_id in self.cart:
                del self.cart[product_id]
                self._refresh_cart()
                self.status.config(text="Item removed from cart")
        except Exception as e:
            print(f"Error removing from cart: {e}")

    def _refresh_cart(self):
        try:
            # Clear cart widgets
            for widget in self.cart_scroll_frame.winfo_children():
                widget.destroy()

            if not self.cart:
                tk.Label(self.cart_scroll_frame, text="Your cart is empty",
                         font=("Segoe UI", 11, "italic"),
                         bg=self.colors["card"], fg=self.colors["muted"],
                         pady=30).pack(fill="x")
                self._update_totals(0, 0, 0, 0)
                self.cart_count_label.config(text="Cart: 0 items")
                return

            total_items = 0
            subtotal = 0

            for pid, qty in self.cart.items():
                product = next((p for p in self.products if p["id"] == pid), None)
                if not product:
                    continue

                total_items += qty
                item_total = product["price"] * qty
                subtotal += item_total

                self._make_cart_item(self.cart_scroll_frame, product, qty, item_total)

            tax = subtotal * 0.18
            discount = subtotal * (self.discount_percent / 100)
            grand_total = subtotal + tax - discount

            self._update_totals(subtotal, tax, discount, grand_total)
            self.cart_count_label.config(text=f"Cart: {total_items} item{'s' if total_items != 1 else ''}")

        except Exception as e:
            print(f"Error refreshing cart: {e}")

    def _make_cart_item(self, parent, product, qty, item_total):
        item = tk.Frame(parent, bg=self.colors["card"],
                        highlightbackground=self.colors["border"],
                        highlightthickness=1)
        item.pack(fill="x", padx=5, pady=4)

        top = tk.Frame(item, bg=self.colors["card"])
        top.pack(fill="x", padx=8, pady=(6, 2))

        tk.Label(top, text=product["name"],
                 font=("Segoe UI", 9, "bold"),
                 bg=self.colors["card"], fg=self.colors["text"],
                 anchor="w", wraplength=220, justify="left").pack(side="left", fill="x", expand=True)

        tk.Button(top, text="X",
                  font=("Segoe UI", 9, "bold"),
                  bg=self.colors["danger"], fg="white",
                  activebackground="#dc2626",
                  bd=0, width=2, cursor="hand2",
                  command=lambda pid=product["id"]: self._remove_from_cart(pid)).pack(side="right")

        bottom = tk.Frame(item, bg=self.colors["card"])
        bottom.pack(fill="x", padx=8, pady=(0, 6))

        # Quantity controls
        tk.Button(bottom, text="-",
                  font=("Segoe UI", 10, "bold"),
                  bg=self.colors["input_bg"], fg=self.colors["text"],
                  bd=1, relief="solid", width=2, cursor="hand2",
                  command=lambda pid=product["id"]: self._change_quantity(pid, -1)).pack(side="left")

        tk.Label(bottom, text=str(qty),
                 font=("Segoe UI", 10, "bold"),
                 bg=self.colors["card"], fg=self.colors["text"],
                 width=3).pack(side="left", padx=4)

        tk.Button(bottom, text="+",
                  font=("Segoe UI", 10, "bold"),
                  bg=self.colors["input_bg"], fg=self.colors["text"],
                  bd=1, relief="solid", width=2, cursor="hand2",
                  command=lambda pid=product["id"]: self._change_quantity(pid, 1)).pack(side="left", padx=(4, 10))

        tk.Label(bottom, text=f"Rs.{item_total:,.2f}",
                 font=("Segoe UI", 10, "bold"),
                 bg=self.colors["card"], fg=self.colors["price"]).pack(side="right")

    def _update_totals(self, subtotal, tax, discount, total):
        try:
            self.subtotal_label.config(text=f"Subtotal:    Rs.{subtotal:,.2f}")
            self.tax_label.config(text=f"GST (18%):   Rs.{tax:,.2f}")
            self.discount_label.config(text=f"Discount:    -Rs.{discount:,.2f}")
            self.total_label.config(text=f"TOTAL:       Rs.{total:,.2f}")
        except Exception as e:
            print(f"Error updating totals: {e}")

    # ---------------- COUPON ----------------
    def _apply_coupon(self):
        try:
            code = self.coupon_var.get().strip().upper()
            coupons = {"SAVE10": 10, "SAVE20": 20, "WELCOME50": 50}

            if not code:
                self.discount_percent = 0
                self.status.config(text="Coupon cleared")
                self._refresh_cart()
                return

            if code in coupons:
                self.discount_percent = coupons[code]
                self.status.config(text=f"Coupon applied: {code} ({self.discount_percent}% off)")
                messagebox.showinfo("Coupon Applied",
                                    f"{code} applied!\nYou get {self.discount_percent}% off on subtotal.")
            else:
                self.discount_percent = 0
                messagebox.showwarning("Invalid Coupon",
                                       f"Coupon '{code}' is not valid.\nTry: SAVE10, SAVE20, or WELCOME50")

            self._refresh_cart()
        except Exception as e:
            print(f"Error applying coupon: {e}")

    # ---------------- CHECKOUT ----------------
    def _checkout(self):
        try:
            if not self.cart:
                messagebox.showinfo("Empty Cart", "Your cart is empty. Add some items first!")
                return

            # Build order summary
            lines = ["=" * 40, "       ORDER SUMMARY", "=" * 40, ""]
            subtotal = 0
            for pid, qty in self.cart.items():
                product = next((p for p in self.products if p["id"] == pid), None)
                if not product:
                    continue
                item_total = product["price"] * qty
                subtotal += item_total
                lines.append(f"{product['name']}")
                lines.append(f"  {qty} x Rs.{product['price']:,} = Rs.{item_total:,.2f}")
                lines.append("")

            tax = subtotal * 0.18
            discount = subtotal * (self.discount_percent / 100)
            grand_total = subtotal + tax - discount

            lines.append("-" * 40)
            lines.append(f"Subtotal:   Rs.{subtotal:,.2f}")
            lines.append(f"GST (18%):  Rs.{tax:,.2f}")
            if discount > 0:
                lines.append(f"Discount:  -Rs.{discount:,.2f}")
            lines.append("-" * 40)
            lines.append(f"TOTAL:      Rs.{grand_total:,.2f}")
            lines.append("=" * 40)
            lines.append("\nThank you for shopping with Shoppy!")

            summary = "\n".join(lines)

            if messagebox.askyesno("Confirm Checkout",
                                   f"Total amount: Rs.{grand_total:,.2f}\n\nProceed to checkout?"):
                messagebox.showinfo("Order Placed", summary)
                # Reset
                self.cart.clear()
                self.discount_percent = 0
                self.coupon_var.set("")
                self._refresh_cart()
                self.status.config(text="Order placed successfully! Thank you.")
        except Exception as e:
            print(f"Error during checkout: {e}")
            messagebox.showerror("Error", f"Checkout failed: {e}")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ShoppingCart(root)
        root.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()