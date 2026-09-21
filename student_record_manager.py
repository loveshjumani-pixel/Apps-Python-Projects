import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import sys
import os

class StudentManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Record Manager")
        self.root.geometry("1000x650")
        self.root.minsize(900, 600)
        self.root.configure(bg="#f4f6f9")
        
        # Database Setup - current directory mein
        try:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'students.db')
            self.conn = sqlite3.connect(db_path)
            self.c = self.conn.cursor()
            self.c.execute('''CREATE TABLE IF NOT EXISTS students
                              (roll TEXT PRIMARY KEY, name TEXT, age INTEGER, course TEXT, contact TEXT)''')
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Database Error", f"Database setup failed: {e}")
            sys.exit(1)

        # Font setup - safe fonts use karein
        self.title_font = ("Arial", 20, "bold")
        self.heading_font = ("Arial", 14, "bold")
        self.normal_font = ("Arial", 11)
        self.btn_font = ("Arial", 11, "bold")
        
        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        # --- Header ---
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="STUDENT RECORD MANAGER", 
                               font=self.title_font, bg="#2c3e50", fg="white")
        title_label.pack(pady=15)

        # --- Main Container ---
        main_frame = tk.Frame(self.root, bg="#f4f6f9")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # --- Left Panel (Form) ---
        left_frame = tk.Frame(main_frame, bg="#ffffff", relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        form_label = tk.Label(left_frame, text="Student Details", 
                              font=self.heading_font, bg="#ffffff", fg="#2c3e50")
        form_label.pack(pady=(15, 10))

        fields = [("Roll Number:", "roll"), ("Full Name:", "name"), 
                  ("Age:", "age"), ("Course:", "course"), ("Contact No:", "contact")]
        
        self.entries = {}
        for label_text, field_name in fields:
            frame = tk.Frame(left_frame, bg="#ffffff")
            frame.pack(fill=tk.X, padx=20, pady=5)
            
            lbl = tk.Label(frame, text=label_text, font=self.normal_font, 
                          bg="#ffffff", anchor="w", width=12)
            lbl.pack(side=tk.LEFT)
            
            entry = tk.Entry(frame, font=self.normal_font, relief=tk.SOLID, bd=1)
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
            self.entries[field_name] = entry

        # Buttons
        btn_frame = tk.Frame(left_frame, bg="#ffffff")
        btn_frame.pack(fill=tk.X, padx=20, pady=20)

        btn_style = {"font": self.btn_font, "fg": "white", "relief": tk.FLAT, 
                     "cursor": "hand2", "activeforeground": "white"}
        
        self.btn_add = tk.Button(btn_frame, text="ADD", bg="#27ae60", 
                                 command=self.add_student, **btn_style)
        self.btn_add.pack(fill=tk.X, pady=5, ipady=6)

        self.btn_update = tk.Button(btn_frame, text="UPDATE", bg="#2980b9", 
                                    command=self.update_student, **btn_style)
        self.btn_update.pack(fill=tk.X, pady=5, ipady=6)

        self.btn_delete = tk.Button(btn_frame, text="DELETE", bg="#c0392b", 
                                    command=self.delete_student, **btn_style)
        self.btn_delete.pack(fill=tk.X, pady=5, ipady=6)

        self.btn_clear = tk.Button(btn_frame, text="CLEAR", bg="#7f8c8d", 
                                   command=self.clear_fields, **btn_style)
        self.btn_clear.pack(fill=tk.X, pady=5, ipady=6)

        # --- Right Panel (Table) ---
        right_frame = tk.Frame(main_frame, bg="#ffffff", relief=tk.RAISED, bd=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Search Bar
        search_frame = tk.Frame(right_frame, bg="#ffffff")
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="Search:", font=self.normal_font, 
                bg="#ffffff").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, 
                                     font=self.normal_font, relief=tk.SOLID, bd=1)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        tk.Button(search_frame, text="Search", bg="#8e44ad", fg="white", 
                  font=self.btn_font, relief=tk.FLAT, cursor="hand2", 
                  command=self.search_student).pack(side=tk.LEFT, padx=5, ipady=2)
        tk.Button(search_frame, text="Show All", bg="#34495e", fg="white", 
                  font=self.btn_font, relief=tk.FLAT, cursor="hand2", 
                  command=self.refresh_table).pack(side=tk.LEFT, padx=5, ipady=2)

        # Treeview (Table)
        tree_frame = tk.Frame(right_frame, bg="#ffffff")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        try:
            style = ttk.Style()
            style.theme_use('clam')  # clam theme zyada stable hai
            style.configure("Treeview", font=self.normal_font, rowheight=30, 
                          background="#ffffff", fieldbackground="#ffffff")
            style.configure("Treeview.Heading", font=self.btn_font, 
                          background="#ecf0f1", foreground="#2c3e50")
            style.map("Treeview", background=[("selected", "#3498db")], 
                     foreground=[("selected", "white")])
        except Exception as e:
            print(f"Style warning: {e}")

        columns = ("roll", "name", "age", "course", "contact")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        self.tree.heading("roll", text="Roll No")
        self.tree.heading("name", text="Name")
        self.tree.heading("age", text="Age")
        self.tree.heading("course", text="Course")
        self.tree.heading("contact", text="Contact")

        self.tree.column("roll", width=100, anchor=tk.CENTER)
        self.tree.column("name", width=200, anchor=tk.W)
        self.tree.column("age", width=80, anchor=tk.CENTER)
        self.tree.column("course", width=150, anchor=tk.W)
        self.tree.column("contact", width=150, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.tag_configure('oddrow', background='#f9f9f9')
        self.tree.tag_configure('evenrow', background='#ffffff')

        self.tree.bind("<ButtonRelease-1>", self.select_record)

    def get_values(self):
        return {k: v.get().strip() for k, v in self.entries.items()}

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        sel = self.tree.selection()
        if sel:
            self.tree.selection_remove(sel)

    def add_student(self):
        vals = self.get_values()
        if not all(vals.values()):
            messagebox.showwarning("Input Error", "Please fill all the fields!")
            return
        
        try:
            age_int = int(vals['age'])
            if age_int < 1 or age_int > 120:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Age must be a valid number (1-120)!")
            return

        try:
            self.c.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?)", 
                           (vals['roll'], vals['name'], vals['age'], vals['course'], vals['contact']))
            self.conn.commit()
            self.refresh_table()
            self.clear_fields()
            messagebox.showinfo("Success", "Student added successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Roll Number already exists!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add: {e}")

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            self.c.execute("SELECT * FROM students")
            rows = self.c.fetchall()
            
            for i, row in enumerate(rows):
                tag = 'oddrow' if i % 2 else 'evenrow'
                self.tree.insert("", tk.END, values=row, tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")

    def select_record(self, event):
        try:
            selected = self.tree.selection()
            if not selected:
                return
            item = self.tree.item(selected[0])
            vals = item['values']
            
            self.clear_fields()
            self.entries['roll'].insert(0, vals[0])
            self.entries['name'].insert(0, vals[1])
            self.entries['age'].insert(0, vals[2])
            self.entries['course'].insert(0, vals[3])
            self.entries['contact'].insert(0, vals[4])
        except Exception as e:
            print(f"Select error: {e}")

    def update_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a student to update!")
            return

        vals = self.get_values()
        if not all(vals.values()):
            messagebox.showwarning("Input Error", "Please fill all the fields!")
            return
            
        try:
            int(vals['age'])
        except ValueError:
            messagebox.showerror("Input Error", "Age must be a valid number!")
            return

        try:
            original_roll = self.tree.item(selected[0])['values'][0]
            self.c.execute("UPDATE students SET name=?, age=?, course=?, contact=? WHERE roll=?",
                           (vals['name'], vals['age'], vals['course'], vals['contact'], original_roll))
            self.conn.commit()
            self.refresh_table()
            self.clear_fields()
            messagebox.showinfo("Success", "Student updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update: {e}")

    def delete_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a student to delete!")
            return

        try:
            roll = self.tree.item(selected[0])['values'][0]
            confirm = messagebox.askyesno("Confirm Delete", 
                                         f"Are you sure you want to delete Roll No: {roll}?")
            
            if confirm:
                self.c.execute("DELETE FROM students WHERE roll=?", (roll,))
                self.conn.commit()
                self.refresh_table()
                self.clear_fields()
                messagebox.showinfo("Success", "Student deleted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")

    def search_student(self):
        query = self.search_var.get().strip()
        if not query:
            self.refresh_table()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            self.c.execute("SELECT * FROM students WHERE name LIKE ? OR roll LIKE ?", 
                          (f'%{query}%', f'%{query}%'))
            rows = self.c.fetchall()
            
            for i, row in enumerate(rows):
                tag = 'oddrow' if i % 2 else 'evenrow'
                self.tree.insert("", tk.END, values=row, tags=(tag,))
                
            if not rows:
                messagebox.showinfo("Info", "No records found!")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {e}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = StudentManager(root)
        root.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")