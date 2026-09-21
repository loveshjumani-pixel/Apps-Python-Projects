#!/usr/bin/env python3
"""
Advanced Gradient Generator App - BUG FIXED VERSION
All major bugs resolved, performance improved
"""

import sys
import json
import os
import random
import math
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QSlider,
                             QColorDialog, QComboBox, QSpinBox, QFileDialog,
                             QMessageBox, QScrollArea, QFrame, QGridLayout,
                             QInputDialog, QShortcut, QSplitter, QGroupBox,
                             QSizePolicy, QToolButton, QMenu, QAction)
from PyQt5.QtCore import (Qt, QTimer, QPointF, QRectF, QSize, pyqtSignal,
                          QMimeData)
from PyQt5.QtGui import (QPainter, QColor, QLinearGradient, QRadialGradient,
                         QConicalGradient, QBrush, QPen, QKeySequence, QDrag,
                         QPixmap, QIcon, QFont, QPalette, QClipboard,
                         QPainterPath)  # ✅ FIXED: Added QPainterPath import

try:
    from PIL import Image
    import numpy as np
    PIL_AVAILABLE = True
    NUMPY_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    NUMPY_AVAILABLE = False
    try:
        from PIL import Image
        PIL_AVAILABLE = True
    except ImportError:
        pass


# ============================================================
# GRADIENT PRESETS
# ============================================================
GRADIENT_PRESETS = {
    "Sunset": [(255, 94, 72), (255, 154, 94)],
    "Ocean": [(30, 144, 255), (0, 210, 255)],
    "Forest": [(20, 80, 40), (144, 238, 144)],
    "Purple Dream": [(102, 51, 153), (255, 102, 178)],
    "Fire": [(255, 0, 0), (255, 165, 0), (255, 255, 0)],
    "Midnight": [(15, 32, 64), (44, 83, 131), (98, 146, 208)],
    "Candy": [(255, 154, 158), (250, 208, 196)],
    "Aurora": [(0, 255, 127), (0, 191, 255), (138, 43, 226)],
    "Peach": [(255, 204, 153), (255, 153, 102)],
    "Mint": [(176, 224, 230), (152, 251, 152)],
    "Lavender": [(230, 230, 250), (147, 112, 219)],
    "Cherry": [(222, 49, 99), (138, 21, 56)],
    "Sky": [(135, 206, 235), (255, 255, 255)],
    "Golden": [(255, 215, 0), (218, 165, 32)],
    "Rose Gold": [(183, 110, 121), (240, 194, 179)],
    "Cyberpunk": [(255, 0, 128), (0, 255, 255)],
    "Neon": [(57, 255, 20), (255, 0, 234)],
    "Cosmic": [(13, 71, 161), (156, 39, 176), (233, 30, 99)],
    "Autumn": [(205, 92, 0), (255, 140, 0), (255, 215, 0)],
    "Arctic": [(224, 247, 250), (179, 229, 252), (100, 181, 246)],
    "Blood Moon": [(74, 0, 0), (139, 0, 0), (255, 69, 0)],
    "Emerald": [(0, 100, 0), (80, 200, 120)],
    "Twilight": [(58, 24, 82), (142, 44, 108), (227, 87, 75)],
    "Coral Reef": [(255, 127, 80), (255, 160, 122), (255, 218, 185)],
    "Deep Space": [(9, 9, 61), (23, 23, 100), (70, 40, 140)],
    "Tropical": [(255, 99, 71), (255, 215, 0), (50, 205, 50)],
    "Ice": [(225, 245, 254), (179, 229, 252), (3, 169, 244)],
    "Vintage": [(210, 180, 140), (160, 82, 45)],
    "Galaxy": [(11, 12, 46), (86, 34, 110), (180, 68, 132)],
    "Mojito": [(180, 230, 180), (100, 200, 100)],
}


