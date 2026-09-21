import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random
from datetime import datetime

DATA_FILE = "bank_data.json"

class BankApp:
    def __init__(self):
        self.data = self.load_data()
        self.current_user = None
        
        # Main Window
        self.root = tk.Tk()
        self.root.title("🏦 Python Bank System - Professional")
        self.root.geometry("1000x650")
        self.root.configure(bg="#1e1e2e")
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        # Style configuration
        self.setup_styles()
        
        # Show login screen
        self.show_login_screen()
        
    def setup_styles(self):
        """Setup ttk styles for professional look."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Button style
        style.configure('Primary.TButton', 
                       font=('Segoe UI', 11, 'bold'),
                       background='#4a9eff',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 10))
        style.map('Primary.TButton',
                 background=[('active', '#3a8eef'), ('pressed', '#2a7edf')])
        
        # Entry style
        style.configure('Custom.TEntry',
                       font=('Segoe UI', 11),
                       padding=8)
        
        # Label style
        style.configure('Title.TLabel',
                       font=('Segoe UI', 24, 'bold'),
                       background='#1e1e2e',
                       foreground='#ffffff')
        
        style.configure('Header.TLabel',
                       font=('Segoe UI', 16, 'bold'),
                       background='#1e1e2e',
                       foreground='#ffffff')
        
        style.configure('Body.TLabel',
                       font=('Segoe UI', 11),
                       background='#1e1e2e',
                       foreground='#cccccc')
        
        style.configure('Balance.TLabel',
                       font=('Segoe UI', 36, 'bold'),
                       background='#1e1e2e',
                       foreground='#4ade80')
    
    def load_data(self):
        """Load data from JSON file safely."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if isinstance(data, dict):
                        return data
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def save_data(self):
        """Save data to JSON file safely."""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)
        except IOError as e:
            messagebox.showerror("Error", f"Could not save data: {e}")
    
    def generate_acc_no(self):
        """Generate unique 8-digit account number."""
        while True:
            acc_no = str(random.randint(10000000, 99999999))
            if acc_no not in self.data:
                return acc_no
    
    def clear_window(self):
        """Clear all widgets from window."""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    # ============ LOGIN SCREEN ============
    def show_login_screen(self):
        self.clear_window()
        
        # Main container
        container = tk.Frame(self.root, bg="#1e1e2e")
        container.pack(expand=True, fill='both', padx=50, pady=30)
        
        # Title
        title_label = tk.Label(container, text="🏦 PYTHON BANK SYSTEM",
                              font=('Segoe UI', 28, 'bold'),
                              bg="#1e1e2e", fg="#4a9eff")
        title_label.pack(pady=(0, 40))
        
        # Login Frame
        login_frame = tk.Frame(container, bg="#2a2a3e", bd=0, relief='flat')
        login_frame.pack(pady=20, padx=20)
        
        # Add padding inside frame
        inner_frame = tk.Frame(login_frame, bg="#2a2a3e")
        inner_frame.pack(padx=40, pady=30)
        
        # Account Number
        tk.Label(inner_frame, text="Account Number",
                font=('Segoe UI', 11, 'bold'),
                bg="#2a2a3e", fg="#ffffff", anchor='w').pack(fill='x', pady=(0, 5))
        
        self.acc_entry = tk.Entry(inner_frame, font=('Segoe UI', 12),
                                 bg="#1e1e2e", fg="#ffffff",
                                 insertbackground="#ffffff",
                                 relief='flat', bd=0)
        self.acc_entry.pack(fill='x', ipady=8, pady=(0, 20))
        
        # PIN
        tk.Label(inner_frame, text="PIN",
                font=('Segoe UI', 11, 'bold'),
                bg="#2a2a3e", fg="#ffffff", anchor='w').pack(fill='x', pady=(0, 5))
        
        self.pin_entry = tk.Entry(inner_frame, font=('Segoe UI', 12),
                                 bg="#1e1e2e", fg="#ffffff",
                                 insertbackground="#ffffff",
                                 show="*", relief='flat', bd=0)
        self.pin_entry.pack(fill='x', ipady=8, pady=(0, 25))
        
        # Buttons Frame
        btn_frame = tk.Frame(inner_frame, bg="#2a2a3e")
        btn_frame.pack(fill='x', pady=10)
        
        login_btn = tk.Button(btn_frame, text="Login",
                             font=('Segoe UI', 11, 'bold'),
                             bg="#4a9eff", fg="#ffffff",
                             activebackground="#3a8eef",
                             activeforeground="#ffffff",
                             relief='flat', bd=0, cursor='hand2',
                             command=self.login)
        login_btn.pack(side='left', fill='x', expand=True, padx=(0, 5), ipady=8)
        
        signup_btn = tk.Button(btn_frame, text="Sign Up",
                              font=('Segoe UI', 11, 'bold'),
                              bg="#6b7280", fg="#ffffff",
                              activebackground="#5b6270",
                              activeforeground="#ffffff",
                              relief='flat', bd=0, cursor='hand2',
                              command=self.show_signup_screen)
        signup_btn.pack(side='left', fill='x', expand=True, padx=(5, 0), ipady=8)
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.login())
    
    # ============ SIGNUP SCREEN ============
    def show_signup_screen(self):
        self.clear_window()
        
        # Main container
        container = tk.Frame(self.root, bg="#1e1e2e")
        container.pack(expand=True, fill='both', padx=50, pady=30)
        
        # Title
        tk.Label(container, text="📝 CREATE NEW ACCOUNT",
                font=('Segoe UI', 24, 'bold'),
                bg="#1e1e2e", fg="#4a9eff").pack(pady=(0, 30))
        
        # Signup Frame
        signup_frame = tk.Frame(container, bg="#2a2a3e")
        signup_frame.pack(pady=20)
        
        inner_frame = tk.Frame(signup_frame, bg="#2a2a3e")
        inner_frame.pack(padx=40, pady=30)
        
        # Name
        tk.Label(inner_frame, text="Full Name",
                font=('Segoe UI', 11, 'bold'),
                bg="#2a2a3e", fg="#ffffff", anchor='w').pack(fill='x', pady=(0, 5))
        
        self.name_entry = tk.Entry(inner_frame, font=('Segoe UI', 12),
                                  bg="#1e1e2e", fg="#ffffff",
                                  insertbackground="#ffffff",
                                  relief='flat', bd=0)
        self.name_entry.pack(fill='x', ipady=8, pady=(0, 20))
        
        # PIN
        tk.Label(inner_frame, text="Set PIN (4 digits)",
                font=('Segoe UI', 11, 'bold'),
                bg="#2a2a3e", fg="#ffffff", anchor='w').pack(fill='x', pady=(0, 5))
        
        self.new_pin_entry = tk.Entry(inner_frame, font=('Segoe UI', 12),
                                     bg="#1e1e2e", fg="#ffffff",
                                     insertbackground="#ffffff",
                                     show="*", relief='flat', bd=0)
        self.new_pin_entry.pack(fill='x', ipady=8, pady=(0, 20))
        
        # Initial Deposit
        tk.Label(inner_frame, text="Initial Deposit (₹)",
                font=('Segoe UI', 11, 'bold'),
                bg="#2a2a3e", fg="#ffffff", anchor='w').pack(fill='x', pady=(0, 5))
        
        self.deposit_entry = tk.Entry(inner_frame, font=('Segoe UI', 12),
                                     bg="#1e1e2e", fg="#ffffff",
                                     insertbackground="#ffffff",
                                     relief='flat', bd=0)
        self.deposit_entry.pack(fill='x', ipady=8, pady=(0, 25))
        
        # Buttons
        btn_frame = tk.Frame(inner_frame, bg="#2a2a3e")
        btn_frame.pack(fill='x', pady=10)
        
        create_btn = tk.Button(btn_frame, text="Create Account",
                              font=('Segoe UI', 11, 'bold'),
                              bg="#4ade80", fg="#1e1e2e",
                              activebackground="#3ade70",
                              activeforeground="#1e1e2e",
                              relief='flat', bd=0, cursor='hand2',
                              command=self.create_account)
        create_btn.pack(side='left', fill='x', expand=True, padx=(0, 5), ipady=8)
        
        back_btn = tk.Button(btn_frame, text="Back to Login",
                            font=('Segoe UI', 11, 'bold'),
                            bg="#6b7280", fg="#ffffff",
                            activebackground="#5b6270",
                            activeforeground="#ffffff",
                            relief='flat', bd=0, cursor='hand2',
                            command=self.show_login_screen)
        back_btn.pack(side='left', fill='x', expand=True, padx=(5, 0), ipady=8)
    
    # ============ LOGIN FUNCTION ============
    def login(self):
        try:
            acc_no = self.acc_entry.get().strip()
            pin = self.pin_entry.get().strip()
            
            if not acc_no or not pin:
                messagebox.showerror("Error", "Please enter Account Number and PIN!")
                return
            
            if acc_no not in self.data:
                messagebox.showerror("Error", "Account not found! Please check your account number.")
                return
            
            if self.data[acc_no]["pin"] != pin:
                messagebox.showerror("Error", "Incorrect PIN! Please try again.")
                return
            
            self.current_user = acc_no
            self.show_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {e}")
    
    # ============ CREATE ACCOUNT FUNCTION ============
    def create_account(self):
        try:
            name = self.name_entry.get().strip()
            pin = self.new_pin_entry.get().strip()
            deposit_str = self.deposit_entry.get().strip()
            
            # Validation
            if not name:
                messagebox.showerror("Error", "Name cannot be empty!")
                return
            
            if len(pin) != 4 or not pin.isdigit():
                messagebox.showerror("Error", "PIN must be exactly 4 digits!")
                return
            
            if not deposit_str:
                messagebox.showerror("Error", "Please enter initial deposit amount!")
                return
            
            try:
                deposit = float(deposit_str)
                if deposit < 0:
                    messagebox.showerror("Error", "Deposit amount cannot be negative!")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid deposit amount! Please enter numbers only.")
                return
            
            # Create account
            acc_no = self.generate_acc_no()
            self.data[acc_no] = {
                "name": name,
                "pin": pin,
                "balance": deposit,
                "transactions": [
                    {
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "Initial Deposit",
                        "amount": deposit
                    }
                ]
            }
            self.save_data()
            
            messagebox.showinfo("Success", 
                              f"✅ Account Created Successfully!\n\n"
                              f"Account Number: {acc_no}\n"
                              f"PIN: {pin}\n"
                              f"Initial Balance: ₹{deposit:.2f}\n\n"
                              f"Please remember your credentials!")
            self.show_login_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Account creation failed: {e}")
    
    # ============ DASHBOARD ============
    def show_dashboard(self):
        self.clear_window()
        
        user_data = self.data[self.current_user]
        
        # Header
        header = tk.Frame(self.root, bg="#2a2a3e", height=80)
        header.pack(fill='x', padx=0, pady=0)
        header.pack_propagate(False)
        
        tk.Label(header, text=f"👤 Welcome, {user_data['name']}",
                font=('Segoe UI', 18, 'bold'),
                bg="#2a2a3e", fg="#ffffff").pack(side='left', padx=30, pady=20)
        
        logout_btn = tk.Button(header, text="Logout",
                              font=('Segoe UI', 10, 'bold'),
                              bg="#ef4444", fg="#ffffff",
                              activebackground="#df3434",
                              activeforeground="#ffffff",
                              relief='flat', bd=0, cursor='hand2',
                              command=self.logout)
        logout_btn.pack(side='right', padx=30, pady=20, ipady=5, ipadx=15)
        
        # Account Info
        info_frame = tk.Frame(self.root, bg="#1e1e2e")
        info_frame.pack(fill='x', padx=30, pady=10)
        
        tk.Label(info_frame, text=f"Account Number: {self.current_user}",
                font=('Segoe UI', 11),
                bg="#1e1e2e", fg="#cccccc").pack(side='left', padx=10)
        
        # Balance Card
        balance_frame = tk.Frame(self.root, bg="#2a2a3e", height=180)
        balance_frame.pack(fill='x', padx=30, pady=20)
        balance_frame.pack_propagate(False)
        
        tk.Label(balance_frame, text="Current Balance",
                font=('Segoe UI', 14),
                bg="#2a2a3e", fg="#cccccc").pack(pady=(30, 5))
        
        tk.Label(balance_frame, text=f"₹{user_data['balance']:.2f}",
                font=('Segoe UI', 42, 'bold'),
                bg="#2a2a3e", fg="#4ade80").pack(pady=5)
        
        # Action Buttons
        action_frame = tk.Frame(self.root, bg="#1e1e2e")
        action_frame.pack(fill='x', padx=30, pady=20)
        
        # Deposit Button
        deposit_btn = tk.Button(action_frame, text="💰 Deposit Money",
                               font=('Segoe UI', 13, 'bold'),
                               bg="#4ade80", fg="#1e1e2e",
                               activebackground="#3ade70",
                               activeforeground="#1e1e2e",
                               relief='flat', bd=0, cursor='hand2',
                               command=self.show_deposit_screen)
        deposit_btn.pack(side='left', fill='x', expand=True, padx=10, ipady=15)
        
        # Withdraw Button
        withdraw_btn = tk.Button(action_frame, text="💸 Withdraw Money",
                                font=('Segoe UI', 13, 'bold'),
                                bg="#f59e0b", fg="#1e1e2e",
                                activebackground="#e58e0b",
                                activeforeground="#1e1e2e",
                                relief='flat', bd=0, cursor='hand2',
                                command=self.show_withdraw_screen)
        withdraw_btn.pack(side='left', fill='x', expand=True, padx=10, ipady=15)
        
        # History Button
        history_btn = tk.Button(action_frame, text="📊 Transaction History",
                               font=('Segoe UI', 13, 'bold'),
                               bg="#8b5cf6", fg="#ffffff",
                               activebackground="#7b4cf6",
                               activeforeground="#ffffff",
                               relief='flat', bd=0, cursor='hand2',
                               command=self.show_history_screen)
        history_btn.pack(side='left', fill='x', expand=True, padx=10, ipady=15)
    
    # ============ DEPOSIT SCREEN ============
    def show_deposit_screen(self):
        self.clear_window()
        
        container = tk.Frame(self.root, bg="#1e1e2e")
        container.pack(expand=True, fill='both', padx=50, pady=30)
        
        tk.Label(container, text="💰 DEPOSIT MONEY",
                font=('Segoe UI', 24, 'bold'),
                bg="#1e1e2e", fg="#4ade80").pack(pady=(0, 30))
        
        frame = tk.Frame(container, bg="#2a2a3e")
        frame.pack(pady=20)
        
        inner_frame = tk.Frame(frame, bg="#2a2a3e")
        inner_frame.pack(padx=40, pady=30)
        
        tk.Label(inner_frame, text="Enter Amount (₹)",
                font=('Segoe UI', 12, 'bold'),
                bg="#2a2a3e", fg="#ffffff").pack(pady=(0, 10))
        
        self.deposit_amount_entry = tk.Entry(inner_frame, font=('Segoe UI', 14),
                                            bg="#1e1e2e", fg="#ffffff",
                                            insertbackground="#ffffff",
                                            relief='flat', bd=0,
                                            justify='center')
        self.deposit_amount_entry.pack(ipady=10, ipadx=50, pady=(0, 25))
        
        btn_frame = tk.Frame(inner_frame, bg="#2a2a3e")
        btn_frame.pack(fill='x', pady=10)
        
        submit_btn = tk.Button(btn_frame, text="Deposit",
                              font=('Segoe UI', 11, 'bold'),
                              bg="#4ade80", fg="#1e1e2e",
                              activebackground="#3ade70",
                              activeforeground="#1e1e2e",
                              relief='flat', bd=0, cursor='hand2',
                              command=self.deposit_money)
        submit_btn.pack(side='left', fill='x', expand=True, padx=(0, 5), ipady=8)
        
        back_btn = tk.Button(btn_frame, text="Back",
                            font=('Segoe UI', 11, 'bold'),
                            bg="#6b7280", fg="#ffffff",
                            activebackground="#5b6270",
                            activeforeground="#ffffff",
                            relief='flat', bd=0, cursor='hand2',
                            command=self.show_dashboard)
        back_btn.pack(side='left', fill='x', expand=True, padx=(5, 0), ipady=8)
    
    def deposit_money(self):
        try:
            amount_str = self.deposit_amount_entry.get().strip()
            
            if not amount_str:
                messagebox.showerror("Error", "Please enter amount!")
                return
            
            try:
                amount = float(amount_str)
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0!")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid amount! Please enter numbers only.")
                return
            
            self.data[self.current_user]["balance"] += amount
            self.data[self.current_user]["transactions"].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "Deposit",
                "amount": amount
            })
            self.save_data()
            
            messagebox.showinfo("Success", f"✅ ₹{amount:.2f} deposited successfully!")
            self.show_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Deposit failed: {e}")
    
    # ============ WITHDRAW SCREEN ============
    def show_withdraw_screen(self):
        self.clear_window()
        
        container = tk.Frame(self.root, bg="#1e1e2e")
        container.pack(expand=True, fill='both', padx=50, pady=30)
        
        tk.Label(container, text="💸 WITHDRAW MONEY",
                font=('Segoe UI', 24, 'bold'),
                bg="#1e1e2e", fg="#f59e0b").pack(pady=(0, 30))
        
        frame = tk.Frame(container, bg="#2a2a3e")
        frame.pack(pady=20)
        
        inner_frame = tk.Frame(frame, bg="#2a2a3e")
        inner_frame.pack(padx=40, pady=30)
        
        tk.Label(inner_frame, text="Enter Amount (₹)",
                font=('Segoe UI', 12, 'bold'),
                bg="#2a2a3e", fg="#ffffff").pack(pady=(0, 10))
        
        self.withdraw_amount_entry = tk.Entry(inner_frame, font=('Segoe UI', 14),
                                             bg="#1e1e2e", fg="#ffffff",
                                             insertbackground="#ffffff",
                                             relief='flat', bd=0,
                                             justify='center')
        self.withdraw_amount_entry.pack(ipady=10, ipadx=50, pady=(0, 25))
        
        btn_frame = tk.Frame(inner_frame, bg="#2a2a3e")
        btn_frame.pack(fill='x', pady=10)
        
        submit_btn = tk.Button(btn_frame, text="Withdraw",
                              font=('Segoe UI', 11, 'bold'),
                              bg="#f59e0b", fg="#1e1e2e",
                              activebackground="#e58e0b",
                              activeforeground="#1e1e2e",
                              relief='flat', bd=0, cursor='hand2',
                              command=self.withdraw_money)
        submit_btn.pack(side='left', fill='x', expand=True, padx=(0, 5), ipady=8)
        
        back_btn = tk.Button(btn_frame, text="Back",
                            font=('Segoe UI', 11, 'bold'),
                            bg="#6b7280", fg="#ffffff",
                            activebackground="#5b6270",
                            activeforeground="#ffffff",
                            relief='flat', bd=0, cursor='hand2',
                            command=self.show_dashboard)
        back_btn.pack(side='left', fill='x', expand=True, padx=(5, 0), ipady=8)
    
    def withdraw_money(self):
        try:
            amount_str = self.withdraw_amount_entry.get().strip()
            
            if not amount_str:
                messagebox.showerror("Error", "Please enter amount!")
                return
            
            try:
                amount = float(amount_str)
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than 0!")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid amount! Please enter numbers only.")
                return
            
            if amount > self.data[self.current_user]["balance"]:
                messagebox.showerror("Error", 
                                   f"❌ Insufficient funds!\n\n"
                                   f"Available Balance: ₹{self.data[self.current_user]['balance']:.2f}\n"
                                   f"Requested Amount: ₹{amount:.2f}")
                return
            
            self.data[self.current_user]["balance"] -= amount
            self.data[self.current_user]["transactions"].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "Withdrawal",
                "amount": amount
            })
            self.save_data()
            
            messagebox.showinfo("Success", f"✅ ₹{amount:.2f} withdrawn successfully!")
            self.show_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Withdrawal failed: {e}")
    
    # ============ TRANSACTION HISTORY ============
    def show_history_screen(self):
        self.clear_window()
        
        # Header
        tk.Label(self.root, text="📊 TRANSACTION HISTORY",
                font=('Segoe UI', 24, 'bold'),
                bg="#1e1e2e", fg="#8b5cf6").pack(pady=20)
        
        # Treeview Frame
        tree_frame = tk.Frame(self.root, bg="#1e1e2e")
        tree_frame.pack(fill='both', expand=True, padx=30, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Treeview
        columns = ('date', 'type', 'amount')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                yscrollcommand=scrollbar.set, height=15)
        
        self.tree.heading('date', text='Date & Time')
        self.tree.heading('type', text='Transaction Type')
        self.tree.heading('amount', text='Amount (₹)')
        
        self.tree.column('date', width=200, anchor='w')
        self.tree.column('type', width=150, anchor='w')
        self.tree.column('amount', width=150, anchor='e')
        
        self.tree.pack(fill='both', expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Insert transactions
        transactions = self.data[self.current_user]["transactions"]
        if transactions:
            for t in reversed(transactions):
                self.tree.insert('', 'end', values=(
                    t['date'],
                    t['type'],
                    f"₹{t['amount']:.2f}"
                ))
        else:
            self.tree.insert('', 'end', values=("No transactions", "-", "-"))
        
        # Back button
        back_btn = tk.Button(self.root, text="Back to Dashboard",
                            font=('Segoe UI', 11, 'bold'),
                            bg="#6b7280", fg="#ffffff",
                            activebackground="#5b6270",
                            activeforeground="#ffffff",
                            relief='flat', bd=0, cursor='hand2',
                            command=self.show_dashboard)
        back_btn.pack(pady=20, ipady=8, ipadx=20)
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.current_user = None
            self.show_login_screen()
    
    def run(self):
        self.root.mainloop()

# Run the app
if __name__ == "__main__":
    try:
        app = BankApp()
        app.run()
    except Exception as e:
        print(f"Fatal Error: {e}")
        messagebox.showerror("Fatal Error", f"Application failed to start: {e}")