import tkinter as tk
from tkinter import font as tkfont
import math

class ProfessionalCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Pro Calculator")
        self.root.geometry("380x700")
        self.root.resizable(False, False)
        self.root.configure(bg="#000000")

        # ── State Variables ──
        self.current_input = "0"
        self.previous_input = ""
        self.operator = None
        self.should_reset = False
        self.history = ""

        # ── Color Theme (iOS Style) ──
        self.colors = {
            "bg":           "#000000",
            "display_bg":   "#000000",
            "display_fg":   "#FFFFFF",
            "history_fg":   "#8E8E93",
            "num_bg":       "#333333",
            "num_fg":       "#FFFFFF",
            "num_hover":    "#555555",
            "op_bg":        "#FF9F0A",
            "op_fg":        "#FFFFFF",
            "op_hover":     "#FFB84D",
            "op_active":    "#FFFFFF",
            "func_bg":      "#A5A5A5",
            "func_fg":      "#000000",
            "func_hover":   "#C8C8C8",
            "equal_bg":     "#FF9F0A",
            "zero_bg":      "#333333",
        }

        self._build_ui()
        self._bind_keyboard()

    # ═══════════════════════════════════════
    #  UI CONSTRUCTION
    # ═══════════════════════════════════════
    def _build_ui(self):
        # ── Display Area ──
        display_frame = tk.Frame(self.root, bg=self.colors["bg"], height=220)
        display_frame.pack(fill="x", padx=15, pady=(30, 10))
        display_frame.pack_propagate(False)

        self.history_label = tk.Label(
            display_frame, text="", font=("SF Pro Display", 16),
            bg=self.colors["display_bg"], fg=self.colors["history_fg"],
            anchor="e"
        )
        self.history_label.pack(fill="x", padx=5, side="top", anchor="e")

        self.display = tk.Label(
            display_frame, text="0", font=("SF Pro Display", 55, "bold"),
            bg=self.colors["display_bg"], fg=self.colors["display_fg"],
            anchor="e"
        )
        self.display.pack(fill="x", padx=5, side="bottom", anchor="e")

        # ── Separator Line ──
        sep = tk.Frame(self.root, bg="#1C1C1E", height=1)
        sep.pack(fill="x", padx=15, pady=(0, 15))

        # ── Button Grid ──
        btn_frame = tk.Frame(self.root, bg=self.colors["bg"])
        btn_frame.pack(fill="both", expand=True, padx=12, pady=(0, 20))

        buttons = [
            [("AC", "func"), ("±", "func"), ("%", "func"), ("÷", "op")],
            [("7", "num"),  ("8", "num"),  ("9", "num"),  ("×", "op")],
            [("4", "num"),  ("5", "num"),  ("6", "num"),  ("−", "op")],
            [("1", "num"),  ("2", "num"),  ("3", "num"),  ("+", "op")],
            [("0", "num_zero"), (".", "num"), ("⌫", "func"), ("=", "equal")],
        ]

        for r, row in enumerate(buttons):
            btn_frame.rowconfigure(r, weight=1, uniform="row")
            for c, (text, btype) in enumerate(row):
                if text == "0":
                    btn_frame.columnconfigure(c, weight=2, uniform="col")
                else:
                    btn_frame.columnconfigure(c, weight=1, uniform="col")

                btn = self._create_button(btn_frame, text, btype, r, c)
                if text == "0":
                    btn.grid(row=r, column=c, columnspan=1, padx=4, pady=4, sticky="nsew")
                else:
                    btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

    def _create_button(self, parent, text, btype, row, col):
        if btype == "num":
            bg, fg, hover = self.colors["num_bg"], self.colors["num_fg"], self.colors["num_hover"]
            fnt = ("SF Pro Display", 24)
        elif btype == "num_zero":
            bg, fg, hover = self.colors["num_bg"], self.colors["num_fg"], self.colors["num_hover"]
            fnt = ("SF Pro Display", 24)
        elif btype == "op":
            bg, fg, hover = self.colors["op_bg"], self.colors["op_fg"], self.colors["op_hover"]
            fnt = ("SF Pro Display", 28, "bold")
        elif btype == "equal":
            bg, fg, hover = self.colors["equal_bg"], self.colors["op_fg"], self.colors["op_hover"]
            fnt = ("SF Pro Display", 28, "bold")
        else:
            bg, fg, hover = self.colors["func_bg"], self.colors["func_fg"], self.colors["func_hover"]
            fnt = ("SF Pro Display", 20, "bold")

        btn = tk.Button(
            parent, text=text, font=fnt,
            bg=bg, fg=fg, activebackground=hover, activeforeground=fg,
            bd=0, relief="flat", cursor="hand2",
            highlightthickness=0,
            command=lambda t=text: self._on_click(t)
        )

        # ── Hover Effects ──
        btn.bind("<Enter>", lambda e, b=btn, h=hover: b.config(bg=h))
        btn.bind("<Leave>", lambda e, b=btn, o=bg: b.config(bg=o))

        # ── Press Animation ──
        btn.bind("<ButtonPress-1>", lambda e, b=btn, h=hover: self._press_anim(b, h))
        btn.bind("<ButtonRelease-1>", lambda e, b=btn, o=bg: self._release_anim(b, o))

        return btn

    def _press_anim(self, btn, color):
        btn.config(bg="#FFFFFF", relief="sunken")

    def _release_anim(self, btn, color):
        btn.config(bg=color, relief="flat")

    # ═══════════════════════════════════════
    #  KEYBOARD BINDING
    # ═══════════════════════════════════════
    def _bind_keyboard(self):
        self.root.bind("<Key>", self._key_handler)

    def _key_handler(self, event):
        key = event.char
        keysym = event.keysym

        if key in "0123456789":
            self._on_click(key)
        elif key == ".":
            self._on_click(".")
        elif key == "+":
            self._on_click("+")
        elif key == "-":
            self._on_click("−")
        elif key == "*":
            self._on_click("×")
        elif key == "/":
            self._on_click("÷")
        elif key == "%":
            self._on_click("%")
        elif keysym == "Return" or key == "=":
            self._on_click("=")
        elif keysym == "BackSpace":
            self._on_click("⌫")
        elif keysym == "Escape":
            self._on_click("AC")

    # ═══════════════════════════════════════
    #  CALCULATOR LOGIC
    # ═══════════════════════════════════════
    def _on_click(self, text):
        if text == "AC":
            self._clear_all()
        elif text == "⌫":
            self._backspace()
        elif text == "±":
            self._toggle_sign()
        elif text == "%":
            self._percentage()
        elif text in ("+", "−", "×", "÷"):
            self._set_operator(text)
        elif text == "=":
            self._calculate()
        elif text == ".":
            self._add_decimal()
        else:
            self._add_digit(text)

    def _clear_all(self):
        self.current_input = "0"
        self.previous_input = ""
        self.operator = None
        self.should_reset = False
        self.history = ""
        self._update_display()

    def _backspace(self):
        if self.should_reset:
            return
        if len(self.current_input) > 1:
            self.current_input = self.current_input[:-1]
            if self.current_input == "-":
                self.current_input = "0"
        else:
            self.current_input = "0"
        self._update_display()

    def _toggle_sign(self):
        if self.current_input == "0":
            return
        if self.current_input.startswith("-"):
            self.current_input = self.current_input[1:]
        else:
            self.current_input = "-" + self.current_input
        self._update_display()

    def _percentage(self):
        try:
            val = float(self.current_input)
            val = val / 100
            self.current_input = self._format_number(val)
            self._update_display()
        except Exception:
            pass

    def _add_digit(self, digit):
        if self.should_reset:
            self.current_input = digit
            self.should_reset = False
        else:
            if self.current_input == "0" and digit != "0":
                self.current_input = digit
            elif self.current_input == "0" and digit == "0":
                pass
            else:
                if len(self.current_input.replace(".", "").replace("-", "")) < 15:
                    self.current_input += digit
        self._update_display()

    def _add_decimal(self):
        if self.should_reset:
            self.current_input = "0."
            self.should_reset = False
        elif "." not in self.current_input:
            self.current_input += "."
        self._update_display()

    def _set_operator(self, op):
        if self.operator and not self.should_reset:
            self._calculate()
        self.previous_input = self.current_input
        self.operator = op
        self.should_reset = True
        self.history = f"{self._format_display(self.previous_input)} {op}"
        self._update_display()

    def _calculate(self):
        if self.operator is None or self.previous_input == "":
            return

        try:
            a = float(self.previous_input)
            b = float(self.current_input)
            result = 0

            if self.operator == "+":
                result = a + b
            elif self.operator == "−":
                result = a - b
            elif self.operator == "×":
                result = a * b
            elif self.operator == "÷":
                if b == 0:
                    self._show_error("Cannot divide by zero")
                    return
                result = a / b

            self.history = f"{self._format_display(self.previous_input)} {self.operator} {self._format_display(self.current_input)} ="
            self.current_input = self._format_number(result)
            self.operator = None
            self.previous_input = ""
            self.should_reset = True
            self._update_display()

        except Exception:
            self._show_error("Error")

    def _show_error(self, msg):
        self.display.config(text=msg, fg="#FF453A")
        self.current_input = "0"
        self.previous_input = ""
        self.operator = None
        self.should_reset = True
        self.root.after(1500, lambda: self.display.config(fg=self.colors["display_fg"]))

    # ═══════════════════════════════════════
    #  DISPLAY HELPERS
    # ═══════════════════════════════════════
    def _format_number(self, value):
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))
        formatted = f"{value:.10g}"
        return formatted

    def _format_display(self, num_str):
        try:
            if "." in num_str:
                integer_part, decimal_part = num_str.split(".")
            else:
                integer_part = num_str
                decimal_part = ""

            negative = integer_part.startswith("-")
            if negative:
                integer_part = integer_part[1:]

            # Add commas
            groups = []
            while len(integer_part) > 3:
                groups.insert(0, integer_part[-3:])
                integer_part = integer_part[:-3]
            groups.insert(0, integer_part)
            formatted = ",".join(groups)

            if negative:
                formatted = "-" + formatted
            if decimal_part:
                formatted += "." + decimal_part

            return formatted
        except Exception:
            return num_str

    def _update_display(self):
        display_text = self._format_display(self.current_input)
        self.display.config(text=display_text)
        self.history_label.config(text=self.history)

        # Auto-resize font based on length
        length = len(display_text)
        if length <= 8:
            size = 55
        elif length <= 11:
            size = 44
        elif length <= 14:
            size = 36
        else:
            size = 28

        self.display.config(font=("SF Pro Display", size, "bold"))


# ═══════════════════════════════════════
#  RUN THE APP
# ═══════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()

    # Try to set icon (optional, won't crash if fails)
    try:
        root.iconbitmap(default="")
    except Exception:
        pass

    # Center the window on screen
    root.update_idletasks()
    w, h = 380, 700
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    app = ProfessionalCalculator(root)
    root.mainloop()