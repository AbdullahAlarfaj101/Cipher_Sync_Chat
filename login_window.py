import os
import random
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QHBoxLayout, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QCursor


class LoginWindow(QWidget):
    connection_successful = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.my_id = self.load_or_generate_id()
        self.dragPos = None  # Tracks mouse position during window drag
        self.init_ui()

    def load_or_generate_id(self):
        id_file = "assets/my_id.txt"
        os.makedirs(os.path.dirname(id_file), exist_ok=True)
        if os.path.exists(id_file):
            with open(id_file, "r") as f:
                return f.read().strip()
        else:
            new_id = str(random.randint(100000, 999999))
            with open(id_file, "w") as f:
                f.write(new_id)
            return new_id

    def init_ui(self):
        # ==========================================
        # 1. Window Configuration (Frameless & Resizable)
        # ==========================================
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(400, 500)
        self.resize(450, 550)

        # Terminal theme styling with custom control buttons
        self.setStyleSheet("""
            QWidget {
                background-color: #0c0c0c;
                color: #00ff00;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QLabel { font-size: 14px; }
            QLineEdit {
                background-color: #000000;
                color: #00ff00;
                border: 1px solid #005500;
                padding: 10px;
                font-size: 24px;
                letter-spacing: 5px;
            }
            QLineEdit:focus { border: 1px solid #00ff00; }
            QPushButton {
                background-color: #002200;
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00ff00;
                color: #000000;
            }
            /* Custom top control buttons styling */
            QPushButton#ctrl_btn {
                background-color: transparent;
                border: none;
                font-size: 16px;
                padding: 0px;
            }
            QPushButton#ctrl_btn:hover {
                color: #ff0000; /* Turn red on hover */
                background-color: transparent;
            }
        """)

        # ==========================================
        # 2. Main Layout Structure
        # ==========================================
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 40)
        main_layout.setSpacing(20)

        # -- Custom Top Control Bar (Minimize & Close) --
        top_bar = QHBoxLayout()
        top_bar.addStretch()

        min_btn = QPushButton("[-]")
        min_btn.setObjectName("ctrl_btn")
        min_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        min_btn.clicked.connect(self.showMinimized)

        close_btn = QPushButton("[X]")
        close_btn.setObjectName("ctrl_btn")
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.clicked.connect(QApplication.instance().quit)

        top_bar.addWidget(min_btn)
        top_bar.addWidget(close_btn)
        main_layout.addLayout(top_bar)

        # -- UI Content (Wrapped in sub-layout for scalability) --
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 0, 30, 0)

        title_label = QLabel("[ SECURE RELAY PROTOCOL ]")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        content_layout.addWidget(title_label)

        my_id_label = QLabel("YOUR SECURE PIN:")
        my_id_label.setStyleSheet("color: #008800;")

        self.id_display = QLabel(f"> {self.my_id}")
        self.id_display.setStyleSheet("font-size: 32px; font-weight: bold; margin-bottom: 30px;")

        content_layout.addWidget(my_id_label)
        content_layout.addWidget(self.id_display)

        target_label = QLabel("ENTER TARGET PIN:")
        target_label.setStyleSheet("color: #008800;")
        content_layout.addWidget(target_label)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("______")
        self.target_input.setMaxLength(6)
        self.target_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.target_input)

        usb_layout = QHBoxLayout()
        self.usb_indicator = QLabel("●")
        self.usb_indicator.setStyleSheet("color: #00ff00; font-size: 20px;")
        self.usb_text = QLabel("CRYPTO KEY: DETECTED")
        usb_layout.addWidget(self.usb_indicator)
        usb_layout.addWidget(self.usb_text)
        usb_layout.addStretch()
        content_layout.addLayout(usb_layout)

        self.connect_btn = QPushButton("INITIATE CONNECTION")
        self.connect_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.connect_btn.clicked.connect(self.handle_connection)
        content_layout.addWidget(self.connect_btn)

        self.status_label = QLabel("SYSTEM READY_")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #008800; margin-top: 10px;")
        content_layout.addWidget(self.status_label)

        content_layout.addStretch()
        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

    def handle_connection(self):
        target_pin = self.target_input.text().strip()
        if not target_pin.isdigit() or len(target_pin) < 5:
            self.status_label.setStyleSheet("color: #ff0000;")
            self.status_label.setText("ERR: INVALID PIN FORMAT")
            return
        if target_pin == self.my_id:
            self.status_label.setStyleSheet("color: #ff0000;")
            self.status_label.setText("ERR: CANNOT CONNECT TO SELF")
            return

        self.status_label.setStyleSheet("color: #00ff00;")
        self.status_label.setText("ESTABLISHING SECURE TUNNEL...")
        self.connection_successful.emit(target_pin)

    # ==========================================
    # 3. Mouse Drag & Window Move Handlers
    # ==========================================
    def mousePressEvent(self, event):
        """Stores the initial mouse position on click."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        """Moves the window based on mouse drag coordinates."""
        if self.dragPos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.dragPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.dragPos = event.globalPosition().toPoint()
            event.accept()
