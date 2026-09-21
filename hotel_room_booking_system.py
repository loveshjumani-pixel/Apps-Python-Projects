import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime, timedelta

class HotelBookingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Royal Grand Hotel - Booking System")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")
        
        # Colors
        self.colors = {
            "primary": "#2c5f8d",
            "secondary": "#4a90e2",
            "success": "#27ae60",
            "warning": "#f39c12",
            "danger": "#e74c3c",
            "light": "#ecf0f1",
            "dark": "#2c3e50"
        }
        
        self.current_user = None
        self.booking_entries = {}
        self.stat_labels = {}
        
        self.setup_database()
        self.create_login_screen()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_database(self):
        try:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hotel.db')
            self.conn = sqlite3.connect(db_path)
            self.c = self.conn.cursor()
            
            # Create tables
            self.c.execute('''CREATE TABLE IF NOT EXISTS admin
                              (username TEXT PRIMARY KEY, password TEXT, name TEXT)''')
            
            self.c.execute('''CREATE TABLE IF NOT EXISTS rooms
                              (room_no TEXT PRIMARY KEY, room_type TEXT, 
                               price REAL, floor INTEGER, status TEXT)''')
            
            self.c.execute('''CREATE TABLE IF NOT EXISTS guests
                              (guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                               name TEXT, phone TEXT, email TEXT, 
                               id_proof TEXT, id_number TEXT)''')
            
            self.c.execute('''CREATE TABLE IF NOT EXISTS bookings
                              (booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                               room_no TEXT, guest_id INTEGER, 
                               check_in TEXT, check_out TEXT,
                               nights INTEGER, total_amount REAL,
                               advance REAL, status TEXT, booking_date TEXT)''')
            
            self.conn.commit()
            
            # Default admin
            self.c.execute("SELECT * FROM admin WHERE username='admin'")
            if not self.c.fetchone():
                self.c.execute("INSERT INTO admin VALUES ('admin', 'admin123', 'Manager')")
                self.conn.commit()
            
            # Sample rooms
            self.c.execute("SELECT COUNT(*) FROM rooms")
            if self.c.fetchone()[0] == 0:
                rooms = [
                    ('101', 'Single', 1500, 1, 'AVAILABLE'),
                    ('102', 'Single', 1500, 1, 'AVAILABLE'),
                    ('103', 'Double', 2500, 1, 'AVAILABLE'),
                    ('104', 'Double', 2500, 1, 'AVAILABLE'),
                    ('201', 'Deluxe', 4000, 2, 'AVAILABLE'),
                    ('202', 'Deluxe', 4000, 2, 'AVAILABLE'),
                    ('301', 'Suite', 8000, 3, 'AVAILABLE'),
                    ('302', 'Suite', 10000, 3, 'AVAILABLE'),
                ]
                self.c.executemany("INSERT INTO rooms VALUES (?, ?, ?, ?, ?)", rooms)
                self.conn.commit()
                
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
            import sys
            sys.exit(1)
    
    def create_login_screen(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self.root, bg=self.colors["primary"], height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="ROYAL GRAND HOTEL", font=("Arial", 24, "bold"),
                bg=self.colors["primary"], fg="white").pack(pady=20)
        
        # Login Frame
        login_frame = tk.Frame(self.root, bg="white", relief=tk.RAISED, bd=2)
        login_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=300)
        
        tk.Label(login_frame, text="Staff Login", font=("Arial", 18, "bold"),
                bg="white", fg=self.colors["primary"]).pack(pady=20)
        
        # Username
        tk.Label(login_frame, text="Username:", font=("Arial", 11),
                bg="white").pack(anchor="w", padx=30, pady=(10, 0))
        self.username_entry = tk.Entry(login_frame, font=("Arial", 11), bd=1, relief=tk.SOLID)
        self.username_entry.pack(fill=tk.X, padx=30, pady=5, ipady=5)
        
        # Password
        tk.Label(login_frame, text="Password:", font=("Arial", 11),
                bg="white").pack(anchor="w", padx=30, pady=(10, 0))
        self.password_entry = tk.Entry(login_frame, font=("Arial", 11), show="*", bd=1, relief=tk.SOLID)
        self.password_entry.pack(fill=tk.X, padx=30, pady=5, ipady=5)
        self.password_entry.bind("<Return>", lambda e: self.login())
        
        # Login Button
        tk.Button(login_frame, text="LOGIN", font=("Arial", 12, "bold"),
                 bg=self.colors["success"], fg="white", bd=0, cursor="hand2",
                 command=self.login).pack(fill=tk.X, padx=30, pady=20, ipady=5)
        
        tk.Label(login_frame, text="Demo: admin / admin123", font=("Arial", 9),
                bg="white", fg="gray").pack(pady=(0, 10))
    
    def create_main_interface(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self.root, bg=self.colors["primary"], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="HOTEL MANAGEMENT SYSTEM", font=("Arial", 20, "bold"),
                bg=self.colors["primary"], fg="white").pack(side=tk.LEFT, padx=20, pady=15)
        
        self.user_lbl = tk.Label(header, text=f"Welcome: {self.current_user}", 
                                font=("Arial", 11), bg=self.colors["primary"], fg="white")
        self.user_lbl.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Main Container
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left Sidebar
        sidebar = tk.Frame(main_frame, bg=self.colors["dark"], width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Rooms", self.show_rooms),
            ("New Booking", self.show_booking),
            ("Active Bookings", self.show_active),
            ("Check Out", self.show_checkout),
            ("History", self.show_history),
            ("Logout", self.logout),
        ]
        
        for text, cmd in buttons:
            btn = tk.Button(sidebar, text=text, font=("Arial", 11),
                           bg=self.colors["dark"], fg="white", bd=0,
                           cursor="hand2", pady=10, command=cmd)
            btn.pack(fill=tk.X, pady=2, padx=5)
            
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.colors["secondary"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.colors["dark"]))
        
        # Content Area
        self.content_frame = tk.Frame(main_frame, bg="#f0f0f0")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Show dashboard by default
        self.show_dashboard()
    
    def show_dashboard(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.content_frame, text="DASHBOARD", font=("Arial", 18, "bold"),
                bg="#f0f0f0", fg=self.colors["primary"]).pack(anchor="w", pady=10)
        
        # Stats
        stats_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.c.execute("SELECT COUNT(*) FROM rooms")
        total = self.c.fetchone()[0]
        
        self.c.execute("SELECT COUNT(*) FROM rooms WHERE status='AVAILABLE'")
        available = self.c.fetchone()[0]
        
        self.c.execute("SELECT COUNT(*) FROM rooms WHERE status='OCCUPIED'")
        occupied = self.c.fetchone()[0]
        
        today = datetime.now().strftime("%Y-%m-%d")
        self.c.execute("SELECT COALESCE(SUM(total_amount), 0) FROM bookings WHERE booking_date LIKE ?", (today + '%',))
        revenue = self.c.fetchone()[0]
        
        stats = [
            ("Total Rooms", total, self.colors["primary"]),
            ("Available", available, self.colors["success"]),
            ("Occupied", occupied, self.colors["warning"]),
            ("Today's Revenue", f"Rs. {revenue:,.0f}", self.colors["danger"]),
        ]
        
        for i, (label, value, color) in enumerate(stats):
            card = tk.Frame(stats_frame, bg="white", relief=tk.RAISED, bd=2)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)
            
            tk.Label(card, text=label, font=("Arial", 11), bg="white", fg="gray").pack(pady=(15, 5))
            tk.Label(card, text=str(value), font=("Arial", 24, "bold"),
                    bg="white", fg=color).pack(pady=(0, 15))
    
    def show_rooms(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.content_frame, text="ROOM STATUS", font=("Arial", 18, "bold"),
                bg="#f0f0f0", fg=self.colors["primary"]).pack(anchor="w", pady=10)
        
        # Filter
        filter_frame = tk.Frame(self.content_frame, bg="white", relief=tk.RAISED, bd=1)
        filter_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(filter_frame, text="Filter:", font=("Arial", 11),
                bg="white").pack(side=tk.LEFT, padx=10, pady=10)
        
        self.room_filter = tk.StringVar(value="ALL")
        for text in ["ALL", "Single", "Double", "Deluxe", "Suite"]:
            tk.Radiobutton(filter_frame, text=text, variable=self.room_filter,
                          value=text, bg="white", font=("Arial", 10),
                          command=self.display_rooms).pack(side=tk.LEFT, padx=5)
        
        tk.Button(filter_frame, text="+ Add Room", font=("Arial", 10, "bold"),
                 bg=self.colors["success"], fg="white", bd=0, cursor="hand2",
                 command=self.add_room).pack(side=tk.RIGHT, padx=10, pady=8)
        
        self.display_rooms()
    
    def display_rooms(self):
        # Clear previous
        for widget in self.content_frame.winfo_children():
            if widget != self.content_frame.winfo_children()[0]:  # Keep title
                widget.destroy()
        
        # Re-add filter
        filter_frame = tk.Frame(self.content_frame, bg="white", relief=tk.RAISED, bd=1)
        filter_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(filter_frame, text="Filter:", font=("Arial", 11),
                bg="white").pack(side=tk.LEFT, padx=10, pady=10)
        
        self.room_filter = tk.StringVar(value="ALL")
        for text in ["ALL", "Single", "Double", "Deluxe", "Suite"]:
            tk.Radiobutton(filter_frame, text=text, variable=self.room_filter,
                          value=text, bg="white", font=("Arial", 10),
                          command=self.display_rooms).pack(side=tk.LEFT, padx=5)
        
        tk.Button(filter_frame, text="+ Add Room", font=("Arial", 10, "bold"),
                 bg=self.colors["success"], fg="white", bd=0, cursor="hand2",
                 command=self.add_room).pack(side=tk.RIGHT, padx=10, pady=8)
        
        # Rooms grid
        grid_frame = tk.Frame(self.content_frame, bg="#f0f0f0")
        grid_frame.pack(fill=tk.BOTH, expand=True)
        
        filter_val = self.room_filter.get()
        if filter_val == "ALL":
            self.c.execute("SELECT * FROM rooms ORDER BY room_no")
        else:
            self.c.execute("SELECT * FROM rooms WHERE room_type=? ORDER BY room_no", (filter_val,))
        
        rooms = self.c.fetchall()
        
        if not rooms:
            tk.Label(grid_frame, text="No rooms found", font=("Arial", 12),
                    bg="#f0f0f0", fg="gray").pack(pady=40)
            return
        
        cols = 4
        for i, room in enumerate(rooms):
            row = i // cols
            col = i % cols
            
            room_no, room_type, price, floor, status = room
            color = self.colors["success"] if status == "AVAILABLE" else self.colors["danger"]
            
            card = tk.Frame(grid_frame, bg="white", relief=tk.RAISED, bd=2, cursor="hand2")
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew", ipadx=15, ipady=10)
            grid_frame.grid_columnconfigure(col, weight=1)
            
            tk.Label(card, text=f"Room {room_no}", font=("Arial", 12, "bold"),
                    bg="white", fg=self.colors["primary"]).pack(pady=5)
            tk.Label(card, text=room_type, font=("Arial", 10),
                    bg="white", fg=self.colors["secondary"]).pack()
            tk.Label(card, text=f"Rs. {price}/night", font=("Arial", 9),
                    bg="white", fg="gray").pack(pady=3)
            tk.Label(card, text=status, font=("Arial", 10, "bold"),
                    bg="white", fg=color).pack(pady=5)
            
            card.bind("<Button-1>", lambda e, r=room: self.room_action(r))
    
    def add_room(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Room")
        dialog.geometry("350x300")
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Add New Room", font=("Arial", 14, "bold"),
                bg="white", fg=self.colors["primary"]).pack(pady=15)
        
        fields = [
            ("Room Number:", "room_no"),
            ("Type (Single/Double/Deluxe/Suite):", "type"),
            ("Price:", "price"),
            ("Floor:", "floor"),
        ]
        
        entries = {}
        for label, key in fields:
            tk.Label(dialog, text=label, font=("Arial", 10), bg="white").pack(anchor="w", padx=20, pady=(10, 0))
            entry = tk.Entry(dialog, font=("Arial", 10), bd=1, relief=tk.SOLID)
            entry.pack(fill=tk.X, padx=20, pady=3, ipady=3)
            entries[key] = entry
        
        def save():
            try:
                room_no = entries["room_no"].get().strip()
                room_type = entries["type"].get().strip()
                price = float(entries["price"].get().strip())
                floor = int(entries["floor"].get().strip())
                
                if not room_no or room_type not in ["Single", "Double", "Deluxe", "Suite"]:
                    raise ValueError("Invalid input")
                
                self.c.execute("INSERT INTO rooms VALUES (?, ?, ?, ?, 'AVAILABLE')",
                              (room_no, room_type, price, floor))
                self.conn.commit()
                messagebox.showinfo("Success", "Room added!", parent=dialog)
                dialog.destroy()
                self.display_rooms()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=dialog)
        
        tk.Button(dialog, text="SAVE", font=("Arial", 11, "bold"),
                 bg=self.colors["success"], fg="white", bd=0,
                 command=save).pack(fill=tk.X, padx=20, pady=20)
    
    def room_action(self, room):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Room {room[0]}")
        dialog.geometry("300x200")
        dialog.configure(bg="white")
        dialog.transient(self.root)
        dialog.grab_set()
        
        room_no, room_type, price, floor, status = room
        
        tk.Label(dialog, text=f"Room {room_no} - {room_type}", font=("Arial", 14, "bold"),
                bg="white", fg=self.colors["primary"]).pack(pady=15)
        
        tk.Label(dialog, text=f"Price: Rs. {price}\nFloor: {floor}\nStatus: {status}",
                font=("Arial", 11), bg="white").pack(pady=10)
        
        def toggle():
            new_status = "AVAILABLE" if status == "OCCUPIED" else "OCCUPIED"
            self.c.execute("UPDATE rooms SET status=? WHERE room_no=?", (new_status, room_no))
            self.conn.commit()
            messagebox.showinfo("Success", f"Status: {new_status}", parent=dialog)
            dialog.destroy()
            self.display_rooms()
        
        def delete():
            if status == "OCCUPIED":
                messagebox.showerror("Error", "Cannot delete occupied room!", parent=dialog)
                return
            if messagebox.askyesno("Confirm", "Delete this room?", parent=dialog):
                self.c.execute("DELETE FROM rooms WHERE room_no=?", (room_no,))
                self.conn.commit()
                messagebox.showinfo("Success", "Room deleted", parent=dialog)
                dialog.destroy()
                self.display_rooms()
        
        btn_frame = tk.Frame(dialog, bg="white")
        btn_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Button(btn_frame, text="Toggle Status", font=("Arial", 10),
                 bg=self.colors["warning"], fg="white", bd=0,
                 command=toggle).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        tk.Button(btn_frame, text="Delete", font=("Arial", 10),
                 bg=self.colors["danger"], fg="white", bd=0,
                 command=delete).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    
    def show_booking(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.content_frame, text="NEW BOOKING", font=("Arial", 18, "bold"),
                bg="#f0f0f0", fg=self.colors["primary"]).pack(anchor="w", pady=10)
        
        # Guest Info
        guest_frame = tk.LabelFrame(self.content_frame, text="Guest Information",
                                   font=("Arial", 12, "bold"), bg="white", relief=tk.RAISED, bd=1)
        guest_frame.pack(fill=tk.X, pady=10, padx=10)
        
        fields = [
            ("Name:", "name"), ("Phone:", "phone"), ("Email:", "email"),
            ("ID Proof:", "id_type"), ("ID Number:", "id_no"),
        ]
        
        for label, key in fields:
            f = tk.Frame(guest_frame, bg="white")
            f.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(f, text=label, font=("Arial", 10), bg="white", width=12, anchor="w").pack(side=tk.LEFT)
            entry = tk.Entry(f, font=("Arial", 10), bd=1, relief=tk.SOLID)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=3)
            self.booking_entries[key] = entry
        
        # Booking Info
        book_frame = tk.LabelFrame(self.content_frame, text="Booking Details",
                                  font=("Arial", 12, "bold"), bg="white", relief=tk.RAISED, bd=1)
        book_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Room
        f = tk.Frame(book_frame, bg="white")
        f.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(f, text="Room:", font=("Arial", 10), bg="white", width=12).pack(side=tk.LEFT)
        
        self.c.execute("SELECT room_no, room_type, price FROM rooms WHERE status='AVAILABLE'")
        rooms = self.c.fetchall()
        
        self.room_var = tk.StringVar()
        if rooms:
            room_options = [f"{r[0]} - {r[1]} (Rs. {r[2]})" for r in rooms]
            self.room_var.set(room_options[0])
            self.room_dropdown = tk.OptionMenu(f, self.room_var, *room_options)
            self.room_dropdown.config(font=("Arial", 10), width=30)
            self.room_dropdown.pack(side=tk.LEFT, padx=5)
            self.room_dropdown.bind("<<ComboboxSelected>>", lambda e: self.calc_total())
        else:
            tk.Label(f, text="No rooms available", font=("Arial", 10), bg="white").pack(side=tk.LEFT)
        
        # Dates
        f = tk.Frame(book_frame, bg="white")
        f.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(f, text="Check-in:", font=("Arial", 10), bg="white", width=12).pack(side=tk.LEFT)
        self.checkin = tk.Entry(f, font=("Arial", 10), bd=1, relief=tk.SOLID)
        self.checkin.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.checkin.pack(side=tk.LEFT, padx=5, ipady=3)
        
        f = tk.Frame(book_frame, bg="white")
        f.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(f, text="Check-out:", font=("Arial", 10), bg="white", width=12).pack(side=tk.LEFT)
        self.checkout = tk.Entry(f, font=("Arial", 10), bd=1, relief=tk.SOLID)
        self.checkout.insert(0, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
        self.checkout.pack(side=tk.LEFT, padx=5, ipady=3)
        
        self.checkin.bind("<KeyRelease>", lambda e: self.calc_total())
        self.checkout.bind("<KeyRelease>", lambda e: self.calc_total())
        
        # Total
        self.total_lbl = tk.Label(book_frame, text="Total: Rs. 0", font=("Arial", 14, "bold"),
                                 bg="white", fg=self.colors["danger"])
        self.total_lbl.pack(pady=10)
        
        # Advance
        f = tk.Frame(book_frame, bg="white")
        f.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(f, text="Advance:", font=("Arial", 10), bg="white", width=12).pack(side=tk.LEFT)
        self.advance_entry = tk.Entry(f, font=("Arial", 10), bd=1, relief=tk.SOLID)
        self.advance_entry.insert(0, "0")
        self.advance_entry.pack(side=tk.LEFT, padx=5, ipady=3)
        
        # Book Button
        tk.Button(self.content_frame, text="CONFIRM BOOKING", font=("Arial", 12, "bold"),
                 bg=self.colors["success"], fg="white", bd=0, cursor="hand2",
                 command=self.confirm_booking).pack(fill=tk.X, padx=10, pady=15, ipady=5)
    
    def calc_total(self):
        try:
            room_text = self.room_var.get()
            if not room_text or "No rooms" in room_text:
                return
            
            room_no = room_text.split(" - ")[0]
            self.c.execute("SELECT price FROM rooms WHERE room_no=?", (room_no,))
            price = self.c.fetchone()[0]
            
            checkin = datetime.strptime(self.checkin.get(), "%Y-%m-%d")
            checkout = datetime.strptime(self.checkout.get(), "%Y-%m-%d")
            
            if checkout > checkin:
                nights = (checkout - checkin).days
                total = price * nights
                self.total_lbl.config(text=f"Total: Rs. {total:,}")
        except:
            pass
    
    def confirm_booking(self):
        try:
            name = self.booking_entries["name"].get().strip()
            phone = self.booking_entries["phone"].get().strip()
            email = self.booking_entries["email"].get().strip()
            id_type = self.booking_entries["id_type"].get().strip()
            id_no = self.booking_entries["id_no"].get().strip()
            
            if not all([name, phone, id_type, id_no]):
                messagebox.showwarning("Error", "Fill all required fields!")
                return
            
            if len(phone) != 10 or not phone.isdigit():
                messagebox.showwarning("Error", "Phone must be 10 digits!")
                return
            
            room_text = self.room_var.get()
            room_no = room_text.split(" - ")[0]
            
            checkin = self.checkin.get()
            checkout = self.checkout.get()
            advance = float(self.advance_entry.get() or 0)
            
            checkin_dt = datetime.strptime(checkin, "%Y-%m-%d")
            checkout_dt = datetime.strptime(checkout, "%Y-%m-%d")
            
            if checkout_dt <= checkin_dt:
                messagebox.showwarning("Error", "Check-out must be after check-in!")
                return
            
            self.c.execute("SELECT price FROM rooms WHERE room_no=?", (room_no,))
            price = self.c.fetchone()[0]
            nights = (checkout_dt - checkin_dt).days
            total = price * nights
            
            if advance > total:
                messagebox.showwarning("Error", "Advance cannot exceed total!")
                return
            
            if not messagebox.askyesno("Confirm", f"Total: Rs. {total:,}\nAdvance: Rs. {advance:,}\nConfirm?"):
                return
            
            # Insert guest
            self.c.execute("INSERT INTO guests (name, phone, email, id_proof, id_number) VALUES (?, ?, ?, ?, ?)",
                          (name, phone, email, id_type, id_no))
            guest_id = self.c.lastrowid
            
            # Insert booking
            booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.c.execute("""INSERT INTO bookings 
                             (room_no, guest_id, check_in, check_out, nights, total_amount, advance, status, booking_date)
                             VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)""",
                          (room_no, guest_id, checkin, checkout, nights, total, advance, booking_date))
            
            # Update room
            self.c.execute("UPDATE rooms SET status='OCCUPIED' WHERE room_no=?", (room_no,))
            self.conn.commit()
            
            messagebox.showinfo("Success", f"Booking confirmed!\nRoom: {room_no}\nTotal: Rs. {total:,}")
            
            # Clear form
            for entry in self.booking_entries.values():
                entry.delete(0, tk.END)
            self.advance_entry.delete(0, tk.END)
            self.advance_entry.insert(0, "0")
            
            self.show_booking()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def show_active(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.content_frame, text="ACTIVE BOOKINGS", font=("Arial", 18, "bold"),
                bg="#f0f0f0", fg=self.colors["primary"]).pack(anchor="w", pady=10)
        
        tree_frame = tk.Frame(self.content_frame, bg="white", relief=tk.RAISED, bd=1)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("ID", "Room", "Guest", "Phone", "Check-in", "Check-out", "Nights", "Amount")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.c.execute("""SELECT b.booking_id, b.room_no, g.name, g.phone,
                                 b.check_in, b.check_out, b.nights, b.total_amount
                          FROM bookings b
                          JOIN guests g ON b.guest_id = g.guest_id
                          WHERE b.status='ACTIVE'
                          ORDER BY b.booking_id DESC""")
        
        for row in self.c.fetchall():
            tree.insert("", tk.END, values=row)
    
    def show_checkout(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.content_frame, text="CHECK OUT", font=("Arial", 18, "bold"),
                bg="#f0f0f0", fg=self.colors["primary"]).pack(anchor="w", pady=10)
        
        frame = tk.Frame(self.content_frame, bg="white", relief=tk.RAISED, bd=1)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(frame, text="Booking ID:", font=("Arial", 11), bg="white").pack(side=tk.LEFT, padx=10)
        self.checkout_id = tk.Entry(frame, font=("Arial", 11), bd=1, relief=tk.SOLID)
        self.checkout_id.pack(side=tk.LEFT, padx=5, ipady=5)
        
        tk.Button(frame, text="Fetch", font=("Arial", 10, "bold"),
                 bg=self.colors["secondary"], fg="white", bd=0,
                 command=self.fetch_checkout).pack(side=tk.LEFT, padx=5)
        
        self.checkout_details = tk.Frame(self.content_frame, bg="#f0f0f0")
        self.checkout_details.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Button(self.content_frame, text="COMPLETE CHECKOUT", font=("Arial", 12, "bold"),
                 bg=self.colors["danger"], fg="white", bd=0,
                 command=self.process_checkout).pack(fill=tk.X, padx=10, pady=10, ipady=5)
        
        self.current_checkout = None
    
    def fetch_checkout(self):
        try:
            bid = int(self.checkout_id.get().strip())
        except:
            messagebox.showerror("Error", "Invalid Booking ID!")
            return
        
        self.c.execute("""SELECT b.*, g.name, g.phone, g.email
                         FROM bookings b
                         JOIN guests g ON b.guest_id = g.guest_id
                         WHERE b.booking_id=? AND b.status='ACTIVE'""", (bid,))
        
        row = self.c.fetchone()
        if not row:
            messagebox.showerror("Error", "Booking not found!")
            return
        
        self.current_checkout = row
        
        for widget in self.checkout_details.winfo_children():
            widget.destroy()
        
        info = f"""
Guest: {row[9]}  |  Phone: {row[10]}
Room: {row[1]}  |  Check-in: {row[3]}  |  Check-out: {row[4]}
Nights: {row[5]}  |  Total: Rs. {row[6]:,}  |  Advance: Rs. {row[7]:,}
Balance: Rs. {row[6] - row[7]:,}
"""
        tk.Label(self.checkout_details, text=info, font=("Arial", 11),
                bg="white", relief=tk.SOLID, bd=1, justify="left").pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def process_checkout(self):
        if not self.current_checkout:
            messagebox.showwarning("Error", "Fetch booking details first!")
            return
        
        if messagebox.askyesno("Confirm", "Complete checkout?"):
            try:
                bid = self.current_checkout[0]
                room_no = self.current_checkout[1]
                
                self.c.execute("UPDATE bookings SET status='COMPLETED' WHERE booking_id=?", (bid,))
                self.c.execute("UPDATE rooms SET status='AVAILABLE' WHERE room_no=?", (room_no,))
                self.conn.commit()
                
                messagebox.showinfo("Success", "Checkout completed!")
                self.checkout_id.delete(0, tk.END)
                for widget in self.checkout_details.winfo_children():
                    widget.destroy()
                self.current_checkout = None
            except Exception as e:
                messagebox.showerror("Error", str(e))
    
    def show_history(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.content_frame, text="BOOKING HISTORY", font=("Arial", 18, "bold"),
                bg="#f0f0f0", fg=self.colors["primary"]).pack(anchor="w", pady=10)
        
        tree_frame = tk.Frame(self.content_frame, bg="white", relief=tk.RAISED, bd=1)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("ID", "Room", "Guest", "Check-in", "Check-out", "Amount", "Status")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.c.execute("""SELECT b.booking_id, b.room_no, g.name, b.check_in, b.check_out,
                                 b.total_amount, b.status
                          FROM bookings b
                          JOIN guests g ON b.guest_id = g.guest_id
                          ORDER BY b.booking_id DESC
                          LIMIT 100""")
        
        for row in self.c.fetchall():
            tree.insert("", tk.END, values=row)
    
    def login(self):
        user = self.username_entry.get().strip()
        pwd = self.password_entry.get().strip()
        
        if not user or not pwd:
            messagebox.showwarning("Error", "Enter username and password!")
            return
        
        self.c.execute("SELECT * FROM admin WHERE username=? AND password=?", (user, pwd))
        if self.c.fetchone():
            self.current_user = user
            self.create_main_interface()
        else:
            messagebox.showerror("Error", "Invalid credentials!")
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure?"):
            self.current_user = None
            self.create_login_screen()
    
    def on_close(self):
        try:
            self.conn.close()
        except:
            pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = HotelBookingSystem(root)
    root.mainloop()