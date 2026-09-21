import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib
matplotlib.use('TkAgg')  # IMPORTANT: Backend set karna zaroori hai
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import csv
import os

# --- Global Theme Settings ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class GradeCalculatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🎓 Advanced Student Grade Calculator")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # Main container with padding
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # Header
        self.create_header()

        # Content area (Left + Right)
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.left_frame = ctk.CTkFrame(self.content_frame, width=320, corner_radius=15)
        self.left_frame.pack(side="left", fill="y", padx=(0, 15))
        self.left_frame.pack_propagate(False)

        self.right_frame = ctk.CTkFrame(self.content_frame, corner_radius=15)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Data storage
        self.subjects_data = []

        self.setup_left_panel()
        self.setup_right_panel()

    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_container, corner_radius=15, height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        title = ctk.CTkLabel(
            header_frame, 
            text="🎓 Student Grade Calculator",
            font=("Segoe UI", 26, "bold"),
            text_color=("#1f538d", "#3b8ed0")
        )
        title.pack(side="left", padx=25, pady=15)

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Advanced Analytics & Visualization",
            font=("Segoe UI", 13),
            text_color="gray"
        )
        subtitle.pack(side="left", padx=10, pady=25)

    def setup_left_panel(self):
        title = ctk.CTkLabel(
            self.left_frame, 
            text="📝 Student Details", 
            font=("Segoe UI", 20, "bold")
        )
        title.pack(pady=(25, 20))

        # Student Name
        self.create_input_field("Student Name:", "name")
        
        # Subject Name
        self.create_input_field("Subject Name:", "subject")
        
        # Marks
        self.create_input_field("Marks (Out of 100):", "marks")

        # Buttons Frame
        btn_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(20, 20))

        btn_config = {"width": 260, "height": 42, "corner_radius": 10, "font": ("Segoe UI", 13, "bold")}

        self.add_btn = ctk.CTkButton(
            btn_frame, text="➕ Add Subject",
            fg_color="#28a745", hover_color="#1e7e34",
            command=self.add_subject, **btn_config
        )
        self.add_btn.pack(pady=6)

        self.calc_btn = ctk.CTkButton(
            btn_frame, text="📊 Calculate & Graph",
            fg_color="#0d6efd", hover_color="#0a58ca",
            command=self.calculate_and_plot, **btn_config
        )
        self.calc_btn.pack(pady=6)

        self.save_btn = ctk.CTkButton(
            btn_frame, text="💾 Save to CSV",
            fg_color="#fd7e14", hover_color="#c46210",
            command=self.save_to_csv, **btn_config
        )
        self.save_btn.pack(pady=6)

        self.reset_btn = ctk.CTkButton(
            btn_frame, text="🔄 Reset All",
            fg_color="#dc3545", hover_color="#b02a37",
            command=self.reset_all, **btn_config
        )
        self.reset_btn.pack(pady=6)

    def create_input_field(self, label_text, field_type):
        """Helper function to create consistent input fields"""
        label = ctk.CTkLabel(
            self.left_frame, text=label_text,
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        )
        label.pack(pady=(12, 4), padx=25, fill="x")

        entry = ctk.CTkEntry(
            self.left_frame, height=38, corner_radius=8,
            font=("Segoe UI", 13),
            border_width=1, border_color=("#ccc", "#444")
        )
        entry.pack(pady=(0, 5), padx=25, fill="x")

        if field_type == "name":
            self.name_entry = entry
        elif field_type == "subject":
            self.sub_entry = entry
        elif field_type == "marks":
            self.marks_entry = entry

    def setup_right_panel(self):
        # Result Summary
        self.result_label = ctk.CTkLabel(
            self.right_frame,
            text="📋 Results will appear here...",
            font=("Segoe UI", 16, "bold"),
            text_color="#00d2ff",
            wraplength=600
        )
        self.result_label.pack(pady=(20, 10), padx=20)

        # Treeview with proper dark theme styling
        self.setup_treeview()

        # Matplotlib Graph
        self.graph_frame = ctk.CTkFrame(self.right_frame, corner_radius=10)
        self.graph_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.fig.patch.set_facecolor('#1e1e1e')
        self.ax = self.fig.add_subplot(111)
        self.setup_graph_style()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def setup_treeview(self):
        """Cross-platform Treeview styling"""
        style = ttk.Style()
        
        # Try different themes based on availability
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        # Configure Treeview colors
        style.configure(
            "Custom.Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            borderwidth=0,
            rowheight=32,
            font=("Segoe UI", 12)
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#1f538d",
            foreground="white",
            font=("Segoe UI", 13, "bold"),
            borderwidth=0,
            relief="flat"
        )
        style.map(
            'Custom.Treeview',
            background=[('selected', '#0d6efd')],
            foreground=[('selected', 'white')]
        )

        # Treeview container with scrollbar
        tree_container = ctk.CTkFrame(self.right_frame, corner_radius=8)
        tree_container.pack(pady=10, padx=20, fill="x")

        columns = ("Subject", "Marks", "Grade")
        self.tree = ttk.Treeview(
            tree_container, 
            columns=columns, 
            show="headings", 
            height=6,
            style="Custom.Treeview"
        )

        self.tree.heading("Subject", text="📚 Subject Name")
        self.tree.heading("Marks", text="📊 Marks")
        self.tree.heading("Grade", text="🏆 Grade")

        self.tree.column("Subject", width=200, anchor="w")
        self.tree.column("Marks", width=120, anchor="center")
        self.tree.column("Grade", width=120, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="x", expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side="right", fill="y", padx=(0, 5), pady=5)

    def setup_graph_style(self):
        """Configure matplotlib graph appearance"""
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='white', labelsize=10)
        self.ax.yaxis.label.set_color('white')
        self.ax.xaxis.label.set_color('white')
        self.ax.title.set_color('white')
        self.ax.spines['bottom'].set_color('#555')
        self.ax.spines['left'].set_color('#555')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.grid(axis='y', color='#444', linestyle='--', alpha=0.5)

    def get_grade(self, marks):
        """Calculate grade based on marks"""
        try:
            marks = float(marks)
            if marks >= 90: return "A+ (Outstanding)"
            elif marks >= 80: return "A (Excellent)"
            elif marks >= 70: return "B (Very Good)"
            elif marks >= 60: return "C (Good)"
            elif marks >= 50: return "D (Pass)"
            else: return "F (Fail)"
        except:
            return "N/A"

    def get_grade_color(self, marks):
        """Return color based on marks"""
        if marks >= 80: return '#28a745'    # Green
        elif marks >= 60: return '#17a2b8'  # Cyan
        elif marks >= 50: return '#ffc107'  # Yellow
        else: return '#dc3545'              # Red

    def add_subject(self):
        """Add a subject to the list"""
        try:
            sub = self.sub_entry.get().strip()
            marks_str = self.marks_entry.get().strip()

            if not sub:
                messagebox.showwarning("⚠️ Input Error", "Please enter Subject Name!")
                return
            if not marks_str:
                messagebox.showwarning("⚠️ Input Error", "Please enter Marks!")
                return

            try:
                marks = float(marks_str)
                if marks < 0 or marks > 100:
                    raise ValueError("Range error")
            except ValueError:
                messagebox.showerror(
                    "❌ Invalid Input", 
                    "Marks must be a number between 0 and 100!"
                )
                return

            grade = self.get_grade(marks)
            sub_cap = sub.capitalize()
            
            self.tree.insert("", "end", values=(sub_cap, f"{marks:.1f}", grade))
            self.subjects_data.append({
                "Subject": sub_cap, 
                "Marks": marks, 
                "Grade": grade
            })

            # Clear entries
            self.sub_entry.delete(0, tk.END)
            self.marks_entry.delete(0, tk.END)
            self.sub_entry.focus()

        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")

    def calculate_and_plot(self):
        """Calculate results and plot graph"""
        try:
            if not self.subjects_data:
                messagebox.showinfo("ℹ️ Empty Data", "Please add at least one subject first!")
                return

            student_name = self.name_entry.get().strip() or "Student"
            total_marks = sum(item["Marks"] for item in self.subjects_data)
            max_marks = len(self.subjects_data) * 100
            percentage = (total_marks / max_marks) * 100
            final_grade = self.get_grade(percentage)

            # Update result label
            result_text = (
                f"👤 {student_name}  |  "
                f"📊 Total: {total_marks:.1f}/{max_marks}  |  "
                f"📈 Percentage: {percentage:.2f}%  |  "
                f"🏆 Grade: {final_grade}"
            )
            self.result_label.configure(text=result_text)

            # Plot graph
            self.ax.clear()
            self.setup_graph_style()

            subjects = [item["Subject"] for item in self.subjects_data]
            marks = [item["Marks"] for item in self.subjects_data]
            colors = [self.get_grade_color(m) for m in marks]

            bars = self.ax.bar(
                subjects, marks, 
                color=colors, width=0.6, 
                edgecolor='white', linewidth=1.2
            )

            self.ax.set_title(
                "📊 Subject-wise Performance Analysis", 
                fontsize=13, fontweight='bold', pad=12
            )
            self.ax.set_ylabel("Marks Obtained", fontsize=11)
            self.ax.set_ylim(0, 115)

            # Add value labels on bars
            for bar in bars:
                yval = bar.get_height()
                self.ax.text(
                    bar.get_x() + bar.get_width()/2, 
                    yval + 2, 
                    f"{yval:.0f}",
                    ha='center', va='bottom', 
                    color='white', fontsize=10, fontweight='bold'
                )

            # Rotate x labels if many subjects
            if len(subjects) > 5:
                self.ax.tick_params(axis='x', rotation=30)

            self.fig.tight_layout()
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Error", f"Error in calculation: {str(e)}")

    def save_to_csv(self):
        """Save data to CSV with file dialog"""
        try:
            if not self.subjects_data:
                messagebox.showinfo("ℹ️ Empty Data", "No data to save!")
                return

            student_name = self.name_entry.get().strip() or "Student"
            default_filename = f"{student_name.replace(' ', '_')}_grades.csv"

            # Open file dialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                initialfile=default_filename,
                title="Save Grade Report"
            )

            if not file_path:  # User cancelled
                return

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=["Subject", "Marks", "Grade"])
                writer.writeheader()
                writer.writerows(self.subjects_data)

            messagebox.showinfo(
                "✅ Success", 
                f"Data saved successfully!\n\nLocation: {file_path}"
            )

        except PermissionError:
            messagebox.showerror(
                "❌ Permission Error", 
                "Cannot save file. Please choose a different location."
            )
        except Exception as e:
            messagebox.showerror("❌ Error", f"Could not save file:\n{str(e)}")

    def reset_all(self):
        """Reset all fields and data"""
        try:
            confirm = messagebox.askyesno(
                "🔄 Confirm Reset", 
                "Are you sure you want to reset all data?"
            )
            if not confirm:
                return

            self.name_entry.delete(0, tk.END)
            self.sub_entry.delete(0, tk.END)
            self.marks_entry.delete(0, tk.END)
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            self.subjects_data.clear()
            self.result_label.configure(text="📋 Results will appear here...")
            
            self.ax.clear()
            self.setup_graph_style()
            self.canvas.draw()

            self.name_entry.focus()

        except Exception as e:
            messagebox.showerror("Error", f"Reset error: {str(e)}")


if __name__ == "__main__":
    try:
        app = GradeCalculatorApp()
        app.mainloop()
    except Exception as e:
        print(f"❌ Application Error: {e}")
        messagebox.showerror(
            "Fatal Error", 
            f"Application failed to start:\n{str(e)}\n\n"
            f"Please ensure customtkinter and matplotlib are installed:\n"
            f"pip install customtkinter matplotlib"
        )