import sys
import os
import asyncio
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt6.QtCore import QThread, pyqtSignal, QTimer

# Core Managers
from crypto_manager import CryptoManager
from network_supabase import SupabaseManager
from local_db import LocalDatabase
from audio_handler import SecureAudioHandler

# UI Components
from login_window import LoginWindow
from chat_window import ChatWindow


# ==========================================
# Background Listener Thread
# ==========================================
class ListenerThread(QThread):
    message_received_signal = pyqtSignal(str, bytes)

    def __init__(self, network_manager):
        super().__init__()
        self.network = network_manager

    def run(self):
        """Creates a dedicated event loop for the background network listener."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        def callback(sender_id, encrypted_bytes):
            self.message_received_signal.emit(sender_id, encrypted_bytes)

        loop.run_until_complete(self.network.start_listening(callback))


# ==========================================
# Main Application Controller
# ==========================================
class AppController:
    def __init__(self):
        # 1. Load environment variables for secure credential management
        load_dotenv()
        self.SUPABASE_URL = os.getenv("SUPABASE_URL")
        self.SUPABASE_KEY = os.getenv("SUPABASE_KEY")

        if not self.SUPABASE_URL or not self.SUPABASE_KEY:
            raise ValueError("Missing Supabase credentials. Please configure the .env file.")

        # 2. Initialize core handlers
        self.crypto = CryptoManager()
        self.db = LocalDatabase()
        self.audio = SecureAudioHandler()

        # Session state variables
        self.network = None
        self.chat_window = None
        self.listener = None
        self.session_key = None

        # 3. Initialize and display the login window
        self.login_window = LoginWindow()
        self.login_window.connection_successful.connect(self.start_session)
        QApplication.instance().aboutToQuit.connect(self.cleanup_on_exit)
        self.login_window.show()

        # 4. Initialize presence polling timer
        self.presence_timer = QTimer()
        self.presence_timer.setInterval(2000)
        self.presence_timer.timeout.connect(self.update_friend_status)

    def start_session(self, target_id: str):
        my_id = self.login_window.my_id

        # 1. Initialize network connection and set presence status
        self.network = SupabaseManager(self.SUPABASE_URL, self.SUPABASE_KEY, my_id)
        self.network.set_online_status(True)

        # 2. Load or generate the encryption session key
        print("System: Initializing encryption key manager...")
        key_file = "assets/usb_key.bin"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                self.session_key = f.read()
        else:
            self.session_key = self.crypto.generate_usb_master_key()
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, "wb") as f:
                f.write(self.session_key)

        # 3. Transition UI states
        self.chat_window = ChatWindow(my_id, target_id)
        self.chat_window.show()
        self.login_window.close()

        QApplication.processEvents()

        # 4. Load chat history and process pending remote messages
        self.load_local_history(target_id)

        pending = self.network.fetch_pending_messages()
        for msg in pending:
            self.receive_secure_message(msg['sender_id'], bytes.fromhex(msg['payload']))

        # 5. Bind UI signals to controller methods
        self.chat_window.send_text_signal.connect(self.send_secure_message)
        self.chat_window.typing_signal.connect(self.network.set_typing_status)
        self.chat_window.record_audio_signal.connect(self.handle_audio_recording)
        self.chat_window.send_file_signal.connect(self.handle_file_selection)
        self.chat_window.link_clicked_signal.connect(self.handle_link_click)

        # 6. Start background listener and presence polling
        self.listener = ListenerThread(self.network)
        self.listener.message_received_signal.connect(self.receive_secure_message)
        self.listener.start()

        self.presence_timer.start()

    def load_local_history(self, friend_id):
        """Loads and decrypts local chat history for the target session."""
        history = self.db.get_chat_history(friend_id)
        for sender_id, encrypted_content, timestamp, _ in history:
            try:
                decrypted = self.crypto.decrypt_data(self.session_key, encrypted_content)
                raw_text = decrypted.decode('utf-8')

                # Parse payload prefix to determine message type
                if raw_text.startswith("audio|"):
                    msg_type = "audio"
                    content = raw_text[6:]
                elif raw_text.startswith("file|"):
                    msg_type = "file"
                    content = raw_text[5:]
                elif raw_text.startswith("text|"):
                    msg_type = "text"
                    content = raw_text[5:]
                else:
                    msg_type = "text"
                    content = raw_text

                self.chat_window.append_message(sender_id, content, msg_type=msg_type)
            except Exception as e:
                pass

    def cleanup_on_exit(self):
        """Handles application shutdown sequence, updating network status."""
        if self.network:
            print("System: Terminating session and updating presence status...")
            self.network.set_online_status(False)

    # ==========================================
    # Message Routing & Handling
    # ==========================================
    def send_secure_message(self, content: str, msg_type="text"):
        """Formats, encrypts, and dispatches an outgoing message."""
        if not self.session_key: return

        # Format payload with type prefix prior to encryption
        payload_str = f"{msg_type}|{content}"
        message_bytes = payload_str.encode('utf-8')
        encrypted_payload = self.crypto.encrypt_data(self.session_key, message_bytes)

        # Persist locally and transmit remotely
        self.db.save_message(self.chat_window.my_id, self.chat_window.target_id, encrypted_payload)
        self.network.send_encrypted_payload(self.chat_window.target_id, encrypted_payload)

    def receive_secure_message(self, sender_id: str, encrypted_bytes: bytes):
        """Decrypts and processes incoming messages."""
        if sender_id != self.chat_window.target_id: return

        try:
            decrypted_bytes = self.crypto.decrypt_data(self.session_key, encrypted_bytes)
            raw_text = decrypted_bytes.decode('utf-8')

            # Parse payload prefix
            if raw_text.startswith("audio|"):
                msg_type = "audio"
                content = raw_text[6:]
            elif raw_text.startswith("file|"):
                msg_type = "file"
                content = raw_text[5:]
            elif raw_text.startswith("text|"):
                msg_type = "text"
                content = raw_text[5:]
            else:
                msg_type = "text"
                content = raw_text

            self.db.save_message(sender_id, self.chat_window.my_id, encrypted_bytes)
            self.chat_window.append_message(sender_id, content, msg_type=msg_type)

        except Exception as e:
            print(f"System Warning: Malformed payload or decryption failure: {e}")

    def handle_audio_recording(self):
        """Manages the audio recording lifecycle and payload transmission."""
        if not self.audio.is_recording:
            self.audio.start_recording()
            self.chat_window.btn_audio.setStyleSheet("background-color: #ff0000; color: #fff;")
            self.chat_window.btn_audio.setText("[ RECORDING... ]")
        else:
            self.chat_window.btn_audio.setStyleSheet("")
            self.chat_window.btn_audio.setText("[MIC]")

            audio_bytes = self.audio.stop_recording_and_get_bytes()

            try:
                encrypted_audio = self.crypto.encrypt_data(self.session_key, audio_bytes)
                file_key = self.network.upload_encrypted_file(encrypted_audio, "voice_msg.wav")

                self.send_secure_message(file_key, msg_type="audio")
                self.chat_window.append_message(self.chat_window.my_id, file_key, msg_type="audio")
            except Exception as e:
                print(f"System Error: Audio upload failed: {e}")

    def handle_file_selection(self):
        """Handles file selection, encryption, and dispatching."""
        if not self.session_key: return

        file_path, _ = QFileDialog.getOpenFileName(self.chat_window, "Select File to Encrypt and Send")
        if not file_path: return

        filename = os.path.basename(file_path)

        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()

            encrypted_file_bytes = self.crypto.encrypt_data(self.session_key, file_bytes)
            print(f"System: Uploading encrypted payload: {filename}...")
            secure_path = self.network.upload_encrypted_file(encrypted_file_bytes, filename)

            self.send_secure_message(secure_path, msg_type="file")
            self.chat_window.append_message(self.chat_window.my_id, secure_path, msg_type="file")

        except Exception as e:
            QMessageBox.critical(self.chat_window, "Security Error", f"File processing failed: {str(e)}")

    def update_friend_status(self):
        """Polls the network for the target user's presence state."""
        if not self.chat_window or not self.network:
            return

        status = self.network.check_friend_status(self.chat_window.target_id)
        is_online = status.get("is_online", False)
        is_typing = status.get("is_typing", False)

        self.chat_window.update_target_status(is_online, is_typing)

    def handle_link_click(self, link_data: str):
        """Processes interaction with media elements (audio/file links)."""
        try:
            action, file_path = link_data.split(":", 1)
            print(f"System: Processing media request: {action} on {file_path}")

            encrypted_bytes = self.network.download_encrypted_file(file_path)
            decrypted_bytes = self.crypto.decrypt_data(self.session_key, encrypted_bytes)

            if action == "play":
                print("System: Initiating audio playback from memory stream...")
                self.audio.play_audio_bytes(decrypted_bytes)

            elif action == "download":
                original_name = file_path.split("_", 1)[-1] 
                save_path, _ = QFileDialog.getSaveFileName(self.chat_window, "Save Received File", original_name)

                if save_path:
                    with open(save_path, "wb") as f:
                        f.write(decrypted_bytes)
                    print(f"System: File saved successfully to: {save_path}")

        except Exception as e:
            print(f"System Error: Media processing failure: {e}")
            QMessageBox.critical(self.chat_window, "Processing Error",
                                 "Failed to download or decrypt file. Key mismatch is possible.")


# ==========================================
# Application Entry Point
# ==========================================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(lambda: print("System: Executing cleanup and shutting down..."))
    
    controller = AppController()
    sys.exit(app.exec())
