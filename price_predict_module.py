"""
PREDICT SENSE
Professional AI-style Price Prediction Dashboard
Single-file Python application.

Run:
    python predict_sense.py

Optional ML package:
    pip install scikit-learn

Note:
This is an educational estimator. It does not use live market listings.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
from datetime import datetime

APP_NAME = "PREDICT SENSE"
VERSION = "4.0"

# ----------------------------- THEME ---------------------------------

BG = "#08111F"
SURFACE = "#0D1929"
SURFACE_2 = "#122238"
INPUT = "#0A1626"
TEXT = "#F3F7FC"
MUTED = "#91A4BD"
ACCENT = "#4D8DFF"
ACCENT_2 = "#7BAAFF"
SUCCESS = "#35D49A"
WARNING = "#F5B84B"
BORDER = "#213552"


# -------------------------- DETECTION --------------------------------

CATEGORY_KEYWORDS = {
    "Cars": [
        "car", "vehicle", "automobile", "toyota", "honda", "suzuki", "hyundai",
        "kia", "nissan", "ford", "bmw", "mercedes", "audi", "corolla", "civic",
        "city", "alto", "swift", "cultus", "yaris", "vitz", "prado", "fortuner",
        "sportage", "tucson", "mehran", "wagon r", "passo", "aqua", "mira",
        "land cruiser", "mg", "changan", "proton"
    ],
    "Real Estate": [
        "house", "home", "property", "plot", "land", "apartment", "flat", "villa",
        "bungalow", "office", "shop", "commercial", "residential", "real estate",
        "farmhouse", "portion", "penthouse", "building", "warehouse"
    ],
    "Electronics": [
        "iphone", "samsung", "pixel", "oneplus", "xiaomi", "oppo", "vivo", "phone",
        "mobile", "tablet", "ipad", "laptop", "macbook", "dell", "hp", "lenovo",
        "asus", "acer", "computer", "desktop", "monitor", "printer", "camera",
        "canon", "nikon", "sony", "headphone", "headphones", "airpods", "earbuds",
        "speaker", "tv", "television", "playstation", "ps5", "xbox", "gaming",
        "keyboard", "mouse", "router", "smartwatch", "watch", "fridge",
        "refrigerator", "washing machine", "microwave", "ac", "air conditioner"
    ],
    "Motorcycles": [
        "bike", "bikes", "motorcycle", "motorbike", "honda cd 70", "cd 70",
        "honda 125", "cg 125", "yamaha", "ybr", "suzuki gs 150", "gs 150",
        "suzuki 150", "benelli", "kawasaki", "road prince", "unique bike"
    ],
    "Furniture": [
        "sofa", "couch", "chair", "table", "dining table", "bed", "double bed",
        "single bed", "wardrobe", "cabinet", "desk", "bookshelf", "shelf",
        "furniture", "cupboard", "dresser", "recliner", "office chair"
    ],
    "Fashion": [
        "shirt", "t shirt", "t-shirt", "jeans", "trousers", "pants", "shoes",
        "sneakers", "jacket", "coat", "dress", "suit", "kurta", "shalwar",
        "shalwar kameez", "clothes", "clothing", "bag", "handbag", "backpack",
        "wallet", "watch"
    ],
    "Home Appliances": [
        "refrigerator", "fridge", "washing machine", "dryer", "microwave",
        "oven", "air conditioner", "ac", "fan", "air fryer", "blender",
        "juicer", "vacuum", "iron", "water dispenser", "heater"
    ],
    "Gaming": [
        "playstation", "ps4", "ps5", "xbox", "nintendo", "switch", "gaming pc",
        "gaming laptop", "gaming console", "controller", "gaming chair"
    ]
}


BRAND_BASES = {
    "iphone": 185000,
    "samsung": 125000,
    "macbook": 285000,
    "dell": 175000,
    "hp": 155000,
    "lenovo": 150000,
    "laptop": 145000,
    "computer": 125000,
    "phone": 75000,
    "mobile": 75000,
    "tablet": 85000,
    "watch": 45000,
    "camera": 130000,
    "headphone": 25000,
    "headphones": 25000,
    "airpods": 55000,
    "tv": 110000,
    "television": 110000,
    "playstation": 150000,
    "ps5": 165000,
    "xbox": 135000,
    "monitor": 55000,
    "printer": 45000,
    "fridge": 115000,
    "refrigerator": 115000,
    "washing machine": 100000,
    "ac": 145000,
    "air conditioner": 145000
}

CAR_BASES = {
    "toyota": 5200000,
    "honda": 4800000,
    "suzuki": 2500000,
    "hyundai": 4300000,
    "kia": 4400000,
    "nissan": 3800000,
    "ford": 5500000,
    "bmw": 10500000,
    "mercedes": 12500000,
    "audi": 10000000
}


def detect_category(query):
    text = query.lower().strip()
    scores = {category: 0 for category in CATEGORY_KEYWORDS}

    for category, words in CATEGORY_KEYWORDS.items():
        for word in words:
            if re.search(r"(?<!\w)" + re.escape(word) + r"(?!\w)", text):
                scores[category] += 2 if " " in word else 1

    if re.search(r"\b(19|20)\d{2}\b", text):
        scores["Cars"] += 2
        scores["Motorcycles"] += 1

    if any(x in text for x in ["sq ft", "sqft", "square feet", "sq yd", "square yards",
                               "bedroom", "bedrooms", "bathroom", "baths"]):
        scores["Real Estate"] += 4

    if any(x in text for x in ["km", "mileage", "cc", "engine"]):
        scores["Cars"] += 3
        scores["Motorcycles"] += 2

    if any(x in text for x in ["gb", "ram", "ssd", "storage", "inch", "tb"]):
        scores["Electronics"] += 2

    best = max(scores, key=scores.get)
    best_score = scores[best]

    # Unknown items are deliberately not forced into a category.
    if best_score == 0:
        return None, 0.0

    confidence = min(0.96, 0.68 + best_score * 0.045)
    return best, confidence


def extract_number(text, patterns, default=0):
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            try:
                return float(match.group(1).replace(",", ""))
            except ValueError:
                pass
    return default


def money(value):
    return f"PKR {value:,.0f}"


# ------------------------- PRICE ENGINE ------------------------------

def predict_product(query):
    text = query.lower()

    base = None
    matched_brand = None

    for name, value in BRAND_BASES.items():
        if name in text:
            base = value
            matched_brand = name
            break

    if base is None:
        base = 65000

    # Detect product age / condition clues
    if any(x in text for x in ["new", "sealed", "brand new"]):
        condition_factor = 1.10
        condition = "New"
    elif any(x in text for x in ["used", "second hand", "2nd hand"]):
        condition_factor = 0.78
        condition = "Used"
    else:
        condition_factor = 1.00
        condition = "Standard"

    # Specs can change an estimate
    ram = extract_number(text, [r"(\d+)\s*gb\s*ram", r"ram\s*(\d+)\s*gb"], 0)
    storage = extract_number(text, [r"(\d+)\s*(?:gb|tb)\s*(?:ssd|storage)", r"(\d+)\s*gb\s*storage"], 0)

    if ram:
        base *= 1 + min(ram, 64) * 0.012
    if storage:
        base *= 1 + min(storage, 2048) * 0.00006

    price = base * condition_factor
    return price, price * 0.88, price * 1.12, condition, matched_brand


def predict_car(query):
    text = query.lower()

    base = 3500000
    matched_brand = "Other"

    for brand, value in CAR_BASES.items():
        if brand in text:
            base = value
            matched_brand = brand.title()
            break

    year = extract_number(text, [r"\b((?:19|20)\d{2})\b"], 2020)
    mileage = extract_number(
        text,
        [r"([\d,]+)\s*(?:km|kms|kilometers)", r"mileage\s*[:\-]?\s*([\d,]+)"],
        50000
    )

    age = max(0, 2026 - year)
    age_factor = max(0.52, 1 - age * 0.06)
    mileage_factor = max(0.70, 1 - mileage / 550000)

    if any(x in text for x in ["excellent", "mint", "like new"]):
        condition_factor = 1.10
        condition = "Excellent"
    elif any(x in text for x in ["fair", "average"]):
        condition_factor = 0.88
        condition = "Fair"
    elif any(x in text for x in ["damaged", "needs work"]):
        condition_factor = 0.70
        condition = "Needs Work"
    else:
        condition_factor = 1.00
        condition = "Good"

    engine = extract_number(text, [r"(\d+(?:\.\d+)?)\s*(?:l|liter|litre)", r"(\d+)\s*cc"], 1.5)
    engine_factor = 1 + min(engine, 5) * 0.055

    price = base * age_factor * mileage_factor * condition_factor * engine_factor

    return price, price * 0.90, price * 1.10, condition, matched_brand


def predict_real_estate(query):
    text = query.lower()

    area = extract_number(
        text,
        [
            r"([\d,]+)\s*(?:sq\.?\s*ft|sqft|square\s*feet)",
            r"([\d,]+)\s*(?:sq\.?\s*yd|sqyd|square\s*yards)"
        ],
        1200
    )

    # If square yards are used, convert approximately to sq ft.
    if re.search(r"(sq\.?\s*yd|sqyd|square\s*yards)", text, re.I):
        area *= 9

    beds = extract_number(text, [r"(\d+)\s*(?:bed|beds|bedroom|bedrooms)"], 3)
    baths = extract_number(text, [r"(\d+)\s*(?:bath|baths|bathroom|bathrooms)"], 2)

    if any(x in text for x in ["prime", "dha", "clifton", "defence", "defense", "gulberg"]):
        location_factor = 1.42
        location = "Prime"
    elif any(x in text for x in ["good", "gated", "central", "main road"]):
        location_factor = 1.18
        location = "Good"
    elif any(x in text for x in ["developing", "outskirts"]):
        location_factor = 0.82
        location = "Developing"
    else:
        location_factor = 1.00
        location = "Average"

    base_per_sqft = 13500
    price = area * base_per_sqft * location_factor
    price *= 1 + beds * 0.08 + baths * 0.04

    return price, price * 0.88, price * 1.12, location, f"{int(area):,} sq ft"


# ---------------------- EXTRA PRICE ENGINES ---------------------------

def predict_generic(query, category, base):
    text = query.lower()
    condition = "Standard"
    factor = 1.0

    if any(x in text for x in ["new", "sealed", "brand new", "unused"]):
        condition, factor = "New", 1.10
    elif any(x in text for x in ["used", "second hand", "2nd hand", "pre owned"]):
        condition, factor = "Used", 0.78
    elif any(x in text for x in ["excellent", "mint", "like new"]):
        condition, factor = "Excellent", 1.06
    elif any(x in text for x in ["damaged", "broken", "needs work"]):
        condition, factor = "Needs Work", 0.62

    # Simple specification adjustments for common categories.
    size = extract_number(text, [r"(\d+(?:\.\d+)?)\s*(?:inch|inches)"], 0)
    if size and category in ["Electronics", "Home Appliances"]:
        base *= 1 + min(size, 100) * 0.004

    price = base * factor
    return price, price * 0.88, price * 1.12, condition, category


def predict_motorcycle(query):
    text = query.lower()
    bases = {
        "honda": 260000, "yamaha": 430000, "suzuki": 360000,
        "benelli": 650000, "kawasaki": 900000, "road prince": 190000,
        "unique": 180000
    }
    base = 250000
    brand = "Other"
    for name, value in bases.items():
        if name in text:
            base, brand = value, name.title()
            break

    year = extract_number(text, [r"\b((?:19|20)\d{2})\b"], 2023)
    mileage = extract_number(text, [r"([\d,]+)\s*(?:km|kms|kilometers)",
                                    r"mileage\s*[:\-]?\s*([\d,]+)"], 25000)
    age_factor = max(0.60, 1 - max(0, 2026 - year) * 0.055)
    mileage_factor = max(0.78, 1 - mileage / 500000)

    price = base * age_factor * mileage_factor
    return price, price * 0.90, price * 1.10, "Good", brand


def predict(query):
    category, detection_confidence = detect_category(query)

    if category is None:
        return {
            "available": False,
            "message": "This item is not available in Predict Sense.",
            "category": "Not supported",
            "price": 0,
            "low": 0,
            "high": 0,
            "confidence": 0,
            "descriptor": "",
            "detail": ""
        }

    if category == "Cars":
        result = predict_car(query)
    elif category == "Real Estate":
        result = predict_real_estate(query)
    elif category == "Motorcycles":
        result = predict_motorcycle(query)
    elif category == "Furniture":
        result = predict_generic(query, category, 45000)
    elif category == "Fashion":
        result = predict_generic(query, category, 12000)
    elif category == "Home Appliances":
        result = predict_generic(query, category, 65000)
    elif category == "Gaming":
        result = predict_generic(query, category, 110000)
    else:
        result = predict_product(query)

    if not isinstance(result, (tuple, list)) or len(result) != 5:
        raise RuntimeError("Internal prediction engine returned an invalid result.")

    price, low, high, descriptor, detail = result
    confidence = min(96, max(64, round(detection_confidence * 100)))

    return {
        "available": True,
        "category": category,
        "price": price,
        "low": low,
        "high": high,
        "confidence": confidence,
        "descriptor": descriptor,
        "detail": detail
    }



# ------------------------ MARKET INSIGHTS ------------------------------

def get_market_insights(query, result):
    """Create simple descriptive insight labels from the parsed item.
    These are heuristic estimates, not live market data.
    """
    text = query.lower()

    if not result.get("available"):
        return []

    category = result["category"]
    price = result["price"]

    if category in ("Cars", "Motorcycles"):
        if any(x in text for x in ["toyota", "honda", "suzuki", "yamaha", "kawasaki"]):
            demand = "High"
        else:
            demand = "Medium"
        liquidity = "Good"
        condition = result["descriptor"]
        market = "Active"
    elif category in ("Electronics", "Gaming", "Home Appliances"):
        demand = "High" if any(x in text for x in
                                ["iphone", "samsung", "laptop", "ps5", "playstation",
                                 "xbox", "ac", "air conditioner"]) else "Medium"
        liquidity = "Good"
        condition = result["descriptor"]
        market = "Active"
    elif category == "Real Estate":
        demand = "High" if any(x in text for x in
                                ["dha", "clifton", "defence", "defense", "main road",
                                 "prime", "central"]) else "Medium"
        liquidity = "Moderate"
        condition = result["descriptor"]
        market = "Location Sensitive"
    else:
        demand = "Medium"
        liquidity = "Moderate"
        condition = result["descriptor"]
        market = "Category Based"

    price_position = "Premium" if price >= 5000000 else ("Mid-range" if price >= 50000 else "Budget")

    return [
        ("Demand", demand),
        ("Market Activity", market),
        ("Liquidity", liquidity),
        ("Condition", condition),
        ("Price Segment", price_position),
    ]

# ---------------------------- UI -------------------------------------

class PredictSenseApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Predict Sense | AI Price Intelligence")
        self.geometry("1180x760")
        self.minsize(1000, 680)
        self.configure(bg=BG)

        self.query = tk.StringVar()
        self.result_price = tk.StringVar(value="-")
        self.result_range = tk.StringVar(value="Your estimated range will appear here.")
        self.result_category = tk.StringVar(value="Waiting for input")
        self.confidence = tk.StringVar(value="-")
        self.status = tk.StringVar(value="Ready | Enter an item to estimate its price")

        # Initialize these BEFORE build_main(). build_main() creates the
        # Market Profile rows from this list.
        self.insight_vars = [tk.StringVar(value="-") for _ in range(5)]

        self.setup_styles()
        self.build_header()
        self.build_main()
        self.build_footer()

        self.bind("<Return>", lambda event: self.run_prediction())
        self.bind("<Escape>", lambda event: self.clear())

        self.after(250, self.query_entry.focus_set)

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "TCombobox",
            fieldbackground=INPUT,
            background=INPUT,
            foreground=TEXT
        )

    def build_header(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=42, pady=(28, 16))

        tk.Frame(self, bg=ACCENT, height=3).pack(fill="x", padx=42, pady=(0, 14))

        # Designed logo mark
        logo = tk.Canvas(
            header,
            width=54,
            height=54,
            bg=BG,
            highlightthickness=0
        )
        logo.pack(side="left", padx=(0, 14))

        logo.create_oval(5, 5, 49, 49, fill=ACCENT, outline="")
        logo.create_arc(
            13, 13, 41, 41,
            start=35, extent=280,
            style="arc",
            outline="white",
            width=4
        )
        logo.create_line(28, 27, 39, 17, fill="white", width=4)
        logo.create_oval(24, 23, 32, 31, fill="white", outline="")

        title = tk.Frame(header, bg=BG)
        title.pack(side="left")

        tk.Label(
            title,
            text=APP_NAME,
            font=("Segoe UI", 25, "bold"),
            fg=TEXT,
            bg=BG
        ).pack(anchor="w")

        tk.Label(
            title,
            text="AI-powered price estimation across multiple product categories",
            font=("Segoe UI", 10),
            fg=MUTED,
            bg=BG
        ).pack(anchor="w")

        version = tk.Label(
            header,
            text=f"VERSION {VERSION}",
            font=("Segoe UI", 8, "bold"),
            fg=ACCENT_2,
            bg=SURFACE_2,
            padx=12,
            pady=7
        )
        version.pack(side="right", pady=7)

    def build_main(self):
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=42)

        # Search card
        search_card = tk.Frame(
            main,
            bg=SURFACE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        search_card.pack(fill="x")

        tk.Label(
            search_card,
            text="What do you want to value?",
            font=("Segoe UI", 16, "bold"),
            fg=TEXT,
            bg=SURFACE
        ).pack(anchor="w", padx=28, pady=(24, 3))

        tk.Label(
            search_card,
            text="Just describe it naturally. Predict Sense detects the category automatically.",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=SURFACE
        ).pack(anchor="w", padx=28)

        search_row = tk.Frame(search_card, bg=SURFACE)
        search_row.pack(fill="x", padx=28, pady=18)

        search_box = tk.Frame(
            search_row,
            bg=INPUT,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            highlightthickness=1
        )
        search_box.pack(side="left", fill="x", expand=True)

        tk.Label(
            search_box,
            text="Search",
            font=("Segoe UI", 9, "bold"),
            fg=ACCENT_2,
            bg=INPUT
        ).pack(side="left", padx=(13, 8))

        self.query_entry = tk.Entry(
            search_box,
            textvariable=self.query,
            font=("Segoe UI", 12),
            fg=TEXT,
            bg=INPUT,
            insertbackground=TEXT,
            relief="flat",
            bd=0
        )
        self.query_entry.pack(side="left", fill="x", expand=True, ipady=12)

        self.predict_button = tk.Button(
            search_row,
            text="Predict Price",
            command=self.run_prediction,
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg=ACCENT,
            activeforeground="white",
            activebackground=ACCENT_2,
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=13
        )
        self.predict_button.pack(side="left", padx=(12, 0))

        examples = tk.Frame(search_card, bg=SURFACE)
        examples.pack(fill="x", padx=28, pady=(0, 23))

        tk.Label(
            examples,
            text="Examples:",
            font=("Segoe UI", 9, "bold"),
            fg=MUTED,
            bg=SURFACE
        ).pack(side="left", padx=(0, 8))

        example_text = (
            "Toyota Corolla 2022 35,000 km   |   iPhone 15 256GB used   |   "
            "1200 sq ft house 3 bedrooms"
        )
        tk.Label(
            examples,
            text=example_text,
            font=("Segoe UI", 9),
            fg=ACCENT_2,
            bg=SURFACE
        ).pack(side="left")

        # Results
        results = tk.Frame(main, bg=BG)
        results.pack(fill="both", expand=True, pady=(18, 0))

        left = tk.Frame(
            results,
            bg=SURFACE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        left.pack(side="left", fill="both", expand=True, padx=(0, 9))

        right = tk.Frame(
            results,
            bg=SURFACE,
            width=335,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        right.pack(side="right", fill="y", padx=(9, 0))
        right.pack_propagate(False)

        tk.Label(
            left,
            text="PRICE ESTIMATE",
            font=("Segoe UI", 9, "bold"),
            fg=ACCENT,
            bg=SURFACE
        ).pack(anchor="w", padx=28, pady=(27, 7))

        tk.Label(
            left,
            textvariable=self.result_category,
            font=("Segoe UI", 13, "bold"),
            fg=TEXT,
            bg=SURFACE
        ).pack(anchor="w", padx=28)

        tk.Label(
            left,
            textvariable=self.result_price,
            font=("Segoe UI", 34, "bold"),
            fg=TEXT,
            bg=SURFACE
        ).pack(anchor="w", padx=28, pady=(17, 2))

        tk.Label(
            left,
            text="Estimated market value",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=SURFACE
        ).pack(anchor="w", padx=28)

        self.make_divider(left)

        tk.Label(
            left,
            text="ESTIMATED RANGE",
            font=("Segoe UI", 8, "bold"),
            fg=MUTED,
            bg=SURFACE
        ).pack(anchor="w", padx=28, pady=(20, 5))

        tk.Label(
            left,
            textvariable=self.result_range,
            font=("Segoe UI", 13, "bold"),
            fg=SUCCESS,
            bg=SURFACE
        ).pack(anchor="w", padx=28)

        tk.Label(
            left,
            text="Range represents an approximate valuation band based on the description.",
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=SURFACE
        ).pack(anchor="w", padx=28, pady=(6, 20))

        # Right intelligence panel
        tk.Label(
            right,
            text="ANALYSIS",
            font=("Segoe UI", 9, "bold"),
            fg=ACCENT,
            bg=SURFACE
        ).pack(anchor="w", padx=25, pady=(27, 18))

        self.info_row(right, "Detected category", self.result_category)
        self.info_row(right, "Input confidence", self.confidence)

        self.make_divider(right)

        tk.Label(
            right,
            text="MARKET PROFILE",
            font=("Segoe UI", 8, "bold"),
            fg=MUTED,
            bg=SURFACE
        ).pack(anchor="w", padx=25, pady=(18, 8))

        insight_labels = [
            "Demand", "Market Activity", "Liquidity",
            "Condition", "Price Segment"
        ]
        for index, label in enumerate(insight_labels):
            variable = self.insight_vars[index]
            self.info_row(right, label, variable)

        tk.Label(
            right,
            text="PROCESS",
            font=("Segoe UI", 8, "bold"),
            fg=MUTED,
            bg=SURFACE
        ).pack(anchor="w", padx=25, pady=(20, 10))

        steps = [
            ("01", "Understand", "Reads the words and specifications."),
            ("02", "Classify", "Detects product, car, or property."),
            ("03", "Estimate", "Calculates an approximate value range.")
        ]

        for num, heading, desc in steps:
            row = tk.Frame(right, bg=SURFACE)
            row.pack(fill="x", padx=25, pady=7)

            tk.Label(
                row,
                text=num,
                font=("Segoe UI", 8, "bold"),
                fg=ACCENT_2,
                bg=SURFACE_2,
                padx=7,
                pady=5
            ).pack(side="left", anchor="n")

            text_box = tk.Frame(row, bg=SURFACE)
            text_box.pack(side="left", padx=10)

            tk.Label(
                text_box,
                text=heading,
                font=("Segoe UI", 9, "bold"),
                fg=TEXT,
                bg=SURFACE
            ).pack(anchor="w")

            tk.Label(
                text_box,
                text=desc,
                font=("Segoe UI", 8),
                fg=MUTED,
                bg=SURFACE,
                wraplength=220,
                justify="left"
            ).pack(anchor="w")

    def info_row(self, parent, label, variable):
        row = tk.Frame(parent, bg=SURFACE)
        row.pack(fill="x", padx=25, pady=8)

        tk.Label(
            row,
            text=label,
            font=("Segoe UI", 8),
            fg=MUTED,
            bg=SURFACE
        ).pack(side="left")

        tk.Label(
            row,
            textvariable=variable,
            font=("Segoe UI", 9, "bold"),
            fg=TEXT,
            bg=SURFACE
        ).pack(side="right")

    def make_divider(self, parent):
        tk.Frame(parent, height=1, bg=BORDER).pack(fill="x", padx=28)

    def build_footer(self):
        footer = tk.Frame(self, bg=BG)
        footer.pack(fill="x", padx=42, pady=(15, 24))

        tk.Label(
            footer,
            textvariable=self.status,
            font=("Segoe UI", 8),
            fg=MUTED,
            bg=BG
        ).pack(side="left")

        tk.Button(
            footer,
            text="Clear",
            command=self.clear,
            font=("Segoe UI", 9),
            fg=TEXT,
            bg=SURFACE_2,
            activebackground=BORDER,
            activeforeground=TEXT,
            relief="flat",
            cursor="hand2",
            padx=17,
            pady=8
        ).pack(side="right")

        tk.Label(
            footer,
            text="Educational estimate | Not a live market quote",
            font=("Segoe UI", 8),
            fg=MUTED,
            bg=BG
        ).pack(side="right", padx=12)

    # -------------------------- ACTIONS -------------------------------

    def run_prediction(self):
        query = self.query.get().strip()

        if len(query) < 3:
            messagebox.showwarning(
                "More information needed",
                "Please enter a product, car, or property description."
            )
            self.query_entry.focus_set()
            return

        try:
            result = predict(query)

            if not result["available"]:
                self.result_category.set("Item not available")
                self.result_price.set("Not Available")
                self.result_range.set("This item is not available in Predict Sense.")
                self.confidence.set("-")
                for variable in self.insight_vars:
                    variable.set("-")
                self.status.set("No supported category detected")
                return

            self.result_category.set(result["category"])
            self.result_price.set(money(result["price"]))
            self.result_range.set(
                f'{money(result["low"])} - {money(result["high"])}'
            )
            self.confidence.set(f'{result["confidence"]}%')

            insights = get_market_insights(query, result)
            for index, variable in enumerate(self.insight_vars):
                variable.set(insights[index][1] if index < len(insights) else "-")

            self.status.set(
                f'Prediction generated | {datetime.now().strftime("%H:%M:%S")}'
            )

        except Exception as exc:
            messagebox.showerror(
                "Prediction Error",
                f"Something went wrong while processing the description.\n\n{exc}"
            )

    def clear(self):
        self.query.set("")
        self.result_price.set("-")
        self.result_range.set("Your estimated range will appear here.")
        self.result_category.set("Waiting for input")
        self.confidence.set("-")
        for variable in self.insight_vars:
            variable.set("-")
        self.status.set("Ready | Enter an item to estimate its price")
        self.query_entry.focus_set()


if __name__ == "__main__":
    app = PredictSenseApp()
    app.mainloop()
