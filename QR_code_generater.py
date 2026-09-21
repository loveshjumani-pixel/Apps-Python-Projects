import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    SquareModuleDrawer,
    RoundedModuleDrawer,
    CircleModuleDrawer,
    GappedSquareModuleDrawer
)
from PIL import Image, ImageTk, ImageDraw
import os
import json
from datetime import datetime
import threading
from io import BytesIO
import base64

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AdvancedQRGenerator:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🎨 Professional QR Code Generator")
        self.root.geometry("1400x900")
        self.root.configure(fg_color=("#f0f4f8", "#1a1d23"))
        
        # Variables
        self.current_qr = None
        self.current_text = ""
        self.logo_path = None
        self.history = []
        self.history_file = "qr_history.json"
        self.load_history()
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with gradient effect
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header
        self.create_header()
        
        # Content area
        content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=20)
        
        # Left panel - Controls
        left_panel = ctk.CTkScrollableFrame(content_frame, 
                                           fg_color=("#ffffff", "#2d3748"),
                                           corner_radius=20,
                                           width=450)
        left_panel.pack(side="left", fill="y", padx=(0, 20))
        
        # Right panel - Preview and History
        right_panel = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True)
        
        self.setup_controls(left_panel)
        self.setup_preview_area(right_panel)
        
    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, 
                                   fg_color=("#3b82f6", "#1e40af"),
                                   height=80,
                                   corner_radius=15)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(header_frame, 
                           text="✨ Advanced QR Code Generator",
                           font=ctk.CTkFont(size=28, weight="bold"),
                           text_color="white")
        title.pack(side="left", padx=30, pady=20)
        
        # Theme toggle
        self.theme_btn = ctk.CTkButton(header_frame, 
                                      text="🌙",
                                      width=50,
                                      height=50,
                                      font=ctk.CTkFont(size=20),
                                      command=self.toggle_theme,
                                      fg_color="transparent",
                                      hover_color=("#2563eb", "#1e3a8a"))
        self.theme_btn.pack(side="right", padx=30, pady=15)
        
    def setup_controls(self, panel):
        # Input Section
        input_card = self.create_card(panel, "📝 Enter Data")
        
        ctk.CTkLabel(input_card, text="Text or URL:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        self.text_input = ctk.CTkTextbox(input_card, 
                                        height=120,
                                        corner_radius=10,
                                        border_width=2,
                                        border_color=("#e5e7eb", "#4b5563"))
        self.text_input.pack(fill="x", pady=(0, 15))
        
        # Color Section
        color_card = self.create_card(panel, "🎨 Customize Colors")
        
        color_grid = ctk.CTkFrame(color_card, fg_color="transparent")
        color_grid.pack(fill="x", pady=10)
        
        # Foreground color
        fg_frame = ctk.CTkFrame(color_grid, fg_color="transparent")
        fg_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(fg_frame, text="Foreground:", 
                    font=ctk.CTkFont(size=12)).pack(anchor="w")
        
        self.fg_btn = ctk.CTkButton(fg_frame, 
                                   text="● Black",
                                   height=40,
                                   command=lambda: self.pick_color("fg"),
                                   fg_color="#000000",
                                   hover_color="#333333")
        self.fg_btn.pack(fill="x", pady=5)
        
        # Background color
        bg_frame = ctk.CTkFrame(color_grid, fg_color="transparent")
        bg_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(bg_frame, text="Background:", 
                    font=ctk.CTkFont(size=12)).pack(anchor="w")
        
        self.bg_btn = ctk.CTkButton(bg_frame, 
                                   text="● White",
                                   height=40,
                                   command=lambda: self.pick_color("bg"),
                                   fg_color="#ffffff",
                                   text_color="#000000",
                                   hover_color="#e5e5e5")
        self.bg_btn.pack(fill="x", pady=5)
        
        # Settings Section
        settings_card = self.create_card(panel, "⚙️ Settings")
        
        # Size
        ctk.CTkLabel(settings_card, text="Size (pixels):", 
                    font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 5))
        
        self.size_slider = ctk.CTkSlider(settings_card, 
                                        from_=100, 
                                        to=800,
                                        number_of_steps=7,
                                        command=self.update_size_label)
        self.size_slider.set(400)
        self.size_slider.pack(fill="x", pady=5)
        
        self.size_label = ctk.CTkLabel(settings_card, text="400px",
                                      font=ctk.CTkFont(size=11))
        self.size_label.pack(anchor="e")
        
        # Error Correction
        ctk.CTkLabel(settings_card, text="Error Correction:", 
                    font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 5))
        
        self.error_var = ctk.StringVar(value="H")
        error_menu = ctk.CTkOptionMenu(settings_card,
                                      values=["L (7%)", "M (15%)", "Q (25%)", "H (30%)"],
                                      variable=self.error_var,
                                      corner_radius=10)
        error_menu.pack(fill="x", pady=5)
        
        # Style
        ctk.CTkLabel(settings_card, text="Module Style:", 
                    font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 5))
        
        self.style_var = ctk.StringVar(value="Rounded")
        style_menu = ctk.CTkOptionMenu(settings_card,
                                      values=["Square", "Rounded", "Circle", "Gapped Square"],
                                      variable=self.style_var,
                                      corner_radius=10)
        style_menu.pack(fill="x", pady=5)
        
        # Logo Section
        logo_card = self.create_card(panel, "🖼️ Logo (Optional)")
        
        self.logo_btn = ctk.CTkButton(logo_card,
                                     text="📁 Upload Logo",
                                     height=45,
                                     corner_radius=10,
                                     command=self.upload_logo)
        self.logo_btn.pack(fill="x", pady=10)
        
        self.logo_status = ctk.CTkLabel(logo_card, text="No logo selected",
                                       text_color="gray",
                                       font=ctk.CTkFont(size=11))
        self.logo_status.pack(pady=5)
        
        # Generate Button
        self.generate_btn = ctk.CTkButton(panel,
                                         text="🚀 Generate QR Code",
                                         height=60,
                                         font=ctk.CTkFont(size=18, weight="bold"),
                                         corner_radius=15,
                                         fg_color=("#3b82f6", "#2563eb"),
                                         hover_color=("#2563eb", "#1e40af"),
                                         command=self.generate_qr)
        self.generate_btn.pack(fill="x", pady=20)
        
    def create_card(self, parent, title):
        card = ctk.CTkFrame(parent, 
                           fg_color=("#f9fafb", "#374151"),
                           corner_radius=15,
                           border_width=1,
                           border_color=("#e5e7eb", "#4b5563"))
        card.pack(fill="x", padx=15, pady=10)
        
        card_title = ctk.CTkLabel(card, 
                                 text=title,
                                 font=ctk.CTkFont(size=16, weight="bold"))
        card_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=(0, 20))
        
        return content
        
    def setup_preview_area(self, panel):
        # Preview Card
        preview_card = ctk.CTkFrame(panel,
                                   fg_color=("#ffffff", "#2d3748"),
                                   corner_radius=20,
                                   border_width=2,
                                   border_color=("#e5e7eb", "#4b5563"))
        preview_card.pack(fill="both", expand=True, pady=(0, 20))
        
        preview_title = ctk.CTkLabel(preview_card,
                                    text="👁️ Preview",
                                    font=ctk.CTkFont(size=20, weight="bold"))
        preview_title.pack(pady=20)
        
        self.preview_frame = ctk.CTkFrame(preview_card,
                                         fg_color=("#f3f4f6", "#1f2937"),
                                         corner_radius=15)
        self.preview_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        self.preview_label = ctk.CTkLabel(self.preview_frame,
                                         text="Your QR code will appear here",
                                         font=ctk.CTkFont(size=16),
                                         text_color="gray")
        self.preview_label.pack(expand=True)
        
        # Save Buttons
        save_frame = ctk.CTkFrame(preview_card, fg_color="transparent")
        save_frame.pack(fill="x", padx=30, pady=20)
        
        btn_style = {"height": 50, "corner_radius": 12, "font": ctk.CTkFont(size=14, weight="bold")}
        
        self.save_png = ctk.CTkButton(save_frame,
                                     text="💾 Save PNG",
                                     command=lambda: self.save_qr("PNG"),
                                     state="disabled",
                                     fg_color=("#10b981", "#059669"),
                                     hover_color=("#059669", "#047857"),
                                     **btn_style)
        self.save_png.pack(side="left", expand=True, fill="x", padx=5)
        
        self.save_jpg = ctk.CTkButton(save_frame,
                                     text="💾 Save JPG",
                                     command=lambda: self.save_qr("JPG"),
                                     state="disabled",
                                     fg_color=("#f59e0b", "#d97706"),
                                     hover_color=("#d97706", "#b45309"),
                                     **btn_style)
        self.save_jpg.pack(side="left", expand=True, fill="x", padx=5)
        
        self.save_svg = ctk.CTkButton(save_frame,
                                     text="💾 Save SVG",
                                     command=lambda: self.save_qr("SVG"),
                                     state="disabled",
                                     fg_color=("#8b5cf6", "#7c3aed"),
                                     hover_color=("#7c3aed", "#6d28d9"),
                                     **btn_style)
        self.save_svg.pack(side="left", expand=True, fill="x", padx=5)
        
        # History Section
        history_card = ctk.CTkFrame(panel,
                                   fg_color=("#ffffff", "#2d3748"),
                                   corner_radius=20,
                                   border_width=2,
                                   border_color=("#e5e7eb", "#4b5563"))
        history_card.pack(fill="x")
        
        history_title = ctk.CTkLabel(history_card,
                                    text="📜 Recent History",
                                    font=ctk.CTkFont(size=18, weight="bold"))
        history_title.pack(pady=15)
        
        self.history_frame = ctk.CTkScrollableFrame(history_card,
                                                   height=150,
                                                   corner_radius=10)
        self.history_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.update_history_display()
        
    def pick_color(self, color_type):
        color = colorchooser.askcolor(title=f"Choose {color_type} color")
        if color[1]:
            if color_type == "fg":
                self.fg_color = color[1]
                self.fg_btn.configure(fg_color=color[1], text=f"● {color[1]}")
                if self.is_light_color(color[1]):
                    self.fg_btn.configure(text_color="#000000")
                else:
                    self.fg_btn.configure(text_color="#ffffff")
            else:
                self.bg_color = color[1]
                self.bg_btn.configure(fg_color=color[1], text=f"● {color[1]}")
                if self.is_light_color(color[1]):
                    self.bg_btn.configure(text_color="#000000")
                else:
                    self.bg_btn.configure(text_color="#ffffff")
                    
    def is_light_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return brightness > 127
        
    def update_size_label(self, value):
        self.size_label.configure(text=f"{int(value)}px")
        
    def upload_logo(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.logo_path = file_path
            filename = os.path.basename(file_path)
            self.logo_status.configure(text=f"✓ {filename}", text_color="#10b981")
            
    def generate_qr(self):
        text = self.text_input.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text or URL!")
            return
            
        try:
            # Get settings
            size = int(self.size_slider.get())
            error_text = self.error_var.get()
            error_level = error_text.split()[0]
            style = self.style_var.get()
            
            fg_color = getattr(self, 'fg_color', '#000000')
            bg_color = getattr(self, 'bg_color', '#ffffff')
            
            # Map error correction levels
            error_map = {
                "L": qrcode.constants.ERROR_CORRECT_L,
                "M": qrcode.constants.ERROR_CORRECT_M,
                "Q": qrcode.constants.ERROR_CORRECT_Q,
                "H": qrcode.constants.ERROR_CORRECT_H
            }
            
            # Map styles
            style_map = {
                "Square": SquareModuleDrawer(),
                "Rounded": RoundedModuleDrawer(),
                "Circle": CircleModuleDrawer(),
                "Gapped Square": GappedSquareModuleDrawer()
            }
            
            # Create QR code
            qr = qrcode.QRCode(
                version=None,
                error_correction=error_map[error_level],
                box_size=10,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)
            
            # Generate image
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=style_map[style],
                fill_color=fg_color,
                back_color=bg_color
            ).convert("RGBA")
            
            # Add logo if provided
            if self.logo_path:
                img = self.add_logo_to_qr(img, error_level)
            
            # Resize
            img = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Store current QR
            self.current_qr = img
            self.current_text = text
            
            # Display preview
            self.display_preview(img)
            
            # Enable save buttons
            self.save_png.configure(state="normal")
            self.save_jpg.configure(state="normal")
            self.save_svg.configure(state="normal")
            
            # Add to history
            self.add_to_history(text)
            
            # Success message
            self.preview_label.configure(text="")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating QR code:\n{str(e)}")
            
    def add_logo_to_qr(self, qr_img, error_level):
        try:
            logo = Image.open(self.logo_path)
            
            # Convert logo to RGBA if needed
            if logo.mode != "RGBA":
                logo = logo.convert("RGBA")
            
            # Calculate logo size based on error correction
            size_ratios = {"L": 0.15, "M": 0.20, "Q": 0.25, "H": 0.30}
            ratio = size_ratios.get(error_level, 0.20)
            
            qr_width, qr_height = qr_img.size
            logo_size = int(min(qr_width, qr_height) * ratio)
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Create circular mask if logo is not square
            if logo.width != logo.height:
                logo = self.make_square(logo)
            
            # Calculate position
            pos_x = (qr_width - logo_size) // 2
            pos_y = (qr_height - logo_size) // 2
            
            # Add white background for logo
            bg_size = logo_size + 20
            bg = Image.new("RGBA", (bg_size, bg_size), (255, 255, 255, 255))
            bg_pos = ((qr_width - bg_size) // 2, (qr_height - bg_size) // 2)
            
            # Paste background and logo
            qr_img.paste(bg, bg_pos, bg)
            qr_img.paste(logo, (pos_x, pos_y), logo)
            
            return qr_img
        except Exception as e:
            print(f"Logo error: {e}")
            return qr_img
            
    def make_square(self, img):
        width, height = img.size
        size = max(width, height)
        square = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        offset_x = (size - width) // 2
        offset_y = (size - height) // 2
        square.paste(img, (offset_x, offset_y))
        return square
        
    def display_preview(self, img):
        # Calculate preview size
        frame_width = self.preview_frame.winfo_width() - 60
        frame_height = self.preview_frame.winfo_height() - 60
        
        if frame_width < 100:
            frame_width = 400
        if frame_height < 100:
            frame_height = 400
            
        preview_size = min(frame_width, frame_height, 500)
        
        img_preview = img.copy()
        img_preview.thumbnail((preview_size, preview_size), Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(img_preview)
        
        self.preview_label.configure(image=photo, text="")
        self.preview_label.image = photo
        
    def save_qr(self, format_type):
        if not self.current_qr:
            messagebox.showwarning("Warning", "No QR code generated yet!")
            return
            
        file_types = {
            "PNG": [("PNG files", "*.png")],
            "JPG": [("JPEG files", "*.jpg *.jpeg")],
            "SVG": [("SVG files", "*.svg")]
        }
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{format_type.lower()}",
            filetypes=file_types[format_type],
            initialfile=f"qrcode_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        if file_path:
            try:
                if format_type == "SVG":
                    self.save_as_svg(file_path)
                elif format_type == "JPG":
                    # Convert RGBA to RGB for JPG
                    rgb_img = Image.new("RGB", self.current_qr.size, (255, 255, 255))
                    rgb_img.paste(self.current_qr, mask=self.current_qr.split()[3])
                    rgb_img.save(file_path, "JPEG", quality=95)
                else:
                    self.current_qr.save(file_path, format_type)
                    
                messagebox.showinfo("Success", f"✅ QR code saved successfully!\nLocation: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file:\n{str(e)}")
                
    def save_as_svg(self, file_path):
        # Get current settings
        text = self.current_text
        error_text = self.error_var.get()
        error_level = error_text.split()[0]
        style = self.style_var.get()
        fg_color = getattr(self, 'fg_color', '#000000')
        bg_color = getattr(self, 'bg_color', '#ffffff')
        
        error_map = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H
        }
        
        # Create SVG QR code
        qr = qrcode.QRCode(
            version=None,
            error_correction=error_map[error_level],
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        # Use SVG image factory
        from qrcode.image.svg import SvgPathImage
        img = qr.make_image(image_factory=SvgPathImage, fill_color=fg_color, back_color=bg_color)
        img.save(file_path)
        
    def add_to_history(self, text):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if same text exists
        for item in self.history:
            if item["text"] == text:
                item["timestamp"] = timestamp
                item["count"] += 1
                self.save_history()
                self.update_history_display()
                return
        
        # Add new entry
        self.history.insert(0, {
            "text": text,
            "timestamp": timestamp,
            "count": 1
        })
        
        # Keep only last 20 entries
        self.history = self.history[:20]
        
        self.save_history()
        self.update_history_display()
        
    def update_history_display(self):
        # Clear existing items
        for widget in self.history_frame.winfo_children():
            widget.destroy()
            
        if not self.history:
            no_history = ctk.CTkLabel(self.history_frame,
                                     text="No history yet",
                                     text_color="gray")
            no_history.pack(pady=20)
            return
            
        # Display items
        for item in self.history:
            item_frame = ctk.CTkFrame(self.history_frame,
                                     fg_color=("#f9fafb", "#374151"),
                                     corner_radius=10,
                                     height=50)
            item_frame.pack(fill="x", pady=3, padx=5)
            item_frame.pack_propagate(False)
            
            # Text
            display_text = item["text"][:45] + "..." if len(item["text"]) > 45 else item["text"]
            text_label = ctk.CTkLabel(item_frame,
                                     text=display_text,
                                     font=ctk.CTkFont(size=12),
                                     anchor="w")
            text_label.pack(side="left", padx=15, pady=10, fill="x", expand=True)
            
            # Count badge
            if item["count"] > 1:
                count_label = ctk.CTkLabel(item_frame,
                                          text=f"×{item['count']}",
                                          font=ctk.CTkFont(size=10),
                                          fg_color=("#3b82f6", "#2563eb"),
                                          corner_radius=10,
                                          width=30,
                                          height=25)
                count_label.pack(side="right", padx=5)
            
            # Time
            time_label = ctk.CTkLabel(item_frame,
                                     text=item["timestamp"].split()[1],
                                     font=ctk.CTkFont(size=10),
                                     text_color="gray")
            time_label.pack(side="right", padx=10)
            
    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
            
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
                self.history = []
                
    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="☀️")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="🌙")
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AdvancedQRGenerator()
    app.run()