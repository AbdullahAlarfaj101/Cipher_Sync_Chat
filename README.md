# 🛡️ Cipher_Sync_Chat

A highly secure, local-first chat application engineered with a focus on data privacy, in-memory cryptographic processing, and a Zero-Trace server architecture. Designed to facilitate end-to-end encrypted messaging, voice, and file transfers using a dual-database approach.

## ✨ Core Features & Security Model

* **Zero-Trace Server (Blind Relay):** The remote Supabase server acts strictly as a blind relay router. Payloads and files are automatically purged from the remote cloud immediately upon successful client delivery.
* **In-Memory Media Processing:** Voice recordings and media streams are processed entirely within RAM (using `io.BytesIO`) to prevent local disk forensic leaks before encryption occurs.
* **Local-First Architecture:** Leverages local `SQLite` persistence, allowing users to browse chat history and draft messages even without an active internet connection.
* **End-to-End Encryption (E2EE):** All data packets (text, audio, files) are encrypted using AES-256-GCM before ever leaving the local machine.
* **Asynchronous Real-Time Sync:** Utilizes non-blocking async network listeners for instantaneous message delivery without freezing the PyQt6 GUI.

## 🛠️ Tech Stack & Architecture

* **Language:** Python 3.x
* **GUI Framework:** PyQt6 (Frameless, custom-styled terminal UI)
* **Cloud Backend:** Supabase (PostgreSQL, Realtime WebSockets)
* **Local Database:** SQLite
* **Cryptography:** `cryptography` library (AES-GCM, ECDH foundations)
* **Audio Processing:** `PyAudio` (Direct-to-RAM streaming)

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/AbdullahAlarfaj101/Cipher_Sync_Chat.git](https://github.com/AbdullahAlarfaj101/Cipher_Sync_Chat.git)
   cd Cipher_Sync_Chat
Install the required dependencies:

Bash
pip install -r requirements.txt
(Note for Windows users: You may need to install standard C++ build tools if PyAudio fails to compile).

Environment Variables:
Create a .env file in the root directory and securely add your Supabase credentials:

Code snippet
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
Database Initialization:
The local SQLite database (assets/chat_history.db) will automatically scaffold itself on the first run.
For Supabase, ensure you have two tables: mailbox (id, sender_id, receiver_id, payload) and presence (user_id, is_online, is_typing). Create a storage bucket named secure_files.

Run the Application:

Bash
python main.py
🧠 Future Roadmap
While the current build utilizes a symmetric master-key approach (simulating a physical USB decryption token), the CryptoManager class is pre-configured with ECDH (Elliptic-curve Diffie–Hellman) and HKDF methods to support future implementations of dynamic, over-the-network ephemeral key exchanges.

📄 License
Distributed under the MIT License. See LICENSE for more information.
