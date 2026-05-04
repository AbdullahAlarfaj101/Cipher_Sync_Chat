from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextBrowser, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QTimer
from PyQt6.QtGui import QCursor, QFont
from datetime import datetime
import html


class ChatWindow(QWidget):
    # Core Communication Signals
    send_text_signal = pyqtSignal(str)
    send_file_signal = pyqtSignal()
    record_audio_signal = pyqtSignal()
    typing_signal = pyqtSignal(bool)
    link_clicked_signal = pyqtSignal(str)  # Signal carrying the clicked media link

    def __init__(self, my_id: str, target_id: str):
        super().__init__()
        self.my_id = my_id
        self.target_id = target_id
        self.dragPos = None
        self.is_typing = False

        # Timer to reset "typing" status after inactivity
        self.typing_timer = QTimer()
        self.typing_timer.setInterval(3500)  # 3.5 seconds timeout
        self.typing_timer.timeout.connect(self.stop_typing_status)

        self.init_ui()

        # Bind link click events to the handler
        self.chat_display.anchorClicked.connect(lambda url: self.link_clicked_signal.emit(url.toString()))

    def init_ui(self):
        # ==========================================
        # 1. Main Window Configuration
        # ==========================================
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(600, 600)
        self.resize(700, 750)

        self.setStyleSheet("""
            QWidget {
                background-color: #0c0c0c;
                color: #00ff00;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QTextBrowser {
                background-color: #050505;
                border: 1px solid #004400;
                padding: 10px;
                font-size: 14px;
                line-height: 1.5;
            }
            QLineEdit {
                background-color: #000000;
                color: #00ff00;
                border: 1px solid #005500;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #00ff00; }
            QPushButton {
                background-color: #002200;
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00ff00;
                color: #000000;
            }
            QPushButton#ctrl_btn {
                background-color: transparent;
                border: none;
                font-size: 16px;
                padding: 0px;
                color: #00aa00;
            }
            QPushButton#ctrl_btn:hover { color: #ff0000; }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ==========================================
        # 2. Top Bar (Window Controls & Target Info)
        # ==========================================
        top_bar = QHBoxLayout()

        # Target information and connection status
        target_info_layout = QVBoxLayout()
        target_info_layout.setSpacing(2)

        self.target_label = QLabel(f"TARGET: [{self.target_id}]")
        self.target_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.status_label = QLabel("STATUS: [OFFLINE]")
        self.status_label.setStyleSheet("color: #888888; font-size: 12px;") 

        self.typing_indicator = QLabel("") 
        self.typing_indicator.setStyleSheet("color: #00ff00; font-style: italic; font-size: 12px;")

        target_info_layout.addWidget(self.target_label)
        target_info_layout.addWidget(self.status_label)
        target_info_layout.addWidget(self.typing_indicator)

        top_bar.addLayout(target_info_layout)
        top_bar.addStretch()

        # Window Control Buttons (Minimize, Maximize, Close)
        min_btn = QPushButton("[-]")
        min_btn.setObjectName("ctrl_btn")
        min_btn.clicked.connect(self.showMinimized)

        max_btn = QPushButton("[O]")
        max_btn.setObjectName("ctrl_btn")
        max_btn.clicked.connect(self.toggle_maximize)

        close_btn = QPushButton("[X]")
        close_btn.setObjectName("ctrl_btn")
        close_btn.clicked.connect(QApplication.instance().quit)

        for btn in [min_btn, max_btn, close_btn]:
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            top_bar.addWidget(btn)

        main_layout.addLayout(top_bar)

        # ==========================================
        # 3. Chat Log Display Area
        # ==========================================
        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(False)
        self.chat_display.setOpenLinks(False)

        self.chat_display.append(f"<i>[SYSTEM] Secure Tunnel Established with {self.target_id}...</i><br>")
        main_layout.addWidget(self.chat_display)

        # ==========================================
        # 4. Input Area & Toolbar
        # ==========================================
        input_layout = QHBoxLayout()
        input_layout.setSpacing(5)

        # File attachment button
        self.btn_file = QPushButton("[FILE]")
        self.btn_file.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_file.clicked.connect(self.send_file_signal.emit)

        # Audio recording button
        self.btn_audio = QPushButton("[MIC]")
        self.btn_audio.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_audio.clicked.connect(self.record_audio_signal.emit)

        # Text input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("TYPE SECURE MESSAGE...")
        self.input_field.textChanged.connect(self.handle_typing)
        self.input_field.returnPressed.connect(self.handle_send_text)  

        # Send message button
        self.btn_send = QPushButton("[SEND]")
        self.btn_send.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_send.clicked.connect(self.handle_send_text)

        input_layout.addWidget(self.btn_file)
        input_layout.addWidget(self.btn_audio)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.btn_send)

        main_layout.addLayout(input_layout)
        self.setLayout(main_layout)

    # ==========================================
    # 5. UI & Message Control Methods
    # ==========================================
    def append_message(self, sender_id: str, text: str, msg_type="text"):
        """Appends a message to the chat log with HTML table formatting and link support."""
        import html
        from datetime import datetime
        from PyQt6.QtWidgets import QApplication

        time_now = datetime.now().strftime("%H:%M:%S")
        raw_payload = text

        # Prepare content display based on message type
        if msg_type == "audio":
            display_text = f"<a href='play:{raw_payload}' style='color:#ffff00; text-decoration:none;'>[ 🔊 SECURE AUDIO MESSAGE ]</a>"
        elif msg_type == "file":
            # Extract and display the original filename without the timestamp
            clean_name = raw_payload.split('_', 1)[-1] if '_' in raw_payload else raw_payload
            display_text = f"<a href='download:{raw_payload}' style='color:#ffff00; text-decoration:none;'>[ 📂 FILE: {clean_name} ]</a>"
        else:
            display_text = f"<span style='color:#00ff00; white-space: pre-wrap;'>{html.escape(text)}</span>"

        time_tag = f"<span style='color:#555555;'>[{time_now}]</span>"

        if str(sender_id).strip() == str(self.my_id).strip():
            # --- Left-aligned layout (Local User) ---
            sender_tag = f"<span style='color:#00aaaa;'>[YOU]</span>&nbsp;&lt;&lt;"
            log_entry = f"""
            <table width='100%' style='margin-bottom: 5px;'>
                <tr>
                    <td width='1%' style='vertical-align: top; white-space: nowrap;'>{time_tag}&nbsp;</td>
                    <td width='1%' style='vertical-align: top; white-space: nowrap;'>{sender_tag}&nbsp;</td>
                    <td align='left' style='vertical-align: top;'>{display_text}</td>
                </tr>
            </table>
            """
        else:
            # --- Right-aligned layout (Remote Target) ---
            sender_tag = f"&gt;&gt;&nbsp;<span style='color:#aa0000;'>[{sender_id}]</span>"
            log_entry = f"""
            <table width='100%' style='margin-bottom: 5px;'>
                <tr>
                    <td width='100%' align='right' style='vertical-align: top;'>{display_text}</td>
                    <td width='1%' style='vertical-align: top; white-space: nowrap;'>&nbsp;{sender_tag}</td>
                    <td width='1%' style='vertical-align: top; white-space: nowrap;'>&nbsp;{time_tag}</td>
                </tr>
            </table>
            """

        self.chat_display.append(log_entry)
        QApplication.processEvents()

        scroll_bar = self.chat_display.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    def update_target_status(self, is_online: bool, is_typing: bool):
        """Updates UI status indicators based on server presence data."""
        if is_online:
            self.status_label.setText("STATUS: [ONLINE]")
            self.status_label.setStyleSheet("color: #00ff00; font-size: 12px;")
        else:
            self.status_label.setText("STATUS: [OFFLINE]")
            self.status_label.setStyleSheet("color: #888888; font-size: 12px;")

        if is_typing:
            self.typing_indicator.setText("> INCOMING TRANSMISSION...")
        else:
            self.typing_indicator.setText("")

    def handle_send_text(self):
        """Processes input text and emits the send signal."""
        text = self.input_field.text().strip()
        if text:
            self.send_text_signal.emit(text)  
            self.append_message(self.my_id, text)  
            self.input_field.clear()
            self.stop_typing_status()

    def handle_typing(self):
        """Broadcasts 'typing' status to the network."""
        if not self.is_typing:
            self.is_typing = True
            self.typing_signal.emit(True)
        # Reset timer on each keystroke
        self.typing_timer.start()

    def stop_typing_status(self):
        """Broadcasts 'stopped typing' status to the network."""
        self.typing_timer.stop()
        if self.is_typing:
            self.is_typing = False
            self.typing_signal.emit(False)

    # ==========================================
    # 6. Window Drag & Resize Handlers
    # ==========================================
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragPos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragPos is not None and event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.dragPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.dragPos = event.globalPosition().toPoint()
            event.accept()
