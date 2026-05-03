# 🛡️ Cipher_Sync_Chat

A robust, secure chat application focused on data privacy, secure communications, and seamless user experience. Designed to facilitate encrypted messaging with a clean interface, utilizing a dual-database architecture for local persistence and real-time cloud synchronization.

## ✨ Features
* **Dual Database Syncing:** Seamlessly synchronizes local data with the cloud.
* **Offline Support:** Local message persistence allows reading and drafting messages without an active internet connection.
* **Real-time Messaging:** Fast and responsive chat architecture powered by Supabase.
* **End-to-End Security:** Ensures that messages are securely transmitted and stored.
* **User Authentication:** Secure login and registration system.

## 🛠️ Tech Stack
* **Language:** Python
* **Cloud Backend & Database:** Supabase (PostgreSQL, Realtime, Auth)
* **Local Database:** SQLite
* **Security:** Python cryptography libraries for data encryption
* **GUI Framework:** PyQt5

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AbdullahAlarfaj101/Cipher_Sync_Chat.git
   cd Cipher_Sync_Chat
Install the required dependencies:

Bash
pip install -r requirements.txt
Environment Variables:
Create a .env file in the root directory and add your Supabase credentials:

Code snippet
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
Database Initialization:
The local SQLite database (chat_history.db) will automatically initialize on the first run. Make sure your Supabase remote tables match the required schema. (Note: You can include an SQL script in your repository for easy Supabase setup).

Run the application:

Bash
python main.py
🧠 Architecture Highlights
Local-First Architecture: By leveraging SQLite locally, the application provides immediate feedback and fast load times. Background workers then sync this data with Supabase to ensure all devices stay up-to-date.

Secure Transmission: All sensitive data streams are encrypted before being pushed to the remote database, prioritizing user privacy at the architectural level.

📄 License
Distributed under the MIT License. See LICENSE for more information.
