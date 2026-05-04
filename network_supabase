import os
import time
import asyncio
from supabase import create_client, Client
from supabase import create_async_client, AsyncClient


class SupabaseManager:
    def __init__(self, supabase_url: str, supabase_key: str, my_user_id: str):
        self.url = supabase_url
        self.key = supabase_key
        self.my_user_id = str(my_user_id)

        # 1. Synchronous Client - Used for standard REST operations (insert, update, upload)
        self.supabase: Client = create_client(self.url, self.key)

        # 2. Asynchronous Client - Dedicated exclusively to Realtime Subscriptions
        self.async_client: AsyncClient = None
        self.is_listening = False

    async def init_async_client(self):
        """Initializes the asynchronous client when realtime functionality is required."""
        if not self.async_client:
            self.async_client = await create_async_client(self.url, self.key)

    # ==========================================
    # 1. Presence System (Online / Typing Status)
    # ==========================================

    def set_online_status(self, is_online: bool):
        """Updates the user's connection status in the presence table."""
        data = {
            "user_id": self.my_user_id,
            "is_online": is_online,
            "last_seen": "now()"
        }
        self.supabase.table("presence").upsert(data).execute()

    def set_typing_status(self, is_typing: bool):
        """Broadcasts the user's typing activity state to the server."""
        self.supabase.table("presence").update({"is_typing": is_typing}).eq("user_id", self.my_user_id).execute()

    def check_friend_status(self, friend_id: str) -> dict:
        """Polls the server for a specific contact's presence status."""
        response = self.supabase.table("presence").select("*").eq("user_id", str(friend_id)).execute()
        if response.data:
            return response.data[0]
        return {"is_online": False, "is_typing": False}

    # ==========================================
    # 2. Messaging Routing & Relay System
    # ==========================================

    def send_encrypted_payload(self, receiver_id: str, encrypted_payload: bytes):
        """Dispatches an encrypted payload to the remote relay database."""
        payload_hex = encrypted_payload.hex()
        data = {
            "sender_id": self.my_user_id,
            "receiver_id": str(receiver_id),
            "payload": payload_hex
        }
        self.supabase.table("mailbox").insert(data).execute()

    def delete_message_from_server(self, message_id: int):
        """Purges a message from the relay server, adhering to the blind-transport paradigm."""
        self.supabase.table("mailbox").delete().eq("id", message_id).execute()

    # --- Realtime Event Listener (Async) ---
    async def start_listening(self, on_message_received_callback):
        """Initializes and maintains a persistent WebSocket connection for real-time payloads."""
        await self.init_async_client()
        self.is_listening = True
        print(f"System: Realtime relay listener established for node [{self.my_user_id}].")

        def process_new_message(event_payload):
            """Callback handler triggered on database INSERT events."""
            # 1. Parse the nested Supabase event payload
            data_block = event_payload.get('data', {})
            new_record = data_block.get('record', {})

            # 2. Extract payload metadata and content
            receiver = new_record.get('receiver_id')
            hex_data = new_record.get('payload')
            message_id = new_record.get('id')
            sender = new_record.get('sender_id')

            # 3. Discard empty payloads or misrouted events
            if not receiver or str(receiver) != self.my_user_id:
                return

            if hex_data:
                print(f"System: Encrypted payload intercepted from node [{sender}]. Forwarding to UI stream...")
                
                # Forward decrypted bytes to the main UI controller
                on_message_received_callback(sender, bytes.fromhex(hex_data))

                # Asynchronously purge the payload from the relay database
                asyncio.create_task(self.async_client.table("mailbox").delete().eq("id", message_id).execute())

        try:
            channel_name = f"room_{self.my_user_id}"
            channel = self.async_client.channel(channel_name)

            # Establish PostgreSQL change listener filtered strictly to the user's ID
            await channel.on_postgres_changes(
                event="INSERT",
                schema="public",
                table="mailbox",
                filter=f"receiver_id=eq.{self.my_user_id}", 
                callback=process_new_message
            ).subscribe()

            # Keep the event loop alive while listening
            while self.is_listening:
                await asyncio.sleep(1)

        except Exception as e:
            print(f"System Warning: Realtime socket connection disrupted: {e}")

    def fetch_pending_messages(self) -> list:
        """Retrieves and clears unread payloads buffered while the client was offline."""
        response = self.supabase.table("mailbox").select("*").eq("receiver_id", self.my_user_id).execute()
        messages = response.data
        
        # Enforce blind-transport: purge fetched messages from the remote relay
        if messages:
            for msg in messages:
                self.delete_message_from_server(msg['id'])
        return messages

    # ==========================================
    # 3. Encrypted Media & File Storage Operations
    # ==========================================

    def upload_encrypted_file(self, file_bytes: bytes, filename: str) -> str:
        """Uploads an encrypted file stream to remote storage and returns its secure path key."""
        # Append timestamp to prevent namespace collisions
        safe_filename = f"{int(time.time())}_{filename}"

        self.supabase.storage.from_("secure_files").upload(
            path=safe_filename,
            file=file_bytes,
            file_options={"content-type": "application/octet-stream"}
        )
        return safe_filename

    def download_encrypted_file(self, filepath: str) -> bytes:
        """Downloads an encrypted file from storage and immediately purges the remote copy."""
        response = self.supabase.storage.from_("secure_files").download(filepath)
        
        # Enforce blind-transport on files
        self.supabase.storage.from_("secure_files").remove([filepath])
        return response
