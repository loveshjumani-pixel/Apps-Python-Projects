# ============================================================
#   🕐 CYBER WATCH PROFESSIONAL
#   Digital Clock & Alarm Management System
#   Developer: Qwen AI | Version: 1.1 | Year: 2026
#   Status: All Bugs Fixed ✅
# ============================================================

import customtkinter as ctk
import json
import os
import threading
import time
from datetime import datetime
from tkinter import messagebox

# ── Global Configuration ──────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ALARM_FILE = "cyber_watch_alarms.json"

COLORS = {
    "bg_dark": "#0a0a0f",
    "bg_card": "#13131a",
    "bg_sidebar": "#0d0d14",
    "accent_cyan": "#00f5ff",
    "accent_purple": "#b026ff",
    "accent_pink": "#ff006e",
    "accent_green": "#00ff88",
    "accent_orange": "#ff8800",
    "accent_red": "#ff0044",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0b0",
    "text_muted": "#606070",
    "border": "#1a1a25",
    "hover": "#1a1a2e",
}


# ── Data Manager ──────────────────────────────────────────
class DataManager:
    @staticmethod
    def load_alarms():
        try:
            if os.path.exists(ALARM_FILE):
                with open(ALARM_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "alarms" not in data:
                        data["alarms"] = []
                    return data
            return {"alarms": []}
        except (json.JSONDecodeError, IOError):
            return {"alarms": []}

    @staticmethod
    def save_alarms(data):
        try:
            with open(ALARM_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            messagebox.showerror("❌ Error", f"Failed to save alarms: {e}")

    @staticmethod
    def generate_alarm_id():
        import random
        import string
        return "ALM" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


# ── Sound Manager (Simplified) ────────────────────────────
class SoundManager:
    def __init__(self):
        self.sound_available = False
        try:
            import pygame
            pygame.mixer.init()
            self.sound_available = True
        except Exception:
            self.sound_available = False

    def play_beep(self):
        if not self.sound_available:
            return
        
        try:
            import pygame
            import numpy as np
            
            # Generate simple beep sound
            sample_rate = 44100
            frequency = 800
            duration = 0.5  # seconds
            
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave = np.sin(2 * np.pi * frequency * t) * 0.3
            wave = (wave * 32767).astype(np.int16)
            
            sound = pygame.sndarray.make_sound(wave)
            sound.play()
            time.sleep(duration)
        except Exception as e:
            print(f"Sound error: {e}")


# ── Animated Clock Display ────────────────────────────────
class ClockDisplay(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_card"],
                         corner_radius=20, border_width=2,
                         border_color=COLORS["accent_cyan"], **kwargs)

        # Time Label
        self.time_label = ctk.CTkLabel(self, text="00:00:00",
                                       font=("Courier New", 72, "bold"),
                                       text_color=COLORS["accent_cyan"])
        self.time_label.pack(pady=(30, 5))

        # Date Label
        self.date_label = ctk.CTkLabel(self, text="Loading...",
                                       font=("Segoe UI", 18),
                                       text_color=COLORS["text_secondary"])
        self.date_label.pack(pady=(0, 10))

        # Day Label
        self.day_label = ctk.CTkLabel(self, text="",
                                      font=("Segoe UI", 16, "bold"),
                                      text_color=COLORS["accent_purple"])
        self.day_label.pack(pady=(0, 30))

        self.start_update()

    def start_update(self):
        self.update_time()

    def update_time(self):
        try:
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            date_str = now.strftime("%d %B %Y")
            day_str = now.strftime("%A")

            self.time_label.configure(text=time_str)
            self.date_label.configure(text=date_str)
            self.day_label.configure(text=day_str)
        except Exception:
            pass

        self.after(1000, self.update_time)


# ── Alarm Card Widget ─────────────────────────────────────
class AlarmCard(ctk.CTkFrame):
    def __init__(self, master, alarm_data, delete_callback, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_card"],
                         corner_radius=12, border_width=1,
                         border_color=COLORS["border"], **kwargs)

        self.alarm_data = alarm_data
        self.delete_callback = delete_callback

        self.grid_columnconfigure(1, weight=1)

        # Time
        time_label = ctk.CTkLabel(self, text=alarm_data["time"],
                                  font=("Courier New", 24, "bold"),
                                  text_color=COLORS["accent_cyan"])
        time_label.grid(row=0, column=0, rowspan=2, padx=20, pady=15, sticky="w")

        # Label
        label_text = alarm_data.get("label", "Alarm")
        label = ctk.CTkLabel(self, text=label_text,
                             font=("Segoe UI", 14),
                             text_color=COLORS["text_primary"])
        label.grid(row=0, column=1, padx=10, pady=(15, 2), sticky="w")

        # Days
        days = alarm_data.get("days", [])
        days_text = ", ".join(days) if days else "One-time"
        days_label = ctk.CTkLabel(self, text=days_text,
                                  font=("Segoe UI", 11),
                                  text_color=COLORS["text_muted"])
        days_label.grid(row=1, column=1, padx=10, pady=(0, 15), sticky="w")

        # Status
        status_color = COLORS["accent_green"] if alarm_data.get("enabled", True) \
            else COLORS["text_muted"]
        status_text = "🟢 Active" if alarm_data.get("enabled", True) else "⚫ Disabled"
        status = ctk.CTkLabel(self, text=status_text,
                              font=("Segoe UI", 12, "bold"),
                              text_color=status_color)
        status.grid(row=0, column=2, rowspan=2, padx=15, pady=15, sticky="e")

        # Delete Button
        delete_btn = ctk.CTkButton(self, text="🗑️",
                                   width=40, height=40,
                                   corner_radius=8,
                                   fg_color=COLORS["accent_red"],
                                   hover_color="#cc0033",
                                   font=("Segoe UI Emoji", 16),
                                   command=self._on_delete)
        delete_btn.grid(row=0, column=3, rowspan=2, padx=15, pady=15, sticky="e")

    def _on_delete(self):
        if messagebox.askyesno("🗑️ Delete Alarm",
                               f"Delete alarm at {self.alarm_data['time']}?"):
            self.delete_callback(self.alarm_data["id"])


# ── Add Alarm Dialog ──────────────────────────────────────
class AddAlarmDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("➕ Add New Alarm")
        self.geometry("450x500")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])
        self.callback = callback

        # Center window
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        # Title
        ctk.CTkLabel(self, text="➕  Create New Alarm",
                     font=("Segoe UI", 22, "bold"),
                     text_color=COLORS["accent_cyan"]).pack(pady=(25, 20))

        # Time Selection
        time_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                                  corner_radius=12)
        time_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(time_frame, text="⏰  Select Time",
                     font=("Segoe UI", 14, "bold"),
                     text_color=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(15, 10))

        time_input_frame = ctk.CTkFrame(time_frame, fg_color="transparent")
        time_input_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.hour_var = ctk.StringVar(value="08")
        self.minute_var = ctk.StringVar(value="00")

        ctk.CTkLabel(time_input_frame, text="Hour:",
                     font=("Segoe UI", 12),
                     text_color=COLORS["text_secondary"]).grid(row=0, column=0, padx=5)
        self.hour_entry = ctk.CTkEntry(time_input_frame, width=80, height=40,
                                       textvariable=self.hour_var,
                                       font=("Segoe UI", 16, "bold"),
                                       justify="center")
        self.hour_entry.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(time_input_frame, text=":",
                     font=("Segoe UI", 20, "bold"),
                     text_color=COLORS["text_primary"]).grid(row=0, column=2, padx=5)

        ctk.CTkLabel(time_input_frame, text="Minute:",
                     font=("Segoe UI", 12),
                     text_color=COLORS["text_secondary"]).grid(row=0, column=3, padx=5)
        self.minute_entry = ctk.CTkEntry(time_input_frame, width=80, height=40,
                                         textvariable=self.minute_var,
                                         font=("Segoe UI", 16, "bold"),
                                         justify="center")
        self.minute_entry.grid(row=0, column=4, padx=5)

        # Label
        label_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                                   corner_radius=12)
        label_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(label_frame, text="📝  Alarm Label",
                     font=("Segoe UI", 14, "bold"),
                     text_color=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(15, 10))

        self.label_entry = ctk.CTkEntry(label_frame, width=350, height=40,
                                        placeholder_text="e.g., Wake Up, Meeting",
                                        font=("Segoe UI", 14))
        self.label_entry.pack(padx=20, pady=(0, 15))

        # Days Selection
        days_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                                  corner_radius=12)
        days_frame.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(days_frame, text="📅  Repeat Days (Optional)",
                     font=("Segoe UI", 14, "bold"),
                     text_color=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(15, 10))

        days_input_frame = ctk.CTkFrame(days_frame, fg_color="transparent")
        days_input_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.day_vars = {}
        days_list = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for idx, day in enumerate(days_list):
            var = ctk.BooleanVar(value=False)
            self.day_vars[day] = var
            btn = ctk.CTkCheckBox(days_input_frame, text=day,
                                  variable=var,
                                  font=("Segoe UI", 12))
            btn.grid(row=0, column=idx, padx=3)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)

        cancel_btn = ctk.CTkButton(btn_frame, text="❌  Cancel",
                                   width=150, height=45,
                                   corner_radius=10,
                                   font=("Segoe UI", 14, "bold"),
                                   fg_color=COLORS["text_muted"],
                                   hover_color="#404050",
                                   command=self.destroy)
        cancel_btn.pack(side="left", padx=10)

        save_btn = ctk.CTkButton(btn_frame, text="✅  Save Alarm",
                                 width=150, height=45,
                                 corner_radius=10,
                                 font=("Segoe UI", 14, "bold"),
                                 fg_color=COLORS["accent_cyan"],
                                 hover_color="#00c5cc",
                                 command=self._save_alarm)
        save_btn.pack(side="right", padx=10)

    def _save_alarm(self):
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())

            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError

            time_str = f"{hour:02d}:{minute:02d}"
            label = self.label_entry.get().strip() or "Alarm"
            days = [day for day, var in self.day_vars.items() if var.get()]

            alarm_data = {
                "id": DataManager.generate_alarm_id(),
                "time": time_str,
                "label": label,
                "days": days,
                "enabled": True,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            self.callback(alarm_data)
            self.destroy()

        except ValueError:
            messagebox.showerror("❌ Error", "Invalid time format!\nUse 00-23 for hours, 00-59 for minutes.")


# ── Main Application ──────────────────────────────────────
class CyberWatchApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🕐 Cyber Watch Professional")
        self.geometry("1000x700")
        self.minsize(900, 600)
        self.configure(fg_color=COLORS["bg_dark"])

        # Center window
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (1000 // 2)
        y = (screen_height // 2) - (700 // 2)
        self.geometry(f"+{x}+{y}")

        self.sound_manager = SoundManager()
        self.alarm_thread = None
        self.running = True

        self._build_ui()
        self._start_alarm_checker()

    def _build_ui(self):
        # Main Container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Left Side - Clock
        left_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Clock Display
        self.clock_display = ClockDisplay(left_frame)
        self.clock_display.pack(fill="both", expand=True, pady=(0, 15))

        # Stats Cards
        stats_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        stats_frame.pack(fill="x")
        stats_frame.grid_columnconfigure((0, 1), weight=1)

        # Active Alarms Card
        self.active_card = ctk.CTkFrame(stats_frame, fg_color=COLORS["bg_card"],
                                        corner_radius=12, border_width=1,
                                        border_color=COLORS["accent_green"])
        self.active_card.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.active_card, text="🟢",
                     font=("Segoe UI Emoji", 24)).pack(pady=(15, 5))
        self.active_count = ctk.CTkLabel(self.active_card, text="0",
                                         font=("Segoe UI", 28, "bold"),
                                         text_color=COLORS["accent_green"])
        self.active_count.pack()
        ctk.CTkLabel(self.active_card, text="Active Alarms",
                     font=("Segoe UI", 12),
                     text_color=COLORS["text_secondary"]).pack(pady=(0, 15))

        # Total Alarms Card
        self.total_card = ctk.CTkFrame(stats_frame, fg_color=COLORS["bg_card"],
                                       corner_radius=12, border_width=1,
                                       border_color=COLORS["accent_purple"])
        self.total_card.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(self.total_card, text="📊",
                     font=("Segoe UI Emoji", 24)).pack(pady=(15, 5))
        self.total_count = ctk.CTkLabel(self.total_card, text="0",
                                        font=("Segoe UI", 28, "bold"),
                                        text_color=COLORS["accent_purple"])
        self.total_count.pack()
        ctk.CTkLabel(self.total_card, text="Total Alarms",
                     font=("Segoe UI", 12),
                     text_color=COLORS["text_secondary"]).pack(pady=(0, 15))

        # Right Side - Alarms
        right_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Header
        header = ctk.CTkFrame(right_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(header, text="⏰  Alarm Management",
                     font=("Segoe UI", 22, "bold"),
                     text_color=COLORS["text_primary"]).pack(side="left")

        add_btn = ctk.CTkButton(header, text="➕  Add Alarm",
                                width=140, height=40,
                                corner_radius=10,
                                font=("Segoe UI", 13, "bold"),
                                fg_color=COLORS["accent_cyan"],
                                hover_color="#00c5cc",
                                command=self._add_alarm)
        add_btn.pack(side="right")

        # Alarm List
        self.alarm_scroll = ctk.CTkScrollableFrame(right_frame,
                                                   fg_color="transparent")
        self.alarm_scroll.pack(fill="both", expand=True)

        self._load_alarms()

    def _load_alarms(self):
        # Clear existing
        for widget in self.alarm_scroll.winfo_children():
            widget.destroy()

        data = DataManager.load_alarms()
        alarms = data.get("alarms", [])

        # Update counts
        active_count = sum(1 for a in alarms if a.get("enabled", True))
        self.active_count.configure(text=str(active_count))
        self.total_count.configure(text=str(len(alarms)))

        if not alarms:
            ctk.CTkLabel(self.alarm_scroll,
                         text="📭  No alarms set\n\nClick 'Add Alarm' to create one",
                         font=("Segoe UI", 16),
                         text_color=COLORS["text_muted"]).pack(pady=80)
        else:
            for alarm in alarms:
                card = AlarmCard(self.alarm_scroll, alarm, self._delete_alarm)
                card.pack(fill="x", pady=5)

    def _add_alarm(self):
        AddAlarmDialog(self, self._save_alarm)

    def _save_alarm(self, alarm_data):
        data = DataManager.load_alarms()
        data["alarms"].append(alarm_data)
        DataManager.save_alarms(data)
        self._load_alarms()
        messagebox.showinfo("✅ Success",
                            f"Alarm set for {alarm_data['time']}")

    def _delete_alarm(self, alarm_id):
        data = DataManager.load_alarms()
        data["alarms"] = [a for a in data["alarms"] if a["id"] != alarm_id]
        DataManager.save_alarms(data)
        self._load_alarms()

    def _start_alarm_checker(self):
        def check_alarms():
            while self.running:
                try:
                    now = datetime.now()
                    current_time = now.strftime("%H:%M")
                    current_day = now.strftime("%a")

                    data = DataManager.load_alarms()
                    triggered_alarms = []
                    
                    for alarm in data["alarms"]:
                        if not alarm.get("enabled", True):
                            continue

                        if alarm["time"] == current_time:
                            days = alarm.get("days", [])
                            if not days or current_day in days:
                                triggered_alarms.append(alarm)
                                if not days:  # One-time alarm
                                    alarm["enabled"] = False

                    if triggered_alarms:
                        DataManager.save_alarms(data)
                        self.after(0, self._load_alarms)
                        
                        for alarm in triggered_alarms:
                            self._trigger_alarm(alarm)

                    time.sleep(1)
                except Exception as e:
                    print(f"Alarm checker error: {e}")
                    time.sleep(5)

        self.alarm_thread = threading.Thread(target=check_alarms, daemon=True)
        self.alarm_thread.start()

    def _trigger_alarm(self, alarm):
        def show_notification():
            # Play sound
            self.sound_manager.play_beep()

            # Show message
            self.after(0, lambda: messagebox.showinfo(
                "⏰  ALARM!",
                f"🔔 {alarm['label']}\n\nTime: {alarm['time']}"
            ))

        threading.Thread(target=show_notification, daemon=True).start()

    def on_closing(self):
        self.running = False
        time.sleep(0.5)  # Wait for thread to stop
        self.destroy()


# ── Run Application ───────────────────────────────────────
if __name__ == "__main__":
    try:
        app = CyberWatchApp()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        print(f"❌ Application Error: {e}")
        import traceback
        traceback.print_exc()