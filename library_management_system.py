import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
import sys
from datetime import datetime, timedelta

class LibraryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System - Professional Edition")
        self.root.geometry("1200x750")
        self.root.minsize(1100, 700)
        self.root.configure(bg="#f5f7fa")
        
        # Color scheme
        self.colors = {
            "primary": "#2c5f8d",
            "secondary": "#4a90e2",
            "accent": "#f39c12",
            "success": "#27ae60",
            "danger": "#e74c3c",
            "warning": "#f39c12",
            "info": "#3498db",
            "bg": "#f5f7fa",
            "card": "#ffffff",
            "text_dark": "#2c3e50",
            "text_light": "#7f8c8d",
            "border": "#dfe6e9",
        }
        
        # Fonts
        self.font_title = ("Arial", 24, "bold")
        self.font_heading = ("Arial", 16, "bold")
        self.font_sub = ("Arial", 13, "bold")
        self.font_normal = ("Arial", 11)
        self.font_small = ("Arial", 10)
        self.font_btn = ("Arial", 11, "bold")
        self.font_big = ("Arial", 32, "bold")
        
        # Database setup
        self.setup_database()
        
        # Create main interface
        self.create_interface()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_database(self):
        try:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'library.db')
            self.conn = sqlite3.connect(db_path)
            self.c = self.conn.cursor()
            
            # Books table
            self.c.execute('''CREATE TABLE IF NOT EXISTS books
                              (book_id TEXT PRIMARY KEY, title TEXT, author TEXT, 
                               isbn TEXT, category TEXT, total_copies INTEGER, 
                               available_copies INTEGER)''')
            
            # Members table
            self.c.execute('''CREATE TABLE IF NOT EXISTS members
                              (member_id TEXT PRIMARY KEY, name TEXT, contact TEXT, 
                               email TEXT, membership_date TEXT)''')
            
            # Transactions table
            self.c.execute('''CREATE TABLE IF NOT EXISTS transactions
                              (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                               book_id TEXT, member_id TEXT, issue_date TEXT,
                               due_date TEXT, return_date TEXT, fine REAL, status TEXT)''')
            
            self.conn.commit()
            
            # Insert sample data if empty
            self.c.execute("SELECT COUNT(*) FROM books")
            if self.c.fetchone()[0] == 0:
                sample_books = [
                    ('B001', 'Python Programming', 'John Smith', '978-1234567890', 'Programming', 5, 5),
                    ('B002', 'Data Structures', 'Jane Doe', '978-0987654321', 'Computer Science', 3, 3),
                    ('B003', 'Database Systems', 'Bob Johnson', '978-1122334455', 'Computer Science', 4, 4),
                ]
                self.c.executemany("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?)", sample_books)
                
                sample_members = [
                    ('M001', 'Rahul Kumar', '9876543210', 'rahul@email.com', '2024-01-15'),
                    ('M002', 'Priya Sharma', '9876543211', 'priya@email.com', '2024-02-20'),
                ]
                self.c.executemany("INSERT INTO members VALUES (?, ?, ?, ?, ?)", sample_members)
                self.conn.commit()
                
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to setup database: {e}")
            sys.exit(1)
    
    def create_interface(self):
        # Header
        header = tk.Frame(self.root, bg=self.colors["primary"], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_lbl = tk.Label(header, text="LIBRARY MANAGEMENT SYSTEM",
                            font=self.font_title, bg=self.colors["primary"], fg="white")
        title_lbl.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Current date/time
        self.datetime_lbl = tk.Label(header, text="", font=self.font_small,
                                    bg=self.colors["primary"], fg="white")
        self.datetime_lbl.pack(side=tk.RIGHT, padx=20, pady=15)
        self.update_datetime()
        
        # Main container with tabs
        main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook (tabs)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=self.colors["bg"])
        style.configure("TNotebook.Tab", font=self.font_sub, padding=[15, 8])
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_books_tab()
        self.create_members_tab()
        self.create_issue_tab()
        self.create_return_tab()
        self.create_transactions_tab()
    
    def create_dashboard_tab(self):
        frame = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(frame, text="  Dashboard  ")
        
        # Stats cards
        stats_frame = tk.Frame(frame, bg=self.colors["bg"])
        stats_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Get counts
        self.c.execute("SELECT COUNT(*) FROM books")
        total_books = self.c.fetchone()[0]
        
        self.c.execute("SELECT SUM(available_copies) FROM books")
        available_books = self.c.fetchone()[0] or 0
        
        self.c.execute("SELECT COUNT(*) FROM members")
        total_members = self.c.fetchone()[0]
        
        self.c.execute("SELECT COUNT(*) FROM transactions WHERE status='ISSUED'")
        issued_books = self.c.fetchone()[0]
        
        stats = [
            ("Total Books", total_books, self.colors["primary"]),
            ("Available Copies", available_books, self.colors["success"]),
            ("Total Members", total_members, self.colors["info"]),
            ("Books Issued", issued_books, self.colors["warning"]),
        ]
        
        for i, (label, value, color) in enumerate(stats):
            card = tk.Frame(stats_frame, bg=self.colors["card"], relief=tk.RAISED, bd=2)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)
            
            tk.Label(card, text=label, font=self.font_sub,
                    bg=self.colors["card"], fg=self.colors["text_light"]).pack(pady=(15, 5))
            tk.Label(card, text=str(value), font=self.font_big,
                    bg=self.colors["card"], fg=color).pack(pady=(0, 15))
        
        # Recent activity
        activity_frame = tk.Frame(frame, bg=self.colors["card"], relief=tk.RAISED, bd=2)
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(activity_frame, text="Recent Transactions", font=self.font_heading,
                bg=self.colors["card"], fg=self.colors["primary"]).pack(pady=15)
        
        tree_frame = tk.Frame(activity_frame, bg=self.colors["card"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        style = ttk.Style()
        style.configure("Dashboard.Treeview", font=self.font_small, rowheight=28)
        style.configure("Dashboard.Treeview.Heading", font=self.font_sub)
        
        columns = ("id", "book", "member", "issue_date", "status")
        self.dashboard_tree = ttk.Treeview(tree_frame, columns=columns,
                                          show="headings", style="Dashboard.Treeview")
        
        self.dashboard_tree.heading("id", text="Trans. ID")
        self.dashboard_tree.heading("book", text="Book ID")
        self.dashboard_tree.heading("member", text="Member ID")
        self.dashboard_tree.heading("issue_date", text="Issue Date")
        self.dashboard_tree.heading("status", text="Status")
        
        for col in columns:
            self.dashboard_tree.column(col, width=150, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
                                 command=self.dashboard_tree.yview)
        self.dashboard_tree.configure(yscroll=scrollbar.set)
        
        self.dashboard_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_dashboard()
    
    def create_books_tab(self):
        frame = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(frame, text="  Books  ")
        
        # Top frame for form and buttons
        top_frame = tk.Frame(frame, bg=self.colors["card"], relief=tk.RAISED, bd=2)
        top_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(top_frame, text="Book Management", font=self.font_heading,
                bg=self.colors["card"], fg=self.colors["primary"]).pack(pady=10)
        
        # Form
        form_frame = tk.Frame(top_frame, bg=self.colors["card"])
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        fields = [
            ("Book ID:", "book_id"),
            ("Title:", "title"),
            ("Author:", "author"),
            ("ISBN:", "isbn"),
            ("Category:", "category"),
            ("Total Copies:", "total_copies"),
        ]
        
        self.book_entries = {}
        for i, (label_text, field_name) in enumerate(fields):
            row = i // 3
            col = (i % 3) * 2
            
            tk.Label(form_frame, text=label_text, font=self.font_normal,
                    bg=self.colors["card"], anchor="w").grid(row=row, column=col,
                                                            padx=5, pady=5, sticky="w")
            
            entry = tk.Entry(form_frame, font=self.font_normal, relief=tk.SOLID, bd=1)
            entry.grid(row=row, column=col+1, padx=5, pady=5, sticky="ew")
            self.book_entries[field_name] = entry
        
        for i in range(3):
            form_frame.grid_columnconfigure(i*2+1, weight=1)
        
        # Buttons
        btn_frame = tk.Frame(top_frame, bg=self.colors["card"])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        btn_style = {"font": self.font_btn, "fg": "white", "relief": tk.FLAT,
                     "cursor": "hand2", "activeforeground": "white"}
        
        tk.Button(btn_frame, text="ADD BOOK", bg=self.colors["success"],
                 command=self.add_book, **btn_style).pack(side=tk.LEFT, padx=5, ipady=6, ipadx=15)
        tk.Button(btn_frame, text="UPDATE", bg=self.colors["info"],
                 command=self.update_book, **btn_style).pack(side=tk.LEFT, padx=5, ipady=6, ipadx=15)
        tk.Button(btn_frame, text="DELETE", bg=self.colors["danger"],
                 command=self.delete_book, **btn_style).pack(side=tk.LEFT, padx=5, ipady=6, ipadx=15)
        tk.Button(btn_frame, text="CLEAR", bg=self.colors["text_light"],
                 command=self.clear_book_form, **btn_style).pack(side=tk.LEFT, padx=5, ipady=6, ipadx=15)
        
        # Search
        search_frame = tk.Frame(top_frame, bg=self.colors["card"])
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(search_frame, text="Search:", font=self.font_normal,
                bg=self.colors["card"]).pack(side=tk.LEFT)
        self.book_search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.book_search_var,
                font=self.font_normal, relief=tk.SOLID, bd=1).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        tk.Button(search_frame, text="Search", bg=self.colors["secondary"],
                 command=self.search_books, **btn_style).pack(side=tk.LEFT, padx=5, ipady=4)
        tk.Button(search_frame, text="Show All", bg=self.colors["primary"],
                 command=self.refresh_books_table, **btn_style).pack(side=tk.LEFT, padx=5, ipady=4)
        
        # Books table
        table_frame = tk.Frame(frame, bg=self.colors["card"], relief=tk.RAISED, bd=2)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        style = ttk.Style()
        style.configure("Books.Treeview", font=self.font_small, rowheight=28)
        style.configure("Books.Treeview.Heading", font=self.font_sub)
        
        columns = ("book_id", "title", "author", "isbn", "category", "total", "available")
        self.books_tree = ttk.Treeview(table_frame, columns=columns,
                                      show="headings", style="Books.Treeview")
        
        self.books_tree.heading("book_id", text="Book ID")
        self.books_tree.heading("title", text="Title")
        self.books_tree.heading("author", text="Author")
        self.books_tree.heading("isbn", text="ISBN")
        self.books_tree.heading("category", text="Category")
        self.books_tree.heading("total", text="Total")
        self.books_tree.heading("available", text="Available")
        
        widths = [80, 200, 150, 120, 120, 80, 80]
        for col, width in zip(columns, widths):
            self.books_tree.column(col, width=width, anchor=tk.CENTER if col in ["book_id", "total", "available"] else tk.W)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                 command=self.books_tree.yview)
        self.books_tree.configure(yscroll=scrollbar.set)
        
        self.books_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        self.books_tree.tag_configure('oddrow', background='#f9f9f9')
        self.books_tree.tag_configure('evenrow', background='#ffffff')
        
        self.books_tree.bind("<ButtonRelease-1>", self.select_book)
        self.refresh_books_table()
    
    def create_members_tab(self):
        frame = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(frame, text="  Members  ")
        
        # Top frame
        top_frame = tk.Frame(frame, bg=self.colors["card"], relief=tk.RAISED, bd=2)
        top_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(top_frame, text="Member Management", font=self.font_heading,
                bg=self.colors["card"], fg=self.colors["primary"]).pack(pady=10)
        
        # Form
        form_frame = tk.Frame(top_frame, bg=self.colors["card"])
        form_frame.pack(fill=tk.X, padx=20, pady=10)
        
        fields = [
            ("Member ID:", "member_id"),
            ("Name:", "name"),
            ("Contact:", "contact"),
            ("Email:", "email"),
        ]
        
        self.member_entries = {}
        for i, (label_text, field_name) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2
            
            tk.Label(form_frame, text=label_text, font=self.font_normal,
                    bg=self.colors["card"], anchor="w").grid(row=row, column=col,
                                                            padx=5, pady=5, sticky="w")
            
            entry = tk.Entry(form_frame, font=self.font_normal, relief=tk.SOLID, bd=1)
            entry.grid(row=row, column=col+1, padx=5, pady=5, sticky="ew")
            self.member_entries[field_name] = entry
        
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)
        
        # Buttons
        btn_frame = tk.Frame(top_frame, bg=self.colors["card"])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        btn_style = {"font": self.font_btn, "fg": "white", "relief": tk.FLAT,
                     "cursor": "hand2", "activeforeground": "white"}
        
        tk.Button(btn_frame, text="ADD MEMBER", bg=self.colors["success"],
                 command=self.add_member, **btn_style).pack(side=tk.LEFT, padx=5, ipady=6, ipadx=15)
        tk.Button(btn_frame, text="UPDATE", bg=self.colors["info"],
                 command=self.update_member, **btn_style).pack(side=tk.LEFT, padx=5, ipady=6, ipadx=15)
        tk.Button(btn_frame, text="DELETE", bg=self.colors["danger"],
                 command=self.delete_member, **btn_style).pack(side=tk.LEFT, padx=5, ipady=6, ipadx=15)
        tk.Button(btn_frame, text="CLEAR", bg=self.colors["text_light"],
                 command=self.clear_member_form, **btn_style).pack(side=tk.LEFT, padx=5, ipady=6, ipadx=15)
        
        # Search
        search_frame = tk.Frame(top_frame, bg=self.colors["card"])
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(search_frame, text="Search:", font=self.font_normal,
                bg=self.colors["card"]).pack(side=tk.LEFT)
        self.member_search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.member_search_var,
                font=self.font_normal, relief=tk.SOLID, bd=1).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        tk.Button(search_frame, text="Search", bg=self.colors["secondary"],
                 command=self.search_members, **btn_style).pack(side=tk.LEFT, padx=5, ipady=4)
        tk.Button(search_frame, text="Show All", bg=self.colors["primary"],
                 command=self.refresh_members_table, **btn_style).pack(side=tk.LEFT, padx=5, ipady=4)
        
        # Members table
        table_frame = tk.Frame(frame, bg=self.colors["card"], relief=tk.RAISED, bd=2)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        style = ttk.Style()
        style.configure("Members.Treeview", font=self.font_small, rowheight=28)
        style.configure("Members.Treeview.Heading", font=self.font_sub)
        
        columns = ("member_id", "name", "contact", "email", "membership_date")
        self.members_tree = ttk.Treeview(table_frame, columns=columns,
                                        show="headings", style="Members.Treeview")
        
        self.members_tree.heading("member_id", text="Member ID")
        self.members_tree.heading("name", text="Name")
        self.members_tree.heading("contact", text="Contact")
        self.members_tree.heading("email", text="Email")
        self.members_tree.heading("membership_date", text="Membership Date")
        
        widths = [100, 200, 150, 200, 150]
        for col, width in zip(columns, widths):
            self.members_tree.column(col, width=width, anchor=tk.CENTER if col == "member_id" else tk.W)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                 command=self.members_tree.yview)
        self.members_tree.configure(yscroll=scrollbar.set)
        
        self.members_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        self.members_tree.tag_configure('oddrow', background='#f9f9f9')
        self.members_tree.tag_configure('evenrow', background='#ffffff')
        
        self.members_tree.bind("<ButtonRelease-1>", self.select_member)
        self.refresh_members_table()
    
    def create_issue_tab(self):
        frame = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(frame, text="  Issue Book  ")
        
        card = tk.Frame(frame, bg=self.colors["card"], relief=tk.RAISED, bd=2)
        card.pack(padx=30, pady=30, fill=tk.BOTH, expand=True)
        
        tk.Label(card, text="Issue Book to Member", font=self.font_heading,
                bg=self.colors["card"], fg=self.colors["primary"]).pack(pady=20)
        
        # Form
        form_frame = tk.Frame(card, bg=self.colors["card"])
        form_frame.pack(fill=tk.X, padx=40, pady=20)
        
        fields = [
            ("Book ID:", "issue_book_id"),
            ("Member ID:", "issue_member_id"),
            ("Due Date (YYYY-MM-DD):", "due_date"),
        ]
        
        self.issue_entries = {}
        for label_text, field_name in fields:
            f = tk.Frame(form_frame, bg=self.colors["card"])
            f.pack(fill=tk.X, pady=10)
            
            tk.Label(f, text=label_text, font=self.font_normal,
                    bg=self.colors["card"], anchor="w").pack(fill=tk.X)
            
            entry = tk.Entry(f, font=self.font_normal, relief=tk.SOLID, bd=1)
            entry.pack(fill=tk.X, pady=(5, 0), ipady=6)
            self.issue_entries[field_name] = entry
        
        # Set default due date (14 days from now)
        default_due = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        self.issue_entries["due_date"].insert(0, default_due)
        
        # Issue button
        btn_style = {"font": self.font_btn, "fg": "white", "relief": tk.FLAT,
                     "cursor": "hand2", "activeforeground": "white"}
        
        tk.Button(card, text="ISSUE BOOK", bg=self.colors["success"],
                 command=self.issue_book, **btn_style).pack(fill=tk.X, padx=40, pady=20, ipady=10)
    
    def create_return_tab(self):
        frame = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(frame, text="  Return Book  ")
        
        card = tk.Frame(frame, bg=self.colors["card"], relief=tk.RAISED, bd=2)
        card.pack(padx=30, pady=30, fill=tk.BOTH, expand=True)
        
        tk.Label(card, text="Return Book", font=self.font_heading,
                bg=self.colors["card"], fg=self.colors["primary"]).pack(pady=20)
        
        # Form
        form_frame = tk.Frame(card, bg=self.colors["card"])
        form_frame.pack(fill=tk.X, padx=40, pady=20)
        
        tk.Label(form_frame, text="Transaction ID:", font=self.font_normal,
                bg=self.colors["card"], anchor="w").pack(fill=tk.X)
        
        self.return_trans_id = tk.Entry(form_frame, font=self.font_normal,
                                       relief=tk.SOLID, bd=1)
        self.return_trans_id.pack(fill=tk.X, pady=(5, 0), ipady=6)
        
        # Info display
        self.return_info_lbl = tk.Label(card, text="", font=self.font_normal,
                                       bg=self.colors["card"], fg=self.colors["text_light"])
        self.return_info_lbl.pack(pady=10)
        
        # Buttons
        btn_style = {"font": self.font_btn, "fg": "white", "relief": tk.FLAT,
                     "cursor": "hand2", "activeforeground": "white"}
        
        tk.Button(card, text="CHECK DETAILS", bg=self.colors["info"],
                 command=self.check_return_details, **btn_style).pack(fill=tk.X, padx=40, pady=10, ipady=8)
        
        tk.Button(card, text="RETURN BOOK", bg=self.colors["warning"],
                 command=self.return_book, **btn_style).pack(fill=tk.X, padx=40, pady=10, ipady=8)
    
    def create_transactions_tab(self):
        frame = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(frame, text="  Transactions  ")
        
        # Search
        search_frame = tk.Frame(frame, bg=self.colors["card"], relief=tk.RAISED, bd=2)
        search_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(search_frame, text="Transaction History", font=self.font_heading,
                bg=self.colors["card"], fg=self.colors["primary"]).pack(pady=10)
        
        filter_frame = tk.Frame(search_frame, bg=self.colors["card"])
        filter_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(filter_frame, text="Filter:", font=self.font_normal,
                bg=self.colors["card"]).pack(side=tk.LEFT)
        
        self.trans_filter_var = tk.StringVar(value="ALL")
        tk.Radiobutton(filter_frame, text="All", variable=self.trans_filter_var,
                      value="ALL", bg=self.colors["card"], font=self.font_normal,
                      command=self.refresh_transactions_table).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(filter_frame, text="Issued", variable=self.trans_filter_var,
                      value="ISSUED", bg=self.colors["card"], font=self.font_normal,
                      command=self.refresh_transactions_table).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(filter_frame, text="Returned", variable=self.trans_filter_var,
                      value="RETURNED", bg=self.colors["card"], font=self.font_normal,
                      command=self.refresh_transactions_table).pack(side=tk.LEFT, padx=10)
        
        # Table
        table_frame = tk.Frame(frame, bg=self.colors["card"], relief=tk.RAISED, bd=2)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        style = ttk.Style()
        style.configure("Trans.Treeview", font=self.font_small, rowheight=28)
        style.configure("Trans.Treeview.Heading", font=self.font_sub)
        
        columns = ("trans_id", "book_id", "member_id", "issue_date", "due_date", "return_date", "fine", "status")
        self.trans_tree = ttk.Treeview(table_frame, columns=columns,
                                      show="headings", style="Trans.Treeview")
        
        self.trans_tree.heading("trans_id", text="Trans. ID")
        self.trans_tree.heading("book_id", text="Book ID")
        self.trans_tree.heading("member_id", text="Member ID")
        self.trans_tree.heading("issue_date", text="Issue Date")
        self.trans_tree.heading("due_date", text="Due Date")
        self.trans_tree.heading("return_date", text="Return Date")
        self.trans_tree.heading("fine", text="Fine")
        self.trans_tree.heading("status", text="Status")
        
        widths = [80, 80, 80, 100, 100, 100, 80, 80]
        for col, width in zip(columns, widths):
            self.trans_tree.column(col, width=width, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                 command=self.trans_tree.yview)
        self.trans_tree.configure(yscroll=scrollbar.set)
        
        self.trans_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        self.trans_tree.tag_configure('issued', foreground=self.colors["warning"])
        self.trans_tree.tag_configure('returned', foreground=self.colors["success"])
        
        self.refresh_transactions_table()
    
    # ============ ACTION METHODS ============
    
    def update_datetime(self):
        try:
            current = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.datetime_lbl.config(text=current)
            self.root.after(1000, self.update_datetime)
        except:
            pass
    
    def refresh_dashboard(self):
        # Update stats
        self.c.execute("SELECT COUNT(*) FROM books")
        total_books = self.c.fetchone()[0]
        
        self.c.execute("SELECT SUM(available_copies) FROM books")
        available_books = self.c.fetchone()[0] or 0
        
        self.c.execute("SELECT COUNT(*) FROM members")
        total_members = self.c.fetchone()[0]
        
        self.c.execute("SELECT COUNT(*) FROM transactions WHERE status='ISSUED'")
        issued_books = self.c.fetchone()[0]
        
        # Update recent transactions
        for item in self.dashboard_tree.get_children():
            self.dashboard_tree.delete(item)
        
        self.c.execute("""SELECT t.transaction_id, t.book_id, t.member_id, 
                                 t.issue_date, t.status 
                          FROM transactions t 
                          ORDER BY t.transaction_id DESC LIMIT 10""")
        rows = self.c.fetchall()
        
        for row in rows:
            self.dashboard_tree.insert("", tk.END, values=row)
    
    def refresh_books_table(self):
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        
        self.c.execute("SELECT * FROM books")
        rows = self.c.fetchall()
        
        for i, row in enumerate(rows):
            tag = 'oddrow' if i % 2 else 'evenrow'
            self.books_tree.insert("", tk.END, values=row, tags=(tag,))
    
    def select_book(self, event):
        try:
            selected = self.books_tree.selection()
            if not selected:
                return
            item = self.books_tree.item(selected[0])
            vals = item['values']
            
            self.clear_book_form()
            self.book_entries["book_id"].insert(0, vals[0])
            self.book_entries["title"].insert(0, vals[1])
            self.book_entries["author"].insert(0, vals[2])
            self.book_entries["isbn"].insert(0, vals[3])
            self.book_entries["category"].insert(0, vals[4])
            self.book_entries["total_copies"].insert(0, vals[5])
        except Exception as e:
            print(f"Select error: {e}")
    
    def clear_book_form(self):
        for entry in self.book_entries.values():
            entry.delete(0, tk.END)
        sel = self.books_tree.selection()
        if sel:
            self.books_tree.selection_remove(sel)
    
    def add_book(self):
        vals = {k: v.get().strip() for k, v in self.book_entries.items()}
        
        if not all(vals.values()):
            messagebox.showwarning("Input Error", "Please fill all fields!")
            return
        
        try:
            total = int(vals["total_copies"])
            if total < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Total copies must be a positive number!")
            return
        
        try:
            self.c.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (vals["book_id"], vals["title"], vals["author"],
                           vals["isbn"], vals["category"], total, total))
            self.conn.commit()
            self.refresh_books_table()
            self.clear_book_form()
            messagebox.showinfo("Success", "Book added successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Book ID already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add book: {e}")
    
    def update_book(self):
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a book to update!")
            return
        
        vals = {k: v.get().strip() for k, v in self.book_entries.items()}
        
        if not all(vals.values()):
            messagebox.showwarning("Input Error", "Please fill all fields!")
            return
        
        try:
            total = int(vals["total_copies"])
            if total < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Total copies must be a positive number!")
            return
        
        try:
            original_id = self.books_tree.item(selected[0])['values'][0]
            
            # Calculate available copies
            self.c.execute("SELECT available_copies, total_copies FROM books WHERE book_id=?", (original_id,))
            row = self.c.fetchone()
            old_total = row[1]
            old_available = row[0]
            diff = total - old_total
            new_available = old_available + diff
            
            if new_available < 0:
                messagebox.showerror("Error", "Cannot reduce total copies below currently issued copies!")
                return
            
            self.c.execute("""UPDATE books SET title=?, author=?, isbn=?, 
                             category=?, total_copies=?, available_copies=? 
                             WHERE book_id=?""",
                          (vals["title"], vals["author"], vals["isbn"],
                           vals["category"], total, new_available, original_id))
            self.conn.commit()
            self.refresh_books_table()
            self.clear_book_form()
            messagebox.showinfo("Success", "Book updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update book: {e}")
    
    def delete_book(self):
        selected = self.books_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a book to delete!")
            return
        
        book_id = self.books_tree.item(selected[0])['values'][0]
        
        # Check if book is issued
        self.c.execute("SELECT COUNT(*) FROM transactions WHERE book_id=? AND status='ISSUED'", (book_id,))
        if self.c.fetchone()[0] > 0:
            messagebox.showerror("Error", "Cannot delete book! It is currently issued to a member.")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Book ID: {book_id}?")
        if confirm:
            try:
                self.c.execute("DELETE FROM books WHERE book_id=?", (book_id,))
                self.conn.commit()
                self.refresh_books_table()
                self.clear_book_form()
                messagebox.showinfo("Success", "Book deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete book: {e}")
    
    def search_books(self):
        query = self.book_search_var.get().strip()
        if not query:
            self.refresh_books_table()
            return
        
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        
        self.c.execute("""SELECT * FROM books WHERE book_id LIKE ? OR title LIKE ? 
                         OR author LIKE ? OR category LIKE ?""",
                      (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
        rows = self.c.fetchall()
        
        for i, row in enumerate(rows):
            tag = 'oddrow' if i % 2 else 'evenrow'
            self.books_tree.insert("", tk.END, values=row, tags=(tag,))
        
        if not rows:
            messagebox.showinfo("Info", "No books found!")
    
    def refresh_members_table(self):
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        
        self.c.execute("SELECT * FROM members")
        rows = self.c.fetchall()
        
        for i, row in enumerate(rows):
            tag = 'oddrow' if i % 2 else 'evenrow'
            self.members_tree.insert("", tk.END, values=row, tags=(tag,))
    
    def select_member(self, event):
        try:
            selected = self.members_tree.selection()
            if not selected:
                return
            item = self.members_tree.item(selected[0])
            vals = item['values']
            
            self.clear_member_form()
            self.member_entries["member_id"].insert(0, vals[0])
            self.member_entries["name"].insert(0, vals[1])
            self.member_entries["contact"].insert(0, vals[2])
            self.member_entries["email"].insert(0, vals[3])
        except Exception as e:
            print(f"Select error: {e}")
    
    def clear_member_form(self):
        for entry in self.member_entries.values():
            entry.delete(0, tk.END)
        sel = self.members_tree.selection()
        if sel:
            self.members_tree.selection_remove(sel)
    
    def add_member(self):
        vals = {k: v.get().strip() for k, v in self.member_entries.items()}
        
        if not all(vals.values()):
            messagebox.showwarning("Input Error", "Please fill all fields!")
            return
        
        try:
            membership_date = datetime.now().strftime("%Y-%m-%d")
            self.c.execute("INSERT INTO members VALUES (?, ?, ?, ?, ?)",
                          (vals["member_id"], vals["name"], vals["contact"],
                           vals["email"], membership_date))
            self.conn.commit()
            self.refresh_members_table()
            self.clear_member_form()
            messagebox.showinfo("Success", "Member added successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Member ID already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add member: {e}")
    
    def update_member(self):
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a member to update!")
            return
        
        vals = {k: v.get().strip() for k, v in self.member_entries.items()}
        
        if not all(vals.values()):
            messagebox.showwarning("Input Error", "Please fill all fields!")
            return
        
        try:
            original_id = self.members_tree.item(selected[0])['values'][0]
            self.c.execute("""UPDATE members SET name=?, contact=?, email=? 
                             WHERE member_id=?""",
                          (vals["name"], vals["contact"], vals["email"], original_id))
            self.conn.commit()
            self.refresh_members_table()
            self.clear_member_form()
            messagebox.showinfo("Success", "Member updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update member: {e}")
    
    def delete_member(self):
        selected = self.members_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a member to delete!")
            return
        
        member_id = self.members_tree.item(selected[0])['values'][0]
        
        # Check if member has issued books
        self.c.execute("SELECT COUNT(*) FROM transactions WHERE member_id=? AND status='ISSUED'", (member_id,))
        if self.c.fetchone()[0] > 0:
            messagebox.showerror("Error", "Cannot delete member! They have books issued.")
            return
        
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Member ID: {member_id}?")
        if confirm:
            try:
                self.c.execute("DELETE FROM members WHERE member_id=?", (member_id,))
                self.conn.commit()
                self.refresh_members_table()
                self.clear_member_form()
                messagebox.showinfo("Success", "Member deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete member: {e}")
    
    def search_members(self):
        query = self.member_search_var.get().strip()
        if not query:
            self.refresh_members_table()
            return
        
        for item in self.members_tree.get_children():
            self.members_tree.delete(item)
        
        self.c.execute("""SELECT * FROM members WHERE member_id LIKE ? OR name LIKE ? 
                         OR contact LIKE ? OR email LIKE ?""",
                      (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
        rows = self.c.fetchall()
        
        for i, row in enumerate(rows):
            tag = 'oddrow' if i % 2 else 'evenrow'
            self.members_tree.insert("", tk.END, values=row, tags=(tag,))
        
        if not rows:
            messagebox.showinfo("Info", "No members found!")
    
    def issue_book(self):
        vals = {k: v.get().strip() for k, v in self.issue_entries.items()}
        
        if not all(vals.values()):
            messagebox.showwarning("Input Error", "Please fill all fields!")
            return
        
        book_id = vals["issue_book_id"]
        member_id = vals["issue_member_id"]
        due_date = vals["due_date"]
        
        # Validate due date
        try:
            due = datetime.strptime(due_date, "%Y-%m-%d")
            if due <= datetime.now():
                messagebox.showerror("Input Error", "Due date must be in the future!")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Invalid date format! Use YYYY-MM-DD")
            return
        
        # Check if book exists and is available
        self.c.execute("SELECT available_copies FROM books WHERE book_id=?", (book_id,))
        book_row = self.c.fetchone()
        if not book_row:
            messagebox.showerror("Error", "Book not found!")
            return
        if book_row[0] <= 0:
            messagebox.showerror("Error", "Book is not available! All copies are issued.")
            return
        
        # Check if member exists
        self.c.execute("SELECT * FROM members WHERE member_id=?", (member_id,))
        if not self.c.fetchone():
            messagebox.showerror("Error", "Member not found!")
            return
        
        try:
            issue_date = datetime.now().strftime("%Y-%m-%d")
            
            # Insert transaction
            self.c.execute("""INSERT INTO transactions 
                             (book_id, member_id, issue_date, due_date, return_date, fine, status)
                             VALUES (?, ?, ?, ?, NULL, 0, 'ISSUED')""",
                          (book_id, member_id, issue_date, due_date))
            
            # Update book availability
            self.c.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id=?",
                          (book_id,))
            
            self.conn.commit()
            
            # Clear form
            self.issue_entries["issue_book_id"].delete(0, tk.END)
            self.issue_entries["issue_member_id"].delete(0, tk.END)
            
            messagebox.showinfo("Success", "Book issued successfully!")
            self.refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to issue book: {e}")
    
    def check_return_details(self):
        trans_id = self.return_trans_id.get().strip()
        if not trans_id:
            messagebox.showwarning("Input Error", "Please enter Transaction ID!")
            return
        
        try:
            trans_id = int(trans_id)
        except ValueError:
            messagebox.showerror("Input Error", "Transaction ID must be a number!")
            return
        
        self.c.execute("""SELECT t.*, b.title, m.name 
                         FROM transactions t
                         JOIN books b ON t.book_id = b.book_id
                         JOIN members m ON t.member_id = m.member_id
                         WHERE t.transaction_id = ?""", (trans_id,))
        row = self.c.fetchone()
        
        if not row:
            messagebox.showerror("Error", "Transaction not found!")
            self.return_info_lbl.config(text="")
            return
        
        if row[7] == 'RETURNED':
            messagebox.showwarning("Warning", "This book has already been returned!")
            self.return_info_lbl.config(text="")
            return
        
        # Calculate fine
        due_date = datetime.strptime(row[3], "%Y-%m-%d")
        today = datetime.now()
        days_late = (today - due_date).days
        fine = max(0, days_late * 5)  # Rs. 5 per day
        
        info = f"""Book: {row[8]} | Member: {row[9]}
Issue Date: {row[2]} | Due Date: {row[3]}
Days Late: {max(0, days_late)} | Fine: Rs. {fine}"""
        
        self.return_info_lbl.config(text=info, fg=self.colors["text_dark"])
    
    def return_book(self):
        trans_id = self.return_trans_id.get().strip()
        if not trans_id:
            messagebox.showwarning("Input Error", "Please enter Transaction ID!")
            return
        
        try:
            trans_id = int(trans_id)
        except ValueError:
            messagebox.showerror("Input Error", "Transaction ID must be a number!")
            return
        
        # Get transaction details
        self.c.execute("SELECT * FROM transactions WHERE transaction_id = ?", (trans_id,))
        row = self.c.fetchone()
        
        if not row:
            messagebox.showerror("Error", "Transaction not found!")
            return
        
        if row[7] == 'RETURNED':
            messagebox.showwarning("Warning", "This book has already been returned!")
            return
        
        # Calculate fine
        due_date = datetime.strptime(row[3], "%Y-%m-%d")
        today = datetime.now()
        days_late = (today - due_date).days
        fine = max(0, days_late * 5)
        
        confirm_msg = f"Return this book?\n"
        if fine > 0:
            confirm_msg += f"Fine: Rs. {fine} ({days_late} days late)"
        
        confirm = messagebox.askyesno("Confirm Return", confirm_msg)
        if not confirm:
            return
        
        try:
            return_date = datetime.now().strftime("%Y-%m-%d")
            
            # Update transaction
            self.c.execute("""UPDATE transactions 
                             SET return_date=?, fine=?, status='RETURNED'
                             WHERE transaction_id=?""",
                          (return_date, fine, trans_id))
            
            # Update book availability
            self.c.execute("UPDATE books SET available_copies = available_copies + 1 WHERE book_id=?",
                          (row[1],))
            
            self.conn.commit()
            
            self.return_trans_id.delete(0, tk.END)
            self.return_info_lbl.config(text="")
            
            msg = "Book returned successfully!"
            if fine > 0:
                msg += f"\nFine collected: Rs. {fine}"
            
            messagebox.showinfo("Success", msg)
            self.refresh_dashboard()
            self.refresh_transactions_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to return book: {e}")
    
    def refresh_transactions_table(self):
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)
        
        filter_val = self.trans_filter_var.get()
        
        if filter_val == "ALL":
            self.c.execute("SELECT * FROM transactions ORDER BY transaction_id DESC")
        else:
            self.c.execute("SELECT * FROM transactions WHERE status=? ORDER BY transaction_id DESC",
                          (filter_val,))
        
        rows = self.c.fetchall()
        
        for row in rows:
            fine_display = f"Rs. {row[5]}" if row[5] > 0 else "-"
            return_date = row[4] if row[4] else "-"
            tag = 'issued' if row[6] == 'ISSUED' else 'returned'
            
            self.trans_tree.insert("", tk.END,
                                  values=(row[0], row[1], row[2], row[3], row[4] or "-",
                                         return_date, fine_display, row[6]),
                                  tags=(tag,))
    
    def on_close(self):
        try:
            self.conn.close()
        except:
            pass
        self.root.destroy()


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = LibraryManagementSystem(root)
        root.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")