# ============================================================
# COLOR STOP MARKER - FIXED VERSION
# ============================================================
class ColorStopMarker(QWidget):
    """Individual draggable color stop marker - BUG FIXED"""
    positionChanged = pyqtSignal(int, float)
    colorChanged = pyqtSignal(int, QColor)
    removed = pyqtSignal(int)
    markerSelected = pyqtSignal(int)  # ✅ FIXED: Renamed to avoid conflict

    def __init__(self, index, color, position, parent=None):
        super().__init__(parent)
        self.index = index
        self.color = color
        self.position = position
        self.is_selected = False  # ✅ FIXED: Renamed from 'selected'
        self.setFixedSize(16, 28)
        self.setCursor(Qt.PointingHandCursor)
        self.drag_start_x = 0
        self.drag_start_pos = 0.0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # ✅ FIXED: Correct QPainterPath usage
        path = QPainterPath()
        path.moveTo(8, 0)
        path.lineTo(0, 12)
        path.lineTo(16, 12)
        path.closeSubpath()

        border_color = QColor(0, 170, 255) if self.is_selected else QColor(100, 100, 100)
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(QBrush(self.color))
        painter.drawPath(path)

        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(2, 14, 12, 12)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_x = event.globalPos().x()
            self.drag_start_pos = self.position
            self.is_selected = True
            self.update()
            self.markerSelected.emit(self.index)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            parent_width = self.parent().width() - 16  # ✅ FIXED: Consistent width
            if parent_width > 0:
                delta_x = event.globalPos().x() - self.drag_start_x
                delta_pos = delta_x / parent_width
                new_pos = max(0.0, min(1.0, self.drag_start_pos + delta_pos))
                self.position = new_pos
                new_x = int(new_pos * parent_width)
                self.move(new_x, self.y())
                self.positionChanged.emit(self.index, new_pos)

    def mouseDoubleClickEvent(self, event):
        color = QColorDialog.getColor(self.color, self, "Select Color")
        if color.isValid():
            self.color = color
            self.update()
            self.colorChanged.emit(self.index, color)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        if self.index > 0 and self.index < len(self.parent().markers) - 1:
            remove_action = menu.addAction("Remove Stop")
            action = menu.exec_(event.globalPos())
            if action == remove_action:
                self.removed.emit(self.index)


# ============================================================
# GRADIENT BAR - FIXED VERSION
# ============================================================
class GradientBar(QWidget):
    """Interactive gradient bar - BUG FIXED"""
    gradientChanged = pyqtSignal()
    stopAdded = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(60)
        self.setMaximumHeight(60)
        # ✅ FIXED: Use QColor objects instead of tuples
        self.color_stops = [
            (0.0, QColor(255, 94, 72)),
            (1.0, QColor(255, 154, 94))
        ]
        self.markers = []
        self.selected_index = -1
        self.setMouseTracking(True)
        self.rebuild_markers()

    def set_color_stops(self, stops):
        self.color_stops = sorted(stops, key=lambda x: x[0])
        self.rebuild_markers()
        self.update()
        self.gradientChanged.emit()

    def get_color_stops(self):
        return [(m.position, m.color) for m in self.markers]

    def rebuild_markers(self):
        # ✅ FIXED: Proper cleanup of old markers
        for m in self.markers:
            m.setParent(None)
            m.deleteLater()
        self.markers = []
        
        for i, (pos, color) in enumerate(self.color_stops):
            marker = ColorStopMarker(i, color, pos, self)
            marker.positionChanged.connect(self._on_marker_moved)
            marker.colorChanged.connect(self._on_marker_color_changed)
            marker.removed.connect(self._on_marker_removed)
            marker.markerSelected.connect(self._on_marker_selected)
            self.markers.append(marker)
            marker.show()
        
        self._layout_markers()

    def _layout_markers(self):
        bar_width = self.width() - 16  # ✅ FIXED: Consistent width calculation
        if bar_width <= 0:
            return
        for i, marker in enumerate(self.markers):
            marker.index = i
            x = int(marker.position * bar_width)
            marker.move(x, 0)
            marker.raise_()

    def _on_marker_moved(self, index, position):
        # ✅ FIXED: Update internal color_stops list
        if 0 <= index < len(self.markers):
            self.color_stops[index] = (position, self.markers[index].color)
            self.color_stops.sort(key=lambda x: x[0])
        self.gradientChanged.emit()

    def _on_marker_color_changed(self, index, color):
        if 0 <= index < len(self.markers):
            self.color_stops[index] = (self.markers[index].position, color)
        self.gradientChanged.emit()

    def _on_marker_removed(self, index):
        # ✅ FIXED: Proper index management after removal
        if len(self.markers) > 2 and 0 < index < len(self.markers) - 1:
            self.markers.pop(index)
            # Rebuild with updated indices
            self.color_stops = [(m.position, m.color) for m in self.markers]
            self.rebuild_markers()
            self.gradientChanged.emit()

    def _on_marker_selected(self, index):
        self.selected_index = index
        for i, m in enumerate(self.markers):
            m.is_selected = (i == index)
            m.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, self.width(), 0)
        for pos, color in [(m.position, m.color) for m in self.markers]:
            gradient.setColorAt(pos, color)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), 30, 8, 8)

        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(0, 0, self.width(), 30, 8, 8)

        painter.end()

    def mouseDoubleClickEvent(self, event):
        if event.y() <= 30:
            bar_width = self.width() - 16
            if bar_width > 0:
                position = max(0.0, min(1.0, event.x() / bar_width))
                color = QColorDialog.getColor(QColor(255, 255, 255), self, "Add Color Stop")
                if color.isValid():
                    self.color_stops.append((position, color))
                    self.color_stops.sort(key=lambda x: x[0])
                    self.rebuild_markers()
                    self.gradientChanged.emit()
                    self.stopAdded.emit()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._layout_markers()


