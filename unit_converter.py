import tkinter as tk
from tkinter import ttk, messagebox

class UnitConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Unit Converter - Professional")
        self.root.geometry("1050x680")
        self.root.minsize(900, 600)
        self.root.configure(bg="#eef2f7")

        # Color palette
        self.colors = {
            "bg": "#eef2f7",
            "sidebar": "#1e293b",
            "sidebar_active": "#3b82f6",
            "card": "#ffffff",
            "primary": "#3b82f6",
            "primary_dark": "#2563eb",
            "accent": "#8b5cf6",
            "success": "#10b981",
            "danger": "#ef4444",
            "text": "#1e293b",
            "muted": "#64748b",
            "border": "#e2e8f0",
            "input_bg": "#f8fafc"
        }

        # Conversion data
        self.categories = {
            "Length": {
                "icon": "L", "base": "meter",
                "units": {
                    "Millimeter (mm)": 0.001,
                    "Centimeter (cm)": 0.01,
                    "Meter (m)": 1.0,
                    "Kilometer (km)": 1000.0,
                    "Inch (in)": 0.0254,
                    "Foot (ft)": 0.3048,
                    "Yard (yd)": 0.9144,
                    "Mile (mi)": 1609.344,
                    "Nautical Mile": 1852.0,
                }
            },
            "Weight": {
                "icon": "W", "base": "kilogram",
                "units": {
                    "Milligram (mg)": 1e-6,
                    "Gram (g)": 0.001,
                    "Kilogram (kg)": 1.0,
                    "Metric Ton (t)": 1000.0,
                    "Ounce (oz)": 0.028349523125,
                    "Pound (lb)": 0.45359237,
                    "Stone (st)": 6.35029318,
                }
            },
            "Temperature": {
                "icon": "T", "base": "kelvin",
                "special": True,
                "units": {
                    "Celsius (C)": "C",
                    "Fahrenheit (F)": "F",
                    "Kelvin (K)": "K",
                }
            },
            "Volume": {
                "icon": "V", "base": "liter",
                "units": {
                    "Milliliter (mL)": 0.001,
                    "Liter (L)": 1.0,
                    "Cubic Meter (m3)": 1000.0,
                    "Teaspoon (tsp)": 0.00492892,
                    "Tablespoon (tbsp)": 0.0147868,
                    "Fluid Ounce (fl oz)": 0.0295735,
                    "Cup (US)": 0.24,
                    "Pint (pt)": 0.473176,
                    "Quart (qt)": 0.946353,
                    "Gallon (US)": 3.78541,
                }
            },
            "Area": {
                "icon": "A", "base": "square meter",
                "units": {
                    "Square Millimeter (mm2)": 1e-6,
                    "Square Centimeter (cm2)": 1e-4,
                    "Square Meter (m2)": 1.0,
                    "Hectare (ha)": 10000.0,
                    "Square Kilometer (km2)": 1e6,
                    "Square Inch (in2)": 0.00064516,
                    "Square Foot (ft2)": 0.092903,
                    "Square Yard (yd2)": 0.836127,
                    "Acre": 4046.8564224,
                    "Square Mile (mi2)": 2589988.11,
                }
            },
            "Speed": {
                "icon": "S", "base": "m/s",
                "units": {
                    "Meter/second (m/s)": 1.0,
                    "Kilometer/hour (km/h)": 0.277778,
                    "Mile/hour (mph)": 0.44704,
                    "Foot/second (ft/s)": 0.3048,
                    "Knot (kn)": 0.514444,
                    "Mach (sea level)": 343.0,
                }
            },
            "Time": {
                "icon": "T", "base": "second",
                "units": {
                    "Millisecond (ms)": 0.001,
                    "Second (s)": 1.0,
                    "Minute (min)": 60.0,
                    "Hour (h)": 3600.0,
                    "Day": 86400.0,
                    "Week": 604800.0,
                    "Month (30 days)": 2592000.0,
                    "Year (365 days)": 31536000.0,
                }
            },
            "Data": {
                "icon": "D", "base": "byte",
                "units": {
                    "Bit (b)": 0.125,
                    "Byte (B)": 1.0,
                    "Kilobyte (KB)": 1024.0,
                    "Megabyte (MB)": 1024**2,
                    "Gigabyte (GB)": 1024**3,
                    "Terabyte (TB)": 1024**4,
                    "Petabyte (PB)": 1024**5,
                }
            },
            "Pressure": {
                "icon": "P", "base": "pascal",
                "units": {
                    "Pascal (Pa)": 1.0,
                    "Kilopascal (kPa)": 1000.0,
                    "Bar": 100000.0,
                    "PSI": 6894.757,
                    "Atmosphere (atm)": 101325.0,
                    "Torr (mmHg)": 133.322,
                }
            },
            "Energy": {
                "icon": "E", "base": "joule",
                "units": {
                    "Joule (J)": 1.0,
                    "Kilojoule (kJ)": 1000.0,
                    "Calorie (cal)": 4.184,
                    "Kilocalorie (kcal)": 4184.0,
                    "Watt-hour (Wh)": 3600.0,
                    "Kilowatt-hour (kWh)": 3600000.0,
                    "BTU": 1055.06,
                    "Electronvolt (eV)": 1.602176634e-19,
                }
            },
        }

        self.current_category = "Length"
        self.history = []
        self.max_history = 20
        self.last_history_entry = ""

        self._setup_styles()
        self._build_ui()
        self._bind_events()
        self._update_units()
        self._do_convert()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=self.colors["bg"])
        style.configure("TLabel", background=self.colors["card"],
                        foreground=self.colors["text"],
                        font=("Segoe UI", 10))
        style.configure("TCombobox", padding=8, font=("Segoe UI", 11))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.colors["primary"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="UNIT CONVERTER",
                 font=("Segoe UI", 16, "bold"),
                 bg=self.colors["primary"], fg="white").pack(side="left", padx=20, pady=15)

        tk.Label(header, text="Professional | Fast | Accurate",
                 font=("Segoe UI", 10, "italic"),
                 bg=self.colors["primary"], fg="#dbeafe").pack(side="right", padx=20)

        # Main container
        main = tk.Frame(self.root, bg=self.colors["bg"])
        main.pack(fill="both", expand=True, padx=15, pady=15)

        # Sidebar
        sidebar = tk.Frame(main, bg=self.colors["sidebar"], width=200)
        sidebar.pack(side="left", fill="y", padx=(0, 15))
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="CATEGORIES",
                 font=("Segoe UI", 10, "bold"),
                 bg=self.colors["sidebar"], fg="#94a3b8").pack(pady=(15, 10))

        self.cat_buttons = {}
        for name, data in self.categories.items():
            btn = tk.Button(sidebar,
                            text=f"  [{data['icon']}]  {name}",
                            font=("Segoe UI", 11),
                            bg=self.colors["sidebar"], fg="white",
                            activebackground=self.colors["sidebar_active"],
                            activeforeground="white",
                            bd=0, anchor="w", padx=15, pady=10,
                            cursor="hand2",
                            command=lambda n=name: self._select_category(n))
            btn.pack(fill="x", padx=8, pady=2)
            self.cat_buttons[name] = btn

        self._select_category("Length", init=True)

        # Right panel
        right = tk.Frame(main, bg=self.colors["bg"])
        right.pack(side="left", fill="both", expand=True)

        # Converter card
        conv_card = tk.Frame(right, bg=self.colors["card"],
                             highlightbackground=self.colors["border"],
                             highlightthickness=1)
        conv_card.pack(fill="x", pady=(0, 15))

        tk.Label(conv_card, text="CONVERTER",
                 font=("Segoe UI", 11, "bold"),
                 bg=self.colors["card"], fg=self.colors["muted"]).pack(anchor="w", padx=20, pady=(15, 10))

        # FROM row
        from_frame = tk.Frame(conv_card, bg=self.colors["card"])
        from_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(from_frame, text="FROM",
                 font=("Segoe UI", 9, "bold"),
                 bg=self.colors["card"], fg=self.colors["muted"]).pack(side="left")

        self.from_unit_var = tk.StringVar()
        self.from_unit_cb = ttk.Combobox(from_frame, textvariable=self.from_unit_var,
                                         state="readonly", font=("Segoe UI", 11))
        self.from_unit_cb.pack(side="right", fill="x", expand=True, padx=(15, 0))
        self.from_unit_cb.bind("<<ComboboxSelected>>", lambda e: self._do_convert())

        # Input
        input_frame = tk.Frame(conv_card, bg=self.colors["card"])
        input_frame.pack(fill="x", padx=20, pady=10)

        self.input_var = tk.StringVar(value="1")
        self.input_entry = tk.Entry(input_frame, textvariable=self.input_var,
                                    font=("Segoe UI", 22, "bold"),
                                    bg=self.colors["input_bg"],
                                    fg=self.colors["text"],
                                    bd=0, relief="flat",
                                    insertbackground=self.colors["primary"])
        self.input_entry.pack(fill="x", ipady=12, padx=10)
        self.input_entry.bind("<KeyRelease>", lambda e: self._do_convert())

        # Swap button
        swap_frame = tk.Frame(conv_card, bg=self.colors["card"])
        swap_frame.pack(pady=5)

        swap_btn = tk.Button(swap_frame, text="SWAP UNITS",
                             font=("Segoe UI", 10, "bold"),
                             bg=self.colors["accent"], fg="white",
                             activebackground="#7c3aed", activeforeground="white",
                             bd=0, padx=20, pady=8, cursor="hand2",
                             command=self._swap_units)
        swap_btn.pack()

        # TO row
        to_frame = tk.Frame(conv_card, bg=self.colors["card"])
        to_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(to_frame, text="TO",
                 font=("Segoe UI", 9, "bold"),
                 bg=self.colors["card"], fg=self.colors["muted"]).pack(side="left")

        self.to_unit_var = tk.StringVar()
        self.to_unit_cb = ttk.Combobox(to_frame, textvariable=self.to_unit_var,
                                       state="readonly", font=("Segoe UI", 11))
        self.to_unit_cb.pack(side="right", fill="x", expand=True, padx=(15, 0))
        self.to_unit_cb.bind("<<ComboboxSelected>>", lambda e: self._do_convert())

        # Result display
        result_frame = tk.Frame(conv_card, bg=self.colors["primary"])
        result_frame.pack(fill="x", padx=20, pady=(15, 20))

        self.result_var = tk.StringVar(value="-")
        result_label = tk.Label(result_frame, textvariable=self.result_var,
                                font=("Segoe UI", 20, "bold"),
                                bg=self.colors["primary"], fg="white",
                                anchor="w", justify="left", wraplength=700)
        result_label.pack(fill="x", ipady=15, padx=15)

        # Action buttons
        actions = tk.Frame(conv_card, bg=self.colors["card"])
        actions.pack(fill="x", padx=20, pady=(0, 15))

        tk.Button(actions, text="Copy Result",
                  font=("Segoe UI", 10, "bold"),
                  bg=self.colors["success"], fg="white",
                  activebackground="#059669", activeforeground="white",
                  bd=0, padx=15, pady=8, cursor="hand2",
                  command=self._copy_result).pack(side="left", padx=(0, 8))

        tk.Button(actions, text="Clear",
                  font=("Segoe UI", 10, "bold"),
                  bg=self.colors["danger"], fg="white",
                  activebackground="#dc2626", activeforeground="white",
                  bd=0, padx=15, pady=8, cursor="hand2",
                  command=self._clear).pack(side="left", padx=(0, 8))

        self.formula_var = tk.StringVar(value="")
        tk.Label(actions, textvariable=self.formula_var,
                 font=("Segoe UI", 9, "italic"),
                 bg=self.colors["card"], fg=self.colors["muted"]).pack(side="right")

        # History card
        hist_card = tk.Frame(right, bg=self.colors["card"],
                             highlightbackground=self.colors["border"],
                             highlightthickness=1)
        hist_card.pack(fill="both", expand=True)

        hist_header = tk.Frame(hist_card, bg=self.colors["card"])
        hist_header.pack(fill="x", padx=20, pady=(15, 5))

        tk.Label(hist_header, text="CONVERSION HISTORY",
                 font=("Segoe UI", 11, "bold"),
                 bg=self.colors["card"], fg=self.colors["muted"]).pack(side="left")

        tk.Button(hist_header, text="Clear History",
                  font=("Segoe UI", 9),
                  bg="#f1f5f9", fg=self.colors["muted"],
                  activebackground="#e2e8f0",
                  bd=0, padx=10, pady=4, cursor="hand2",
                  command=self._clear_history).pack(side="right")

        # History listbox
        list_frame = tk.Frame(hist_card, bg=self.colors["card"])
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.history_list = tk.Listbox(list_frame,
                                       font=("Segoe UI", 10),
                                       bg=self.colors["input_bg"],
                                       fg=self.colors["text"],
                                       bd=0, highlightthickness=0,
                                       selectbackground=self.colors["primary"],
                                       selectforeground="white",
                                       activestyle="none")
        self.history_list.pack(fill="both", expand=True, ipady=8)

        hist_sb = ttk.Scrollbar(list_frame, orient="vertical", command=self.history_list.yview)
        self.history_list.config(yscrollcommand=hist_sb.set)
        hist_sb.pack(side="right", fill="y")

        # Status bar
        self.status = tk.Label(self.root, text="Ready | Press Enter to copy | Esc to clear",
                               bg=self.colors["primary"], fg="white",
                               font=("Segoe UI", 9), anchor="w")
        self.status.pack(side="bottom", fill="x")

    def _bind_events(self):
        self.root.bind("<Return>", lambda e: self._copy_result())
        self.root.bind("<Escape>", lambda e: self._clear())
        self.root.bind("<Control-s>", lambda e: self._swap_units())

    def _select_category(self, name, init=False):
        self.current_category = name
        for n, b in self.cat_buttons.items():
            if n == name:
                b.config(bg=self.colors["sidebar_active"])
            else:
                b.config(bg=self.colors["sidebar"])
        self._update_units()
        if not init:
            self._do_convert()

    def _update_units(self):
        try:
            units = list(self.categories[self.current_category]["units"].keys())
            self.from_unit_cb["values"] = units
            self.to_unit_cb["values"] = units
            if units:
                self.from_unit_cb.current(0)
                self.to_unit_cb.current(min(1, len(units) - 1))
        except Exception as e:
            print(f"Error updating units: {e}")

    def _convert_value(self, value, from_unit, to_unit):
        try:
            cat = self.categories[self.current_category]
            if cat.get("special"):
                return self._convert_temperature(value, from_unit, to_unit)
            from_factor = cat["units"][from_unit]
            to_factor = cat["units"][to_unit]
            base_value = value * from_factor
            return base_value / to_factor
        except Exception as e:
            raise ValueError(f"Conversion error: {e}")

    def _convert_temperature(self, value, from_unit, to_unit):
        try:
            units = self.categories["Temperature"]["units"]
            from_code = units[from_unit]
            to_code = units[to_unit]

            # Convert to Celsius first
            if from_code == "C":
                c = value
            elif from_code == "F":
                c = (value - 32) * 5 / 9
            else:  # K
                c = value - 273.15

            # Convert from Celsius to target
            if to_code == "C":
                return c
            elif to_code == "F":
                return c * 9 / 5 + 32
            else:  # K
                return c + 273.15
        except Exception as e:
            raise ValueError(f"Temperature conversion error: {e}")

    def _format_number(self, n):
        try:
            if n == 0:
                return "0"
            abs_n = abs(n)
            if abs_n >= 1e15 or abs_n < 1e-6:
                return f"{n:.6e}"
            if abs_n >= 1000:
                return f"{n:,.4f}".rstrip("0").rstrip(".")
            if abs_n >= 1:
                return f"{n:.6f}".rstrip("0").rstrip(".")
            return f"{n:.10f}".rstrip("0").rstrip(".")
        except Exception:
            return str(n)

    def _do_convert(self):
        try:
            text = self.input_var.get().strip()
            if not text:
                self.result_var.set("-")
                self.formula_var.set("")
                return

            try:
                value = float(text.replace(",", ""))
            except ValueError:
                self.result_var.set("Invalid number")
                self.formula_var.set("")
                return

            from_u = self.from_unit_var.get()
            to_u = self.to_unit_var.get()
            
            if not from_u or not to_u:
                self.result_var.set("-")
                self.formula_var.set("")
                return

            result = self._convert_value(value, from_u, to_u)
            formatted = self._format_number(result)
            self.result_var.set(f"{formatted}  {to_u}")
            
            formula_val = self._convert_value(1, from_u, to_u)
            self.formula_var.set(f"1 {from_u} = {self._format_number(formula_val)} {to_u}")
            
            self._add_history(value, from_u, result, to_u)
            
        except Exception as e:
            self.result_var.set(f"Error: {str(e)}")
            self.formula_var.set("")

    def _add_history(self, val, from_u, res, to_u):
        try:
            entry = f"{self._format_number(val)} {from_u} -> {self._format_number(res)} {to_u}"
            
            # Avoid duplicate consecutive entries
            if entry == self.last_history_entry:
                return
            
            self.history.insert(0, entry)
            self.history = self.history[:self.max_history]
            self.last_history_entry = entry
            self._refresh_history()
        except Exception as e:
            print(f"Error adding history: {e}")

    def _refresh_history(self):
        try:
            self.history_list.delete(0, tk.END)
            for item in self.history:
                self.history_list.insert(tk.END, "  " + item)
        except Exception as e:
            print(f"Error refreshing history: {e}")

    def _swap_units(self):
        try:
            f = self.from_unit_var.get()
            t = self.to_unit_var.get()
            if f and t:
                self.from_unit_var.set(t)
                self.to_unit_var.set(f)
                self._do_convert()
                self.status.config(text="Units swapped")
        except Exception as e:
            print(f"Error swapping units: {e}")

    def _copy_result(self):
        try:
            result = self.result_var.get()
            if not result or result in ("-",) or result.startswith("Error") or result.startswith("Invalid"):
                return
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            self.status.config(text=f"Copied: {result}")
        except Exception as e:
            print(f"Error copying: {e}")

    def _clear(self):
        try:
            self.input_var.set("")
            self.result_var.set("-")
            self.formula_var.set("")
            self.input_entry.focus_set()
            self.status.config(text="Cleared")
        except Exception as e:
            print(f"Error clearing: {e}")

    def _clear_history(self):
        try:
            if not self.history:
                return
            if messagebox.askyesno("Clear History", "Clear all conversion history?"):
                self.history.clear()
                self.last_history_entry = ""
                self._refresh_history()
                self.status.config(text="History cleared")
        except Exception as e:
            print(f"Error clearing history: {e}")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = UnitConverter(root)
        root.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()