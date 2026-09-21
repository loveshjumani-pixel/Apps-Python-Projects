import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import sys
from datetime import datetime

class ATMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ATM Simulation - Professional Banking")
        self.root.geometry("500x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f2f5")
        
        # Current logged-in user data
        self.current_account = None
        self.current_balance = 0.0
        self.current_name = ""
        
        # Color scheme
        self.colors = {
            "primary": "#1a5490",
            "secondary": "#2c7be5",
            "accent": "#f6c90e",
            "success": "#28a745",
            "danger": "#dc3545",
            "warning": "#fd7e14",
            "bg": "#f0f2f5",
            "card": "#ffffff",
            "text_dark": "#212529",
            "text_light": "#6c757d",
        }
        
        # Fonts (safe fonts)
        self.font_title = ("Arial", 22, "bold")
        self.font_heading = ("Arial", 16, "bold")
        self.font_sub = ("Arial", 12, "bold")
        self.font_normal = ("Arial", 11)
        self.font_small = ("Arial", 10)
        self.font_btn = ("Arial", 12, "bold")
        self.font_big = ("Arial", 28, "bold")
        
        # Database setup
        self.setup_database()
        
        # Create all screens
        self.frames = {}
        self.create_login_screen()
        self.create_main_menu()
        self.create_withdraw_screen()
        self.create_deposit_screen()
        self.create_balance_screen()
        self.create_pin_change_screen()
        self.create_history_screen()
        
        # Show login screen
        self.show_frame("login")
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_database(self):
        try:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'atm_data.db')
            self.conn = sqlite3.connect(db_path)
            self.c = self.conn.cursor()
            
            # Accounts table
            self.c.execute('''CREATE TABLE IF NOT EXISTS accounts
                              (account_no TEXT PRIMARY KEY, pin TEXT, name TEXT, balance REAL)''')
            
            # Transactions table
            self.c.execute('''CREATE TABLE IF NOT EXISTS transactions
                              (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                               account_no TEXT, type TEXT, amount REAL, 
                               balance_after REAL, date TEXT, description TEXT)''')
            
            self.conn.commit()
            
            # Insert default account if not exists
            self.c.execute("SELECT * FROM accounts WHERE account_no='1234567890'")
            if not self.c.fetchone():
                self.c.execute("INSERT INTO accounts VALUES (?, ?, ?, ?)",
                               ('1234567890', '1234', 'Demo User', 10000.0))
                self.conn.commit()
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to setup database: {e}")
            sys.exit(1)
    
    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        
        # Refresh specific screens when shown
        if name == "balance":
            self.refresh_balance()
        elif name == "history":
            self.refresh_history()
        elif name == "main_menu":
            self.update_status_bar()
    
    def create_header(self, parent, title, show_back=False, back_command=None):
        header = tk.Frame(parent, bg=self.colors["primary"], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        if show_back:
            back_btn = tk.Button(header, text="< Back", font=self.font_small,
                                bg=self.colors["primary"], fg="white",
                                relief=tk.FLAT, cursor="hand2",
                                activebackground=self.colors["primary"],
                                activeforeground="white",
                                command=back_command)
            back_btn.pack(side=tk.LEFT, padx=15, pady=20)
        
        title_lbl = tk.Label(header, text=title, font=self.font_title,
                            bg=self.colors["primary"], fg="white")
        title_lbl.pack(side=tk.LEFT if show_back else tk.LEFT, expand=not show_back, 
                      padx=15 if show_back else 0, pady=15)
        
        # Logout button on main menu
        if title == "MAIN MENU":
            logout_btn = tk.Button(header, text="Logout", font=self.font_small,
                                  bg=self.colors["danger"], fg="white",
                                  relief=tk.FLAT, cursor="hand2",
                                  activebackground="#b02a37",
                                  activeforeground="white",
                                  command=self.logout)
            logout_btn.pack(side=tk.RIGHT, padx=15, pady=20)
    
    def create_login_screen(self):
        frame = tk.Frame(self.root, bg=self.colors["bg"])
        frame.place(relwidth=1, relheight=1)
        self.frames["login"] = frame
        
        # Logo area
        logo_frame = tk.Frame(frame, bg=self.colors["primary"], height=150)
        logo_frame.pack(fill=tk.X)
        logo_frame.pack_propagate(False)
        
        bank_name = tk.Label(logo_frame, text="SECURE BANK ATM",
                            font=("Arial", 24, "bold"),
                            bg=self.colors["primary"], fg="white")
        bank_name.pack(pady=20)
        
        subtitle = tk.Label(logo_frame, text="24/7 Banking Service",
                           font=self.font_normal,
                           bg=self.colors["primary"], fg=self.colors["accent"])
        subtitle.pack()
        
        # Login card
        card = tk.Frame(frame, bg=self.colors["card"], relief=tk.RAISED, bd=3)
        card.pack(padx=40, pady=40, fill=tk.BOTH, expand=True)
        
        tk.Label(card, text="Customer Login", font=self.font_heading,
                bg=self.colors["card"], fg=self.colors["primary"]).pack(pady=(25, 20))
        
        # Account Number
        acc_frame = tk.Frame(card, bg=self.colors["card"])
        acc_frame.pack(fill=tk.X, padx=40, pady=10)
        tk.Label(acc_frame, text="Account Number:", font=self.font_normal,
                bg=self.colors["card"], anchor="w").pack(fill=tk.X)
        self.acc_entry = tk.Entry(acc_frame, font=self.font_normal,
                                 relief=tk.SOLID, bd=1, justify="center")
        self.acc_entry.pack(fill=tk.X, pady=(5, 0), ipady=8)
        
        # PIN
        pin_frame = tk.Frame(card, bg=self.colors["card"])
        pin_frame.pack(fill=tk.X, padx=40, pady=10)
        tk.Label(pin_frame, text="PIN (4 digits):", font=self.font_normal,
                bg=self.colors["card"], anchor="w").pack(fill=tk.X)
        self.pin_entry = tk.Entry(pin_frame, font=self.font_normal,
                                 relief=tk.SOLID, bd=1, show="*", justify="center")
        self.pin_entry.pack(fill=tk.X, pady=(5, 0), ipady=8)
        self.pin_entry.bind("<Return>", lambda e: self.login())
        
        # Login button
        login_btn = tk.Button(card, text="LOGIN", font=self.font_btn,
                             bg=self.colors["success"], fg="white",
                             relief=tk.FLAT, cursor="hand2",
                             activebackground="#1e7e34",
                             activeforeground="white",
                             command=self.login)
        login_btn.pack(fill=tk.X, padx=40, pady=20, ipady=10)
        
        # Hint
        tk.Label(card, text="Demo: Account 1234567890 | PIN 1234",
                font=self.font_small, bg=self.colors["card"],
                fg=self.colors["text_light"]).pack(pady=(0, 15))
    
    def create_main_menu(self):
        frame = tk.Frame(self.root, bg=self.colors["bg"])
        frame.place(relwidth=1, relheight=1)
        self.frames["main_menu"] = frame
        
        self.create_header(frame, "MAIN MENU")
        
        # Status bar
        self.status_frame = tk.Frame(frame, bg=self.colors["accent"], height=50)
        self.status_frame.pack(fill=tk.X)
        self.status_frame.pack_propagate(False)
        
        self.welcome_lbl = tk.Label(self.status_frame, text="",
                                   font=self.font_sub,
                                   bg=self.colors["accent"],
                                   fg=self.colors["text_dark"])
        self.welcome_lbl.pack(side=tk.LEFT, padx=15, pady=10)
        
        self.balance_lbl = tk.Label(self.status_frame, text="",
                                   font=self.font_sub,
                                   bg=self.colors["accent"],
                                   fg=self.colors["text_dark"])
        self.balance_lbl.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Menu buttons grid
        menu_frame = tk.Frame(frame, bg=self.colors["bg"])
        menu_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        buttons = [
            ("Balance Inquiry", self.colors["secondary"], lambda: self.show_frame("balance"), "0"),
            ("Cash Withdraw", self.colors["success"], lambda: self.show_frame("withdraw"), "1"),
            ("Cash Deposit", self.colors["warning"], lambda: self.show_frame("deposit"), "2"),
            ("Change PIN", self.colors["primary"], lambda: self.show_frame("pin_change"), "3"),
            ("Transaction History", "#6f42c1", lambda: self.show_frame("history"), "4"),
            ("Exit", self.colors["danger"], self.logout, "5"),
        ]
        
        for i, (text, color, cmd, _) in enumerate(buttons):
            row = i // 2
            col = i % 2
            btn = tk.Button(menu_frame, text=text, font=self.font_btn,
                           bg=color, fg="white", relief=tk.FLAT,
                           cursor="hand2", activebackground=color,
                           activeforeground="white", command=cmd)
            btn.grid(row=row, column=col, padx=10, pady=10,
                    sticky="nsew", ipady=25)
        
        for i in range(2):
            menu_frame.grid_columnconfigure(i, weight=1)
        for i in range(3):
            menu_frame.grid_rowconfigure(i, weight=1)
        
        # Footer
        tk.Label(frame, text="Secure Banking | 24/7 Support",
                font=self.font_small, bg=self.colors["bg"],
                fg=self.colors["text_light"]).pack(side=tk.BOTTOM, pady=10)
    
    def create_withdraw_screen(self):
        frame = tk.Frame(self.root, bg=self.colors["bg"])
        frame.place(relwidth=1, relheight=1)
        self.frames["withdraw"] = frame
        
        self.create_header(frame, "CASH WITHDRAW", True,
                          lambda: self.show_frame("main_menu"))
        
        card = tk.Frame(frame, bg=self.colors["card"], relief=tk.RAISED, bd=2)
        card.pack(padx=30, pady=20, fill=tk.BOTH, expand=True)
        
        tk.Label(card, text="Enter Withdrawal Amount",
                font=self.font_heading, bg=self.colors["card"],
                fg=self.colors["primary"]).pack(pady=20)
        
        tk.Label(card, text="(Amount should be in multiples of 100)",
                font=self.font_small, bg=self.colors["card"],
                fg=self.colors["text_light"]).pack()
        
        amt_frame = tk.Frame(card, bg=self.colors["card"])
        amt_frame.pack(fill=tk.X, padx=40, pady=20)
        
        tk.Label(amt_frame, text="Rs.", font=self.font_heading,
                bg=self.colors["card"], fg=self.colors["text_dark"]).pack(side=tk.LEFT)
        
        self.withdraw_entry = tk.Entry(amt_frame, font=self.font_big,
                                      relief=tk.SOLID, bd=1, justify="center")
        self.withdraw_entry.pack(side=tk.LEFT, fill=tk.X, expand=True,
                                padx=(10, 0), ipady=8)
        
        # Quick amount buttons
        quick_frame = tk.Frame(card, bg=self.colors["card"])
        quick_frame.pack(fill=tk.X, padx=40, pady=10)
        
        for amt in [500, 1000, 2000, 5000]:
            btn = tk.Button(quick_frame, text=f"Rs. {amt}", font=self.font_small,
                           bg=self.colors["secondary"], fg="white",
                           relief=tk.FLAT, cursor="hand2",
                           command=lambda a=amt: self.withdraw_entry.delete(0, tk.END) or
                                                self.withdraw_entry.insert(0, str(a)))
            btn.pack(side=tk.LEFT, padx=3, expand=True, fill=tk.X, ipady=5)
        
        # Withdraw button
        tk.Button(card, text="WITHDRAW", font=self.font_btn,
                 bg=self.colors["success"], fg="white",
                 relief=tk.FLAT, cursor="hand2",
                 activebackground="#1e7e34",
                 activeforeground="white",
                 command=self.process_withdraw).pack(fill=tk.X, padx=40, pady=20, ipady=10)
    
    def create_deposit_screen(self):
        frame = tk.Frame(self.root, bg=self.colors["bg"])
        frame.place(relwidth=1, relheight=1)
        self.frames["deposit"] = frame
        
        self.create_header(frame, "CASH DEPOSIT", True,
                          lambda: self.show_frame("main_menu"))
        
        card = tk.Frame(frame, bg=self.colors["card"], relief=tk.RAISED, bd=2)
        card.pack(padx=30, pady=20, fill=tk.BOTH, expand=True)
        
        tk.Label(card, text="Enter Deposit Amount",
                font=self.font_heading, bg=self.colors["card"],
                fg=self.colors["primary"]).pack(pady=20)
        
        amt_frame = tk.Frame(card, bg=self.colors["card"])
        amt_frame.pack(fill=tk.X, padx=40, pady=20)
        
        tk.Label(amt_frame, text="Rs.", font=self.font_heading,
                bg=self.colors["card"], fg=self.colors["text_dark"]).pack(side=tk.LEFT)
        
        self.deposit_entry = tk.Entry(amt_frame, font=self.font_big,
                                     relief=tk.SOLID, bd=1, justify="center")
        self.deposit_entry.pack(side=tk.LEFT, fill=tk.X, expand=True,
                               padx=(10, 0), ipady=8)
        
        tk.Button(card, text="DEPOSIT", font=self.font_btn,
                 bg=self.colors["warning"], fg="white",
                 relief=tk.FLAT, cursor="hand2",
                 activebackground="#e8590c",
                 activeforeground="white",
                 command=self.process_deposit).pack(fill=tk.X, padx=40, pady=20, ipady=10)
    
    def create_balance_screen(self):
        frame = tk.Frame(self.root, bg=self.colors["bg"])
        frame.place(relwidth=1, relheight=1)
        self.frames["balance"] = frame
        
        self.create_header(frame, "BALANCE INQUIRY", True,
                          lambda: self.show_frame("main_menu"))
        
        card = tk.Frame(frame, bg=self.colors["card"], relief=tk.RAISED, bd=2)
        card.pack(padx=30, pady=30, fill=tk.BOTH, expand=True)
        
        tk.Label(card, text="Available Balance", font=self.font_heading,
                bg=self.colors["card"], fg=self.colors["primary"]).pack(pady=(30, 10))
        
        self.balance_display = tk.Label(card, text="Rs. 0.00", font=("Arial", 36, "bold"),
                                       bg=self.colors["card"],
                                       fg=self.colors["success"])
        self.balance_display.pack(pady=20)
        
        self.account_info_lbl = tk.Label(card, text="", font=self.font_normal,
                                        bg=self.colors["card"],
                                        fg=self.colors["text_light"])
        self.account_info_lbl.pack(pady=10)
        
        tk.Button(card, text="BACK TO MENU", font=self.font_btn,
                 bg=self.colors["secondary"], fg="white",
                 relief=tk.FLAT, cursor="hand2",
                 command=lambda: self.show_frame("main_menu")).pack(fill=tk.X, padx=40, pady=30, ipady=10)
    
    def create_pin_change_screen(self):
        frame = tk.Frame(self.root, bg=self.colors["bg"])
        frame.place(relwidth=1, relheight=1)
        self.frames["pin_change"] = frame
        
        self.create_header(frame, "CHANGE PIN", True,
                          lambda: self.show_frame("main_menu"))
        
        card = tk.Frame(frame, bg=self.colors["card"], relief=tk.RAISED, bd=2)
        card.pack(padx=30, pady=20, fill=tk.BOTH, expand=True)
        
        tk.Label(card, text="Update Your PIN", font=self.font_heading,
                bg=self.colors["card"], fg=self.colors["primary"]).pack(pady=20)
        
        fields = [
            ("Current PIN:", "current_pin"),
            ("New PIN (4 digits):", "new_pin"),
            ("Confirm New PIN:", "confirm_pin"),
        ]
        
        self.pin_entries = {}
        for label_text, field_name in fields:
            f = tk.Frame(card, bg=self.colors["card"])
            f.pack(fill=tk.X, padx=40, pady=8)
            tk.Label(f, text=label_text, font=self.font_normal,
                    bg=self.colors["card"], anchor="w").pack(fill=tk.X)
            entry = tk.Entry(f, font=self.font_normal, relief=tk.SOLID,
                            bd=1, show="*", justify="center")
            entry.pack(fill=tk.X, pady=(3, 0), ipady=6)
            self.pin_entries[field_name] = entry
        
        tk.Button(card, text="UPDATE PIN", font=self.font_btn,
                 bg=self.colors["primary"], fg="white",
                 relief=tk.FLAT, cursor="hand2",
                 command=self.process_pin_change).pack(fill=tk.X, padx=40, pady=20, ipady=10)
    
    def create_history_screen(self):
        frame = tk.Frame(self.root, bg=self.colors["bg"])
        frame.place(relwidth=1, relheight=1)
        self.frames["history"] = frame
        
        self.create_header(frame, "TRANSACTION HISTORY", True,
                          lambda: self.show_frame("main_menu"))
        
        tree_frame = tk.Frame(frame, bg=self.colors["card"], relief=tk.RAISED, bd=2)
        tree_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("History.Treeview", font=self.font_small, rowheight=28,
                       background="white", fieldbackground="white")
        style.configure("History.Treeview.Heading", font=self.font_sub,
                       background="#ecf0f1", foreground="#2c3e50")
        style.map("History.Treeview", background=[("selected", "#3498db")],
                 foreground=[("selected", "white")])
        
        columns = ("date", "type", "description", "amount", "balance")
        self.history_tree = ttk.Treeview(tree_frame, columns=columns,
                                        show="headings", style="History.Treeview")
        
        self.history_tree.heading("date", text="Date & Time")
        self.history_tree.heading("type", text="Type")
        self.history_tree.heading("description", text="Description")
        self.history_tree.heading("amount", text="Amount")
        self.history_tree.heading("balance", text="Balance")
        
        self.history_tree.column("date", width=130, anchor=tk.CENTER)
        self.history_tree.column("type", width=80, anchor=tk.CENTER)
        self.history_tree.column("description", width=150, anchor=tk.W)
        self.history_tree.column("amount", width=90, anchor=tk.E)
        self.history_tree.column("balance", width=90, anchor=tk.E)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                                 command=self.history_tree.yview)
        self.history_tree.configure(yscroll=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        self.history_tree.tag_configure('credit', foreground=self.colors["success"])
        self.history_tree.tag_configure('debit', foreground=self.colors["danger"])
    
    # ============ ACTION METHODS ============
    
    def login(self):
        acc = self.acc_entry.get().strip()
        pin = self.pin_entry.get().strip()
        
        if not acc or not pin:
            messagebox.showwarning("Input Error", "Please enter Account Number and PIN!")
            return
        
        if len(pin) != 4 or not pin.isdigit():
            messagebox.showerror("Input Error", "PIN must be 4 digits!")
            return
        
        try:
            self.c.execute("SELECT * FROM accounts WHERE account_no=? AND pin=?", (acc, pin))
            row = self.c.fetchone()
            
            if row:
                self.current_account = row[0]
                self.current_name = row[2]
                self.current_balance = row[3]
                
                # Log transaction
                self.log_transaction("LOGIN", 0, self.current_balance, "Login Successful")
                
                # Clear entries
                self.acc_entry.delete(0, tk.END)
                self.pin_entry.delete(0, tk.END)
                
                self.show_frame("main_menu")
            else:
                messagebox.showerror("Login Failed", "Invalid Account Number or PIN!")
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {e}")
    
    def logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            self.current_account = None
            self.current_balance = 0.0
            self.current_name = ""
            self.show_frame("login")
    
    def update_status_bar(self):
        if self.current_account:
            self.welcome_lbl.config(text=f"Welcome, {self.current_name} | A/C: {self.current_account}")
            self.balance_lbl.config(text=f"Balance: Rs. {self.current_balance:,.2f}")
    
    def refresh_balance(self):
        self.balance_display.config(text=f"Rs. {self.current_balance:,.2f}")
        self.account_info_lbl.config(
            text=f"Account: {self.current_account} | Name: {self.current_name}")
    
    def process_withdraw(self):
        amt_str = self.withdraw_entry.get().strip()
        if not amt_str:
            messagebox.showwarning("Input Error", "Please enter amount!")
            return
        
        try:
            amount = float(amt_str)
        except ValueError:
            messagebox.showerror("Input Error", "Invalid amount!")
            return
        
        if amount <= 0:
            messagebox.showerror("Input Error", "Amount must be greater than 0!")
            return
        
        if amount % 100 != 0:
            messagebox.showerror("Input Error", "Amount must be in multiples of 100!")
            return
        
        if amount > self.current_balance:
            messagebox.showerror("Insufficient Funds",
                                f"You don't have enough balance!\nAvailable: Rs. {self.current_balance:,.2f}")
            return
        
        if amount > 25000:
            messagebox.showerror("Limit Exceeded",
                                "Daily withdrawal limit is Rs. 25,000!")
            return
        
        confirm = messagebox.askyesno("Confirm Withdrawal",
                                     f"Withdraw Rs. {amount:,.2f}?\nCurrent Balance: Rs. {self.current_balance:,.2f}")
        if not confirm:
            return
        
        try:
            self.current_balance -= amount
            self.c.execute("UPDATE accounts SET balance=? WHERE account_no=?",
                          (self.current_balance, self.current_account))
            self.log_transaction("DEBIT", amount, self.current_balance, "Cash Withdrawal")
            self.conn.commit()
            
            self.withdraw_entry.delete(0, tk.END)
            messagebox.showinfo("Success",
                               f"Rs. {amount:,.2f} withdrawn successfully!\nNew Balance: Rs. {self.current_balance:,.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"Withdrawal failed: {e}")
    
    def process_deposit(self):
        amt_str = self.deposit_entry.get().strip()
        if not amt_str:
            messagebox.showwarning("Input Error", "Please enter amount!")
            return
        
        try:
            amount = float(amt_str)
        except ValueError:
            messagebox.showerror("Input Error", "Invalid amount!")
            return
        
        if amount <= 0:
            messagebox.showerror("Input Error", "Amount must be greater than 0!")
            return
        
        if amount > 100000:
            messagebox.showerror("Limit Exceeded",
                                "Maximum deposit amount is Rs. 1,00,000 at a time!")
            return
        
        confirm = messagebox.askyesno("Confirm Deposit",
                                     f"Deposit Rs. {amount:,.2f}?")
        if not confirm:
            return
        
        try:
            self.current_balance += amount
            self.c.execute("UPDATE accounts SET balance=? WHERE account_no=?",
                          (self.current_balance, self.current_account))
            self.log_transaction("CREDIT", amount, self.current_balance, "Cash Deposit")
            self.conn.commit()
            
            self.deposit_entry.delete(0, tk.END)
            messagebox.showinfo("Success",
                               f"Rs. {amount:,.2f} deposited successfully!\nNew Balance: Rs. {self.current_balance:,.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"Deposit failed: {e}")
    
    def process_pin_change(self):
        current = self.pin_entries["current_pin"].get().strip()
        new_pin = self.pin_entries["new_pin"].get().strip()
        confirm = self.pin_entries["confirm_pin"].get().strip()
        
        if not current or not new_pin or not confirm:
            messagebox.showwarning("Input Error", "Please fill all fields!")
            return
        
        if len(new_pin) != 4 or not new_pin.isdigit():
            messagebox.showerror("Input Error", "New PIN must be 4 digits!")
            return
        
        if new_pin != confirm:
            messagebox.showerror("Input Error", "New PIN and Confirm PIN do not match!")
            return
        
        if current == new_pin:
            messagebox.showwarning("Input Error", "New PIN must be different from current PIN!")
            return
        
        # Verify current PIN
        self.c.execute("SELECT pin FROM accounts WHERE account_no=?", (self.current_account,))
        row = self.c.fetchone()
        if row[0] != current:
            messagebox.showerror("Error", "Current PIN is incorrect!")
            return
        
        try:
            self.c.execute("UPDATE accounts SET pin=? WHERE account_no=?",
                          (new_pin, self.current_account))
            self.log_transaction("PIN_CHANGE", 0, self.current_balance, "PIN Changed")
            self.conn.commit()
            
            for e in self.pin_entries.values():
                e.delete(0, tk.END)
            
            messagebox.showinfo("Success", "PIN changed successfully!\nPlease use new PIN for next login.")
            self.show_frame("main_menu")
        except Exception as e:
            messagebox.showerror("Error", f"PIN change failed: {e}")
    
    def refresh_history(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        try:
            self.c.execute("SELECT date, type, description, amount, balance_after "
                          "FROM transactions WHERE account_no=? ORDER BY id DESC LIMIT 50",
                          (self.current_account,))
            rows = self.c.fetchall()
            
            for row in rows:
                date_str, typ, desc, amt, bal = row
                amt_display = f"Rs. {amt:,.2f}" if amt > 0 else "-"
                tag = 'credit' if typ == 'CREDIT' else 'debit'
                self.history_tree.insert("", tk.END,
                                        values=(date_str, typ, desc, amt_display, f"Rs. {bal:,.2f}"),
                                        tags=(tag,))
            
            if not rows:
                messagebox.showinfo("Info", "No transactions found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history: {e}")
    
    def log_transaction(self, typ, amount, balance_after, description):
        try:
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.c.execute("INSERT INTO transactions (account_no, type, amount, balance_after, date, description) "
                          "VALUES (?, ?, ?, ?, ?, ?)",
                          (self.current_account, typ, amount, balance_after, date_str, description))
            self.conn.commit()
        except Exception as e:
            print(f"Transaction log error: {e}")
    
    def on_close(self):
        try:
            self.conn.close()
        except:
            pass
        self.root.destroy()


if __name__ == "__main__":
    try:
        root = tk.Tk()
        # Center window on screen
        root.update_idletasks()
        width = 500
        height = 650
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        app = ATMApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")