# ============================================================
# GRADIENT PREVIEW - FIXED VERSION
# ============================================================
class GradientPreview(QWidget):
    """Main gradient preview widget - BUG FIXED"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gradient_type = "linear"
        self.angle = 90
        self.color_stops = [(0.0, QColor(255, 94, 72)), (1.0, QColor(255, 154, 94))]
        self.animation_offset = 0
        self.animate = False

    def set_gradient(self, gradient_type, angle, color_stops):
        self.gradient_type = gradient_type
        self.angle = angle
        self.color_stops = color_stops
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        self._draw_checkerboard(painter, rect)

        if self.gradient_type == "linear":
            gradient = self._create_linear_gradient(rect)
        elif self.gradient_type == "radial":
            gradient = self._create_radial_gradient(rect)
        elif self.gradient_type == "conic":
            gradient = self._create_conic_gradient(rect)
        else:
            gradient = self._create_linear_gradient(rect)

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 12, 12)

        painter.setPen(QPen(QColor(80, 80, 80), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect, 12, 12)

        painter.end()

    def _draw_checkerboard(self, painter, rect):
        size = 16
        painter.setPen(Qt.NoPen)
        for y in range(0, rect.height(), size):
            for x in range(0, rect.width(), size):
                if (x // size + y // size) % 2 == 0:
                    painter.setBrush(QBrush(QColor(220, 220, 220)))
                else:
                    painter.setBrush(QBrush(QColor(255, 255, 255)))
                painter.drawRect(x, y, size, size)

    def _create_linear_gradient(self, rect):
        # ✅ FIXED: Correct angle calculation for CSS compatibility
        angle_rad = math.radians(self.angle + self.animation_offset - 90)
        cx, cy = rect.center().x(), rect.center().y()
        length = max(rect.width(), rect.height())
        dx = math.cos(angle_rad) * length / 2
        dy = math.sin(angle_rad) * length / 2

        gradient = QLinearGradient(cx - dx, cy - dy, cx + dx, cy + dy)
        for pos, color in self.color_stops:
            gradient.setColorAt(pos, color)
        return gradient

    def _create_radial_gradient(self, rect):
        cx, cy = rect.center().x(), rect.center().y()
        radius = max(rect.width(), rect.height()) / 2
        gradient = QRadialGradient(QPointF(cx, cy), radius)
        for pos, color in self.color_stops:
            gradient.setColorAt(pos, color)
        return gradient

    def _create_conic_gradient(self, rect):
        cx, cy = rect.center().x(), rect.center().y()
        gradient = QConicalGradient(QPointF(cx, cy), self.angle + self.animation_offset)
        for pos, color in self.color_stops:
            gradient.setColorAt(pos, color)
        return gradient


# ============================================================
# PRESET BUTTON
# ============================================================
class PresetButton(QPushButton):
    def __init__(self, name, colors, parent=None):
        super().__init__(parent)
        self.name = name
        self.colors = colors
        self.setMinimumSize(100, 60)
        self.setMaximumSize(140, 70)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(name)
        self.setStyleSheet("""
            QPushButton {
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 2px;
            }
            QPushButton:hover {
                border: 2px solid #00aaff;
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(2, 2, -2, -2)

        gradient = QLinearGradient(0, 0, rect.width(), 0)
        for i, color in enumerate(self.colors):
            pos = i / (len(self.colors) - 1) if len(self.colors) > 1 else 0
            gradient.setColorAt(pos, QColor(*color))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 6, 6)

        painter.setPen(QPen(QColor(255, 255, 255)))
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignBottom | Qt.AlignHCenter, self.name)

        painter.end()


