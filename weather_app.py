import tkinter as tk
from tkinter import font as tkfont
import urllib.request
import urllib.parse
import json
import threading
from datetime import datetime
import math

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")
        self.root.geometry("450x820")
        self.root.resizable(False, False)
        self.root.configure(bg="#0F172A")

        # ── Safe Font Detection ──
        self.font_family = self._get_safe_font()

        # ── Color Palette ──
        self.colors = {
            "bg_dark":        "#0F172A",
            "bg_medium":      "#1E293B",
            "card":           "#1E293B",
            "card_light":     "#334155",
            "card_border":    "#334155",
            "text_primary":   "#F8FAFC",
            "text_secondary": "#94A3B8",
            "accent_blue":    "#38BDF8",
            "accent_amber":   "#F59E0B",
            "accent_cyan":    "#06B6D4",
            "accent_green":   "#10B981",
            "accent_red":     "#EF4444",
            "input_bg":       "#1E293B",
            "input_border":   "#475569",
            "btn_bg":         "#38BDF8",
            "btn_fg":         "#0F172A",
        }

        self._build_ui()
        self._load_weather("Islamabad")

    def _get_safe_font(self):
        """Get a font that exists on the system"""
        try:
            available = tkfont.families()
            for name in ["Segoe UI", "SF Pro Display", "Helvetica", "Arial"]:
                if name in available:
                    return name
        except Exception:
            pass
        return "Helvetica"

    # ═══════════════════════════════════════
    #  UI CONSTRUCTION
    # ═══════════════════════════════════════
    def _build_ui(self):
        # ── Main Background Frame ──
        self.main = tk.Frame(self.root, bg=self.colors["bg_dark"])
        self.main.pack(fill="both", expand=True)

        # ── Gradient Canvas at Top ──
        self.gradient_canvas = tk.Canvas(
            self.main, height=200,
            bg=self.colors["bg_dark"],
            highlightthickness=0, bd=0
        )
        self.gradient_canvas.pack(fill="x")
        self.gradient_canvas.bind("<Configure>", self._draw_gradient)

        # ── Header ──
        header = tk.Frame(self.main, bg=self.colors["bg_dark"])
        header.pack(fill="x", padx=25, pady=(10, 15))

        # Custom weather icon (Canvas)
        icon_canvas = tk.Canvas(
            header, width=40, height=40,
            bg=self.colors["bg_dark"],
            highlightthickness=0
        )
        icon_canvas.pack(side="left", padx=(0, 10))
        self._draw_weather_icon(icon_canvas)

        tk.Label(
            header, text="Weather",
            font=(self.font_family, 24, "bold"),
            bg=self.colors["bg_dark"], fg=self.colors["accent_blue"]
        ).pack(side="left")

        now = datetime.now().strftime("%b %d, %Y")
        tk.Label(
            header, text=now,
            font=(self.font_family, 10),
            bg=self.colors["bg_dark"], fg=self.colors["text_secondary"]
        ).pack(side="right", pady=(10, 0))

        # ── Search Bar ──
        search_frame = tk.Frame(
            self.main, bg=self.colors["card"],
            highlightbackground=self.colors["input_border"],
            highlightthickness=1
        )
        search_frame.pack(fill="x", padx=25, pady=(0, 20))

        tk.Label(
            search_frame, text="🔍",
            font=(self.font_family, 14),
            bg=self.colors["card"]
        ).pack(side="left", padx=(15, 8), pady=12)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame, textvariable=self.search_var,
            font=(self.font_family, 13),
            bg=self.colors["card"],
            fg=self.colors["text_primary"],
            insertbackground=self.colors["accent_blue"],
            bd=0, relief="flat"
        )
        self.search_entry.pack(side="left", fill="x", expand=True, pady=12)
        self.search_entry.insert(0, "Enter city name...")
        self.search_entry.config(fg=self.colors["text_secondary"])
        self.search_entry.bind("<FocusIn>", self._on_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_focus_out)
        self.search_entry.bind("<Return>", lambda e: self._search())

        search_btn = tk.Button(
            search_frame, text="Search",
            font=(self.font_family, 11, "bold"),
            bg=self.colors["btn_bg"], fg=self.colors["btn_fg"],
            activebackground="#0EA5E9", activeforeground=self.colors["btn_fg"],
            bd=0, cursor="hand2", relief="flat",
            command=self._search
        )
        search_btn.pack(side="right", padx=8, pady=8, ipadx=15, ipady=4)

        # ── Content Area ──
        self.content = tk.Frame(self.main, bg=self.colors["bg_dark"])
        self.content.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        # Loading
        self.loading_lbl = tk.Label(
            self.content, text="⏳ Loading weather data...",
            font=(self.font_family, 13),
            bg=self.colors["bg_dark"], fg=self.colors["text_secondary"]
        )
        self.loading_lbl.pack(pady=150)

    def _draw_gradient(self, event=None):
        """Draw beautiful gradient on top canvas"""
        self.gradient_canvas.delete("all")
        width = self.gradient_canvas.winfo_width()
        height = self.gradient_canvas.winfo_height()

        steps = 60
        for i in range(steps):
            ratio = i / steps
            # Top: deep blue -> Bottom: dark navy
            r = int(30 + (15 - 30) * ratio)
            g = int(58 + (23 - 58) * ratio)
            b = int(138 + (42 - 138) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            y1 = int(height * i / steps)
            y2 = int(height * (i + 1) / steps)
            self.gradient_canvas.create_rectangle(0, y1, width, y2, fill=color, outline="")

        # Add decorative circles
        self.gradient_canvas.create_oval(
            width - 120, -40, width + 40, 120,
            fill="#F59E0B", outline=""
        )
        self.gradient_canvas.create_oval(
            width - 100, -20, width + 20, 100,
            fill="#FB923C", outline=""
        )

    def _draw_weather_icon(self, canvas):
        """Draw custom sun icon"""
        # Sun body
        canvas.create_oval(10, 10, 30, 30, fill="#F59E0B", outline="")
        # Rays
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = 20 + 11 * math.cos(rad)
            y1 = 20 + 11 * math.sin(rad)
            x2 = 20 + 15 * math.cos(rad)
            y2 = 20 + 15 * math.sin(rad)
            canvas.create_line(x1, y1, x2, y2, fill="#F59E0B", width=2)

    def _on_focus_in(self, event):
        if self.search_entry.get() == "Enter city name...":
            self.search_entry.delete(0, "end")
            self.search_entry.config(fg=self.colors["text_primary"])

    def _on_focus_out(self, event):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Enter city name...")
            self.search_entry.config(fg=self.colors["text_secondary"])

    # ═══════════════════════════════════════
    #  SEARCH & API
    # ═══════════════════════════════════════
    def _search(self):
        city = self.search_var.get().strip()
        if not city or city == "Enter city name...":
            self._show_error("Please enter a city name")
            return
        self._load_weather(city)

    def _load_weather(self, city):
        self._clear_content()
        self.loading_lbl = tk.Label(
            self.content, text="⏳ Loading weather data...",
            font=(self.font_family, 13),
            bg=self.colors["bg_dark"], fg=self.colors["text_secondary"]
        )
        self.loading_lbl.pack(pady=150)

        thread = threading.Thread(target=self._fetch_weather, args=(city,), daemon=True)
        thread.start()

    def _fetch_weather(self, city):
        try:
            encoded = urllib.parse.quote(city)
            url = f"https://wttr.in/{encoded}?format=j1"
            req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            current = data["current_condition"][0]
            area = data["nearest_area"][0]

            weather_data = {
                "city": area["areaName"][0]["value"],
                "country": area["country"][0]["value"],
                "temp": current["temp_C"],
                "feels_like": current["FeelsLikeC"],
                "humidity": current["humidity"],
                "wind_speed": current["windspeedKmph"],
                "pressure": current["pressure"],
                "visibility": current["visibility"],
                "desc": current["weatherDesc"][0]["value"],
                "forecast": []
            }

            for day in data.get("weather", [])[:3]:
                hourly = day.get("hourly", [])
                noon = hourly[4] if len(hourly) > 4 else hourly[0]
                weather_data["forecast"].append({
                    "date": day["date"],
                    "max": day["maxtempC"],
                    "min": day["mintempC"],
                    "desc": noon["weatherDesc"][0]["value"]
                })

            self.root.after(0, lambda: self._display_weather(weather_data))

        except urllib.error.HTTPError as e:
            if e.code == 404:
                self.root.after(0, lambda: self._show_error(f"City '{city}' not found"))
            else:
                self.root.after(0, lambda: self._show_error(f"Network error: {e.code}"))
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"Error: {str(e)[:50]}"))

    # ═══════════════════════════════════════
    #  DISPLAY
    # ═══════════════════════════════════════
    def _clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def _show_error(self, msg):
        self._clear_content()
        err_frame = tk.Frame(self.content, bg=self.colors["bg_dark"])
        err_frame.pack(pady=100)

        tk.Label(err_frame, text="⚠️", font=(self.font_family, 56),
                 bg=self.colors["bg_dark"]).pack()
        tk.Label(err_frame, text=msg, font=(self.font_family, 13),
                 bg=self.colors["bg_dark"], fg=self.colors["accent_red"]).pack(pady=(15, 0))

        tk.Button(
            err_frame, text="Try Again",
            font=(self.font_family, 11, "bold"),
            bg=self.colors["btn_bg"], fg=self.colors["btn_fg"],
            bd=0, cursor="hand2", relief="flat",
            command=lambda: self._load_weather("Islamabad")
        ).pack(pady=20, ipadx=20, ipady=6)

    def _make_card(self, parent, height=None):
        """Create a styled card frame"""
        card = tk.Frame(
            parent, bg=self.colors["card"],
            highlightbackground=self.colors["card_border"],
            highlightthickness=1
        )
        if height:
            card.configure(height=height)
            card.pack_propagate(False)
        return card

    def _display_weather(self, data):
        self._clear_content()

        # ── Main Weather Card ──
        main_card = self._make_card(self.content, 220)
        main_card.pack(fill="x", pady=(0, 12))

        # City
        tk.Label(
            main_card, text=f"📍 {data['city']}, {data['country']}",
            font=(self.font_family, 15, "bold"),
            bg=self.colors["card"], fg=self.colors["text_primary"],
            anchor="w"
        ).pack(fill="x", padx=22, pady=(20, 0))

        tk.Label(
            main_card, text=data["desc"],
            font=(self.font_family, 11),
            bg=self.colors["card"], fg=self.colors["text_secondary"]
        ).pack(anchor="w", padx=22, pady=(2, 0))

        # Temp row
        temp_row = tk.Frame(main_card, bg=self.colors["card"])
        temp_row.pack(fill="x", padx=22, pady=(15, 10))

        # Weather icon canvas
        big_icon = tk.Canvas(temp_row, width=80, height=80,
                             bg=self.colors["card"], highlightthickness=0)
        big_icon.pack(side="left")
        self._draw_big_weather_icon(big_icon, data["desc"])

        tk.Label(
            temp_row, text=f"{data['temp']}°C",
            font=(self.font_family, 48, "bold"),
            bg=self.colors["card"], fg=self.colors["text_primary"]
        ).pack(side="right")

        tk.Label(
            main_card, text=f"Feels like {data['feels_like']}°C",
            font=(self.font_family, 10),
            bg=self.colors["card"], fg=self.colors["text_secondary"]
        ).pack(anchor="e", padx=22, pady=(0, 18))

        # ── Info Grid ──
        info_grid = tk.Frame(self.content, bg=self.colors["bg_dark"])
        info_grid.pack(fill="x", pady=(0, 12))
        info_grid.columnconfigure(0, weight=1, uniform="col")
        info_grid.columnconfigure(1, weight=1, uniform="col")

        info_items = [
            ("💧", "Humidity", f"{data['humidity']}%", self.colors["accent_cyan"]),
            ("💨", "Wind", f"{data['wind_speed']} km/h", self.colors["accent_blue"]),
            ("🌡️", "Pressure", f"{data['pressure']} hPa", self.colors["accent_amber"]),
            ("👁️", "Visibility", f"{data['visibility']} km", self.colors["accent_green"]),
        ]

        for i, (emoji, label, value, color) in enumerate(info_items):
            row, col = i // 2, i % 2
            card = tk.Frame(
                info_grid, bg=self.colors["card"],
                highlightbackground=self.colors["card_border"],
                highlightthickness=1, height=100
            )
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            card.grid_propagate(False)

            # Colored accent bar
            tk.Frame(card, bg=color, width=4).place(x=12, y=15, height=70)

            tk.Label(card, text=emoji, font=(self.font_family, 22),
                     bg=self.colors["card"]).place(x=28, y=12)
            tk.Label(card, text=label, font=(self.font_family, 9),
                     bg=self.colors["card"], fg=self.colors["text_secondary"]).place(x=28, y=48)
            tk.Label(card, text=value, font=(self.font_family, 13, "bold"),
                     bg=self.colors["card"], fg=self.colors["text_primary"]).place(x=28, y=66)

        # ── Forecast ──
        tk.Label(
            self.content, text="📅  3-Day Forecast",
            font=(self.font_family, 14, "bold"),
            bg=self.colors["bg_dark"], fg=self.colors["text_primary"],
            anchor="w"
        ).pack(fill="x", pady=(8, 8))

        for day_data in data["forecast"]:
            self._create_forecast_card(day_data)

    def _draw_big_weather_icon(self, canvas, desc):
        """Draw big weather icon based on description"""
        desc_lower = desc.lower()
        canvas.delete("all")

        if any(x in desc_lower for x in ["clear", "sunny"]):
            # Sun
            canvas.create_oval(15, 15, 65, 65, fill="#F59E0B", outline="")
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x1 = 40 + 28 * math.cos(rad)
                y1 = 40 + 28 * math.sin(rad)
                x2 = 40 + 36 * math.cos(rad)
                y2 = 40 + 36 * math.sin(rad)
                canvas.create_line(x1, y1, x2, y2, fill="#F59E0B", width=3)
        elif any(x in desc_lower for x in ["cloud", "overcast"]):
            # Cloud
            canvas.create_oval(10, 30, 45, 65, fill="#94A3B8", outline="")
            canvas.create_oval(25, 15, 65, 55, fill="#CBD5E1", outline="")
            canvas.create_oval(45, 30, 75, 65, fill="#94A3B8", outline="")
            canvas.create_rectangle(15, 50, 70, 70, fill="#94A3B8", outline="")
        elif any(x in desc_lower for x in ["rain", "drizzle", "shower"]):
            # Cloud + rain
            canvas.create_oval(10, 15, 45, 50, fill="#64748B", outline="")
            canvas.create_oval(25, 5, 65, 45, fill="#94A3B8", outline="")
            canvas.create_oval(45, 15, 75, 50, fill="#64748B", outline="")
            canvas.create_rectangle(15, 35, 70, 55, fill="#64748B", outline="")
            # Rain drops
            for x in [20, 35, 50, 65]:
                canvas.create_line(x, 60, x-3, 72, fill="#38BDF8", width=2)
        elif "snow" in desc_lower:
            # Snowflake
            for angle in range(0, 360, 60):
                rad = math.radians(angle)
                x2 = 40 + 25 * math.cos(rad)
                y2 = 40 + 25 * math.sin(rad)
                canvas.create_line(40, 40, x2, y2, fill="#E0F2FE", width=3)
        elif any(x in desc_lower for x in ["thunder", "storm"]):
            # Storm cloud + lightning
            canvas.create_oval(10, 15, 45, 50, fill="#475569", outline="")
            canvas.create_oval(25, 5, 65, 45, fill="#64748B", outline="")
            canvas.create_oval(45, 15, 75, 50, fill="#475569", outline="")
            canvas.create_rectangle(15, 35, 70, 55, fill="#475569", outline="")
            # Lightning
            canvas.create_polygon(35, 55, 45, 55, 40, 68, 50, 68, 30, 80, 38, 70, 28, 70,
                                  fill="#FCD34D", outline="")
        else:
            # Default: thermometer
            canvas.create_oval(30, 50, 50, 70, fill="#EF4444", outline="")
            canvas.create_rectangle(35, 15, 45, 60, fill="#EF4444", outline="")
            canvas.create_rectangle(33, 10, 47, 65, outline="#94A3B8", width=2)

    def _create_forecast_card(self, day_data):
        card = tk.Frame(
            self.content, bg=self.colors["card"],
            highlightbackground=self.colors["card_border"],
            highlightthickness=1, height=80
        )
        card.pack(fill="x", pady=4)
        card.pack_propagate(False)

        try:
            dt = datetime.strptime(day_data["date"], "%Y-%m-%d")
            day_name = dt.strftime("%a")
            day_date = dt.strftime("%b %d")
        except Exception:
            day_name = day_data["date"]
            day_date = ""

        # Day name
        tk.Label(card, text=day_name, font=(self.font_family, 13, "bold"),
                 bg=self.colors["card"], fg=self.colors["text_primary"]).place(x=20, y=15)
        tk.Label(card, text=day_date, font=(self.font_family, 9),
                 bg=self.colors["card"], fg=self.colors["text_secondary"]).place(x=20, y=42)

        # Icon + desc
        icon = self._get_emoji(day_data["desc"])
        tk.Label(card, text=f"{icon}  {day_data['desc']}", font=(self.font_family, 11),
                 bg=self.colors["card"], fg=self.colors["text_primary"]).place(relx=0.5, rely=0.5, anchor="center")

        # Temps
        tk.Label(card, text=f"{day_data['max']}°", font=(self.font_family, 14, "bold"),
                 bg=self.colors["card"], fg=self.colors["accent_amber"]).place(relx=1.0, x=-25, y=15, anchor="e")
        tk.Label(card, text=f"{day_data['min']}°", font=(self.font_family, 11),
                 bg=self.colors["card"], fg=self.colors["text_secondary"]).place(relx=1.0, x=-25, y=45, anchor="e")

    def _get_emoji(self, desc):
        desc_lower = desc.lower()
        icons = {
            "clear": "☀️", "sunny": "☀️",
            "clouds": "☁️", "cloudy": "☁️", "overcast": "☁️",
            "rain": "🌧️", "drizzle": "🌦️", "shower": "🌦️",
            "mist": "🌫️", "fog": "🌫️", "haze": "🌫️",
            "snow": "❄️", "thunder": "⛈️", "storm": "⛈️",
        }
        for key, emoji in icons.items():
            if key in desc_lower:
                return emoji
        return "🌡️"


# ═══════════════════════════════════════
#  RUN
# ═══════════════════════════════════════
if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.update_idletasks()
        w, h = 450, 820
        x = (root.winfo_screenwidth() // 2) - (w // 2)
        y = (root.winfo_screenheight() // 2) - (h // 2)
        root.geometry(f"{w}x{h}+{x}+{y}")

        app = WeatherApp(root)
        root.mainloop()
    except tk.TclError as e:
        print(f"TclError: {e}")
    except Exception as e:
        print(f"Error: {e}")