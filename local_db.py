import sqlite3
import os


class LocalDatabase:
    def __init__(self, db_path="assets/chat_history.db"):
        """Initializes the database connection and creates necessary tables if they do not exist."""
        self.db_path = db_path
        
        # Ensure the target directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Creates the schema for the messages and contacts tables."""
        # Messages table: Content is stored as BLOB to accommodate encrypted byte payloads
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id TEXT,
                receiver_id TEXT,
                encrypted_content BLOB,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                message_type TEXT -- (text, audio, file)
            )
        ''')

        # Contacts table: Optional storage for user aliases and public keys
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                user_id TEXT PRIMARY KEY,
                display_name TEXT,
                public_key_pem BLOB
            )
        ''')
        self.conn.commit()

    # ==========================================
    # 1. Message Management
    # ==========================================

    def save_message(self, sender_id: str, receiver_id: str, encrypted_data: bytes, m_type="text"):
        """Persists an encrypted message payload to the local archive."""
        self.cursor.execute('''
            INSERT INTO messages (sender_id, receiver_id, encrypted_content, message_type)
            VALUES (?, ?, ?, ?)
        ''', (sender_id, receiver_id, encrypted_data, m_type))
        self.conn.commit()

    def get_chat_history(self, friend_id: str, limit=50):
        """Retrieves the most recent encrypted message history for a specific conversation."""
        self.cursor.execute('''
            SELECT sender_id, encrypted_content, timestamp, message_type 
            FROM messages 
            WHERE (sender_id = ? OR receiver_id = ?)
            ORDER BY timestamp DESC LIMIT ?
        ''', (friend_id, friend_id, limit))
        
        # Return results sorted chronologically (oldest to newest) for UI rendering
        return self.cursor.fetchall()[::-1]

    # ==========================================
    # 2. Contact Management
    # ==========================================

    def add_contact(self, user_id: str, name: str):
        """Adds or updates a contact in the local registry."""
        self.cursor.execute('INSERT OR REPLACE INTO contacts (user_id, display_name) VALUES (?, ?)', (user_id, name))
        self.conn.commit()

    def close(self):
        """Safely closes the database connection."""
        self.conn.close()