# ============================================================
# MAIN WINDOW - FIXED VERSION
# ============================================================
class GradientGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎨 Advanced Gradient Generator Pro")
        self.setMinimumSize(1200, 750)
        self.resize(1400, 850)

        self.current_file = None
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_step)
        self.animation_angle = 0
        self.ratio_locked = True  # ✅ FIXED: Track ratio lock state

        self._setup_ui()
        self._setup_shortcuts()
        self._apply_dark_theme()
        self._update_preview()

    def _apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e2e; }
            QWidget { background-color: #1e1e2e; color: #e0e0e0; font-family: 'Segoe UI', Arial; }
            QGroupBox {
                background-color: #2a2a3e;
                border: 1px solid #404060;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 16px;
                font-weight: bold;
                color: #00aaff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }
            QPushButton {
                background-color: #3a3a5e;
                color: #ffffff;
                border: 1px solid #505080;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a4a7e;
                border: 1px solid #00aaff;
            }
            QPushButton:pressed {
                background-color: #00aaff;
            }
            QPushButton#primaryBtn {
                background-color: #00aaff;
                color: #ffffff;
            }
            QPushButton#primaryBtn:hover {
                background-color: #0088dd;
            }
            QPushButton#dangerBtn {
                background-color: #d9534f;
            }
            QPushButton#dangerBtn:hover {
                background-color: #c9302c;
            }
            QPushButton#successBtn {
                background-color: #5cb85c;
            }
            QPushButton#successBtn:hover {
                background-color: #449d44;
            }
            QLabel {
                color: #e0e0e0;
                background-color: transparent;
            }
            QComboBox {
                background-color: #3a3a5e;
                color: #ffffff;
                border: 1px solid #505080;
                border-radius: 6px;
                padding: 6px;
                min-width: 120px;
            }
            QComboBox:hover { border: 1px solid #00aaff; }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a3e;
                color: #ffffff;
                selection-background-color: #00aaff;
                border: 1px solid #505080;
            }
            QSlider::groove:horizontal {
                background: #3a3a5e;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00aaff;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover { background: #0088dd; }
            QSpinBox {
                background-color: #3a3a5e;
                color: #ffffff;
                border: 1px solid #505080;
                border-radius: 6px;
                padding: 4px;
            }
            QSpinBox:hover { border: 1px solid #00aaff; }
            QScrollArea {
                background-color: #1e1e2e;
                border: none;
            }
            QScrollBar:vertical {
                background: #1e1e2e;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #3a3a5e;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background: #00aaff; }
        """)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # LEFT PANEL
        left_panel = QWidget()
        left_panel.setMaximumWidth(380)
        left_panel.setMinimumWidth(340)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)

        title = QLabel("🎨 Gradient Generator Pro")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00aaff; padding: 8px;")
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)

        # Gradient Type
        type_group = QGroupBox("Gradient Type")
        type_layout = QVBoxLayout(type_group)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Linear", "Radial", "Conic"])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.type_combo)

        angle_row = QHBoxLayout()
        angle_row.addWidget(QLabel("Angle:"))
        self.angle_slider = QSlider(Qt.Horizontal)
        self.angle_slider.setRange(0, 360)
        self.angle_slider.setValue(90)
        self.angle_slider.valueChanged.connect(self._on_angle_changed)
        angle_row.addWidget(self.angle_slider)
        self.angle_label = QLabel("90°")
        self.angle_label.setMinimumWidth(40)
        angle_row.addWidget(self.angle_label)
        type_layout.addLayout(angle_row)
        left_layout.addWidget(type_group)

        # Color Stops
        stops_group = QGroupBox("Color Stops")
        stops_layout = QVBoxLayout(stops_group)

        self.gradient_bar = GradientBar()
        self.gradient_bar.gradientChanged.connect(self._update_preview)
        stops_layout.addWidget(self.gradient_bar)

        hint = QLabel("💡 Double-click bar to add stop • Right-click to remove")
        hint.setStyleSheet("font-size: 10px; color: #888; font-style: italic;")
        hint.setWordWrap(True)
        stops_layout.addWidget(hint)

        color_row = QHBoxLayout()
        self.color1_btn = QPushButton("Color 1")
        self.color1_btn.setStyleSheet("background-color: #ff5e48;")
        self.color1_btn.clicked.connect(lambda: self._pick_color(0))
        color_row.addWidget(self.color1_btn)

        self.color2_btn = QPushButton("Color 2")
        self.color2_btn.setStyleSheet("background-color: #ff9a5e;")
        self.color2_btn.clicked.connect(lambda: self._pick_color(-1))
        color_row.addWidget(self.color2_btn)
        stops_layout.addLayout(color_row)

        hex_row = QHBoxLayout()
        hex_row.addWidget(QLabel("HEX:"))
        self.hex_input = QComboBox()
        self.hex_input.setEditable(True)
        self.hex_input.setMinimumWidth(120)
        self.hex_input.addItem("#FF5E48")
        self.hex_input.addItem("#FF9A5E")
        self.hex_input.lineEdit().returnPressed.connect(self._apply_hex_color)
        hex_row.addWidget(self.hex_input)
        stops_layout.addLayout(hex_row)

        left_layout.addWidget(stops_group)

        # Actions
        action_group = QGroupBox("Actions")
        action_layout = QVBoxLayout(action_group)

        self.random_btn = QPushButton("🎲 Random Gradient")
        self.random_btn.setObjectName("primaryBtn")
        self.random_btn.clicked.connect(self._random_gradient)
        action_layout.addWidget(self.random_btn)

        self.animate_btn = QPushButton("▶ Start Animation")
        self.animate_btn.clicked.connect(self._toggle_animation)
        action_layout.addWidget(self.animate_btn)

        btn_grid = QGridLayout()
        self.copy_css_btn = QPushButton("📋 Copy CSS")
        self.copy_css_btn.setObjectName("successBtn")
        self.copy_css_btn.clicked.connect(self._copy_css)
        btn_grid.addWidget(self.copy_css_btn, 0, 0)

        self.copy_hex_btn = QPushButton("📋 Copy HEX")
        self.copy_hex_btn.clicked.connect(self._copy_hex)
        btn_grid.addWidget(self.copy_hex_btn, 0, 1)

        self.save_btn = QPushButton("💾 Save Config")
        self.save_btn.clicked.connect(self._save_config)
        btn_grid.addWidget(self.save_btn, 1, 0)

        self.load_btn = QPushButton("📂 Load Config")
        self.load_btn.clicked.connect(self._load_config)
        btn_grid.addWidget(self.load_btn, 1, 1)

        action_layout.addLayout(btn_grid)
        left_layout.addWidget(action_group)

        # Export
        export_group = QGroupBox("Export")
        export_layout = QVBoxLayout(export_group)

        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Width:"))
        self.export_width = QSpinBox()
        self.export_width.setRange(100, 4096)
        self.export_width.setValue(1920)
        self.export_width.valueChanged.connect(self._on_width_changed)
        size_row.addWidget(self.export_width)
        size_row.addWidget(QLabel("Height:"))
        self.export_height = QSpinBox()
        self.export_height.setRange(100, 4096)
        self.export_height.setValue(1080)
        self.export_height.valueChanged.connect(self._on_height_changed)
        size_row.addWidget(self.export_height)
        export_layout.addLayout(size_row)

        self.lock_ratio_btn = QPushButton("🔒 Ratio Locked")
        self.lock_ratio_btn.setCheckable(True)
        self.lock_ratio_btn.setChecked(True)
        self.lock_ratio_btn.clicked.connect(self._toggle_ratio_lock)
        export_layout.addWidget(self.lock_ratio_btn)

        export_btn_row = QHBoxLayout()
        self.export_png_btn = QPushButton("🖼️ Export PNG")
        self.export_png_btn.setObjectName("successBtn")
        self.export_png_btn.clicked.connect(self._export_png)
        export_btn_row.addWidget(self.export_png_btn)

        self.export_svg_btn = QPushButton("📐 Export SVG")
        self.export_svg_btn.clicked.connect(self._export_svg)
        export_btn_row.addWidget(self.export_svg_btn)
        export_layout.addLayout(export_btn_row)

        left_layout.addWidget(export_group)
        left_layout.addStretch()

        # CENTER - Preview
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)

        preview_label = QLabel("Preview")
        preview_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #00aaff; padding: 4px;")
        preview_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(preview_label)

        self.preview = GradientPreview()
        center_layout.addWidget(self.preview, 1)

        css_group = QGroupBox("Generated CSS Code")
        css_layout = QVBoxLayout(css_group)
        self.css_output = QLabel()
        self.css_output.setWordWrap(True)
        self.css_output.setStyleSheet("""
            background-color: #0d0d1a;
            color: #00ff88;
            padding: 12px;
            border-radius: 6px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 11px;
            border: 1px solid #404060;
        """)
        self.css_output.setMinimumHeight(80)
        self.css_output.setTextInteractionFlags(Qt.TextSelectableByMouse)
        css_layout.addWidget(self.css_output)

        css_btn_row = QHBoxLayout()
        self.copy_css2_btn = QPushButton("📋 Copy CSS Code")
        self.copy_css2_btn.setObjectName("successBtn")
        self.copy_css2_btn.clicked.connect(self._copy_css)
        css_btn_row.addWidget(self.copy_css2_btn)
        css_layout.addLayout(css_btn_row)

        center_layout.addWidget(css_group)

        # RIGHT PANEL - Presets
        right_panel = QWidget()
        right_panel.setMaximumWidth(320)
        right_panel.setMinimumWidth(280)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        preset_title = QLabel("✨ Presets")
        preset_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00aaff; padding: 4px;")
        preset_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(preset_title)

        self.preset_search = QComboBox()
        self.preset_search.setEditable(True)
        self.preset_search.setPlaceholderText("🔍 Search presets...")
        self.preset_search.lineEdit().textChanged.connect(self._filter_presets)
        right_layout.addWidget(self.preset_search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.presets_container = QWidget()
        self.presets_layout = QGridLayout(self.presets_container)
        self.presets_layout.setSpacing(8)
        self.presets_layout.setContentsMargins(4, 4, 4, 4)
        self.presets_layout.setColumnStretch(0, 1)
        self.presets_layout.setColumnStretch(1, 1)

        self._populate_presets()

        scroll.setWidget(self.presets_container)
        right_layout.addWidget(scroll, 1)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(center_panel, 1)
        main_layout.addWidget(right_panel)

        self.statusBar().showMessage("Ready | Double-click gradient bar to add color stops")

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+R"), self, self._random_gradient)
        QShortcut(QKeySequence("Ctrl+S"), self, self._save_config)
        QShortcut(QKeySequence("Ctrl+O"), self, self._load_config)
        QShortcut(QKeySequence("Ctrl+C"), self, self._copy_css)
        QShortcut(QKeySequence("Ctrl+E"), self, self._export_png)
        QShortcut(QKeySequence("Space"), self, self._toggle_animation)

    def _populate_presets(self, filter_text=""):
        for i in reversed(range(self.presets_layout.count())):
            item = self.presets_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        row, col = 0, 0
        filter_lower = filter_text.lower()
        for name, colors in GRADIENT_PRESETS.items():
            if filter_text and filter_lower not in name.lower():
                continue
            btn = PresetButton(name, colors)
            btn.clicked.connect(lambda checked, n=name, c=colors: self._apply_preset(n, c))
            self.presets_layout.addWidget(btn, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1

    def _filter_presets(self, text):
        self._populate_presets(text)

    def _apply_preset(self, name, colors):
        stops = []
        n = len(colors)
        for i, color in enumerate(colors):
            pos = i / (n - 1) if n > 1 else 0
            stops.append((pos, QColor(*color)))
        self.gradient_bar.set_color_stops(stops)
        self._update_color_buttons()
        self.statusBar().showMessage(f"Applied preset: {name}", 3000)

    def _update_color_buttons(self):
        stops = self.gradient_bar.get_color_stops()
        if len(stops) >= 1:
            self.color1_btn.setStyleSheet(f"background-color: {stops[0][1].name()};")
            self.color1_btn.setText(f"Color 1: {stops[0][1].name()}")
        if len(stops) >= 2:
            self.color2_btn.setStyleSheet(f"background-color: {stops[-1][1].name()};")
            self.color2_btn.setText(f"Color 2: {stops[-1][1].name()}")

        self.hex_input.clear()
        for pos, color in stops:
            self.hex_input.addItem(color.name())

    def _pick_color(self, index):
        stops = self.gradient_bar.get_color_stops()
        if index == -1:
            index = len(stops) - 1
        if 0 <= index < len(stops):
            current_color = stops[index][1]
            color = QColorDialog.getColor(current_color, self, "Select Color")
            if color.isValid():
                stops[index] = (stops[index][0], color)
                self.gradient_bar.set_color_stops(stops)
                self._update_color_buttons()

    def _apply_hex_color(self):
        hex_value = self.hex_input.currentText().strip()
        if not hex_value.startswith('#'):
            hex_value = '#' + hex_value
        try:
            color = QColor(hex_value)
            if color.isValid():
                stops = self.gradient_bar.get_color_stops()
                if stops:
                    idx = self.gradient_bar.selected_index
                    if idx < 0 or idx >= len(stops):
                        idx = 0
                    stops[idx] = (stops[idx][0], color)
                    self.gradient_bar.set_color_stops(stops)
                    self._update_color_buttons()
                    self.statusBar().showMessage(f"Applied color: {hex_value}", 2000)
        except:
            QMessageBox.warning(self, "Invalid Color", "Please enter a valid hex color (e.g., #FF5E48)")

    def _on_type_changed(self, text):
        self.preview.gradient_type = text.lower()
        self._update_preview()

    def _on_angle_changed(self, value):
        self.preview.angle = value
        self.angle_label.setText(f"{value}°")
        self._update_preview()

    def _on_width_changed(self, value):
        if self.ratio_locked:
            ratio = 1920 / 1080
            new_height = int(value / ratio)
            self.export_height.blockSignals(True)
            self.export_height.setValue(new_height)
            self.export_height.blockSignals(False)

    def _on_height_changed(self, value):
        if self.ratio_locked:
            ratio = 1920 / 1080
            new_width = int(value * ratio)
            self.export_width.blockSignals(True)
            self.export_width.setValue(new_width)
            self.export_width.blockSignals(False)

    def _toggle_ratio_lock(self):
        self.ratio_locked = self.lock_ratio_btn.isChecked()
        if self.ratio_locked:
            self.lock_ratio_btn.setText("🔒 Ratio Locked")
        else:
            self.lock_ratio_btn.setText("🔓 Ratio Unlocked")

    def _update_preview(self):
        stops = self.gradient_bar.get_color_stops()
        self.preview.set_gradient(
            self.type_combo.currentText().lower(),
            self.angle_slider.value(),
            stops
        )
        self._update_css_output()
        self._update_color_buttons()

    def _update_css_output(self):
        stops = self.gradient_bar.get_color_stops()
        gtype = self.type_combo.currentText().lower()

        stops_str = ", ".join([f"{c.name()} {p*100:.1f}%" for p, c in stops])

        if gtype == "linear":
            css = f"background: linear-gradient({self.angle_slider.value()}deg, {stops_str});"
        elif gtype == "radial":
            css = f"background: radial-gradient(circle, {stops_str});"
        elif gtype == "conic":
            css = f"background: conic-gradient(from {self.angle_slider.value()}deg, {stops_str});"
        else:
            css = f"background: linear-gradient({self.angle_slider.value()}deg, {stops_str});"

        self.css_output.setText(css)

    def _random_gradient(self):
        num_stops = random.randint(2, 4)
        stops = []

        base_hue = random.randint(0, 360)
        scheme = random.choice(["analogous", "complementary", "triadic", "monochromatic"])

        for i in range(num_stops):
            if scheme == "analogous":
                hue = (base_hue + i * 30) % 360
                sat = random.randint(60, 100)
                light = random.randint(40, 70)
            elif scheme == "complementary":
                hue = (base_hue + (i * 180)) % 360
                sat = random.randint(70, 100)
                light = random.randint(45, 65)
            elif scheme == "triadic":
                hue = (base_hue + i * 120) % 360
                sat = random.randint(70, 100)
                light = random.randint(45, 65)
            else:
                hue = base_hue
                sat = random.randint(50, 100)
                light = 30 + i * (50 // num_stops)

            color = QColor.fromHsl(hue, sat, light)
            pos = i / (num_stops - 1) if num_stops > 1 else 0
            stops.append((pos, color))

        self.gradient_bar.set_color_stops(stops)
        self.angle_slider.setValue(random.randint(0, 360))
        self._update_preview()
        self.statusBar().showMessage(f"🎲 Random gradient generated ({scheme} scheme)", 3000)

    def _toggle_animation(self):
        if self.animation_timer.isActive():
            self.animation_timer.stop()
            self.preview.animate = False
            self.preview.animation_offset = 0
            self.animate_btn.setText("▶ Start Animation")
            self.preview.update()
        else:
            self.preview.animate = True
            self.animation_timer.start(30)
            self.animate_btn.setText("⏸ Stop Animation")

    def _animate_step(self):
        self.preview.animation_offset = (self.preview.animation_offset + 2) % 360
        self.preview.update()

    def _copy_css(self):
        css = self.css_output.text()
        clipboard = QApplication.clipboard()
        clipboard.setText(css)
        self.statusBar().showMessage("✅ CSS code copied to clipboard!", 3000)

    def _copy_hex(self):
        stops = self.gradient_bar.get_color_stops()
        hex_values = ", ".join([c.name() for p, c in stops])
        clipboard = QApplication.clipboard()
        clipboard.setText(hex_values)
        self.statusBar().showMessage(f"✅ Colors copied: {hex_values}", 3000)

    def _save_config(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Gradient Config", "",
            "JSON Files (*.json);;All Files (*)"
        )
        if filename:
            config = {
                "type": self.type_combo.currentText().lower(),
                "angle": self.angle_slider.value(),
                "stops": [(p, c.name()) for p, c in self.gradient_bar.get_color_stops()],
                "export_width": self.export_width.value(),
                "export_height": self.export_height.value(),
                "saved_at": datetime.now().isoformat()
            }
            try:
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=2)
                self.statusBar().showMessage(f"💾 Saved to {filename}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")

    def _load_config(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Gradient Config", "",
            "JSON Files (*.json);;All Files (*)"
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                self.type_combo.setCurrentText(config["type"].capitalize())
                self.angle_slider.setValue(config["angle"])
                stops = [(p, QColor(c)) for p, c in config["stops"]]
                self.gradient_bar.set_color_stops(stops)
                if "export_width" in config:
                    self.export_width.setValue(config["export_width"])
                if "export_height" in config:
                    self.export_height.setValue(config["export_height"])
                self._update_preview()
                self.statusBar().showMessage(f"📂 Loaded from {filename}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load: {str(e)}")

    def _export_png(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export PNG", "gradient.png",
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        if filename:
            width = self.export_width.value()
            height = self.export_height.value()
            
            # ✅ FIXED: Use QPixmap for fast export
            pixmap = QPixmap(width, height)
            pixmap.fill(Qt.transparent)

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            stops = self.gradient_bar.get_color_stops()
            gtype = self.type_combo.currentText().lower()
            angle = self.angle_slider.value()
            rect = pixmap.rect()

            if gtype == "linear":
                angle_rad = math.radians(angle - 90)
                cx, cy = rect.center().x(), rect.center().y()
                length = max(rect.width(), rect.height())
                dx = math.cos(angle_rad) * length / 2
                dy = math.sin(angle_rad) * length / 2
                gradient = QLinearGradient(QPointF(cx - dx, cy - dy), QPointF(cx + dx, cy + dy))
            elif gtype == "radial":
                gradient = QRadialGradient(QPointF(rect.center()), max(rect.width(), rect.height()) / 2)
            elif gtype == "conic":
                gradient = QConicalGradient(QPointF(rect.center()), angle)

            for pos, color in stops:
                gradient.setColorAt(pos, color)

            painter.fillRect(rect, QBrush(gradient))
            painter.end()

            if not pixmap.save(filename):
                QMessageBox.critical(self, "Error", "Failed to save image")
            else:
                self.statusBar().showMessage(f"🖼️ Exported to {filename} ({width}x{height})", 3000)

    def _export_svg(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export SVG", "gradient.svg",
            "SVG Files (*.svg);;All Files (*)"
        )
        if filename:
            width = self.export_width.value()
            height = self.export_height.value()
            stops = self.gradient_bar.get_color_stops()
            gtype = self.type_combo.currentText().lower()
            angle = self.angle_slider.value()

            try:
                svg_lines = [
                    f'<?xml version="1.0" encoding="UTF-8"?>',
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                ]

                if gtype == "linear":
                    # ✅ FIXED: Correct SVG angle calculation
                    angle_rad = math.radians(angle - 90)
                    x1 = 50 - math.cos(angle_rad) * 50
                    y1 = 50 - math.sin(angle_rad) * 50
                    x2 = 50 + math.cos(angle_rad) * 50
                    y2 = 50 + math.sin(angle_rad) * 50
                    svg_lines.append(f'  <defs>')
                    svg_lines.append(f'    <linearGradient id="grad" x1="{x1}%" y1="{y1}%" x2="{x2}%" y2="{y2}%">')
                    for pos, color in stops:
                        svg_lines.append(f'      <stop offset="{pos*100:.1f}%" stop-color="{color.name()}"/>')
                    svg_lines.append(f'    </linearGradient>')
                    svg_lines.append(f'  </defs>')
                elif gtype == "radial":
                    svg_lines.append(f'  <defs>')
                    svg_lines.append(f'    <radialGradient id="grad" cx="50%" cy="50%" r="50%">')
                    for pos, color in stops:
                        svg_lines.append(f'      <stop offset="{pos*100:.1f}%" stop-color="{color.name()}"/>')
                    svg_lines.append(f'    </radialGradient>')
                    svg_lines.append(f'  </defs>')
                else:
                    svg_lines.append(f'  <defs>')
                    svg_lines.append(f'    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">')
                    for pos, color in stops:
                        svg_lines.append(f'      <stop offset="{pos*100:.1f}%" stop-color="{color.name()}"/>')
                    svg_lines.append(f'    </linearGradient>')
                    svg_lines.append(f'  </defs>')

                svg_lines.append(f'  <rect width="{width}" height="{height}" fill="url(#grad)"/>')
                svg_lines.append(f'</svg>')

                with open(filename, 'w') as f:
                    f.write('\n'.join(svg_lines))
                self.statusBar().showMessage(f"📐 SVG exported to {filename}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export SVG: {str(e)}")

    def closeEvent(self, event):
        self.animation_timer.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Gradient Generator Pro")

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = GradientGeneratorApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()