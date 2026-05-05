import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization


class CryptoManager:
    def __init__(self):
        # Recommended nonce size for AES-GCM is 12 bytes
        self.NONCE_SIZE = 12

    # ==========================================
    # 1. Core Encryption & Decryption (AES-256-GCM)
    # ==========================================

    def encrypt_data(self, key: bytes, plaintext: bytes) -> bytes:
        """Encrypts plaintext and prepends the nonce to the ciphertext."""
        aesgcm = AESGCM(key)
        nonce = os.urandom(self.NONCE_SIZE)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        
        # Return the concatenated payload (nonce + ciphertext)
        return nonce + ciphertext

    def decrypt_data(self, key: bytes, payload: bytes) -> bytes:
        """Extracts the nonce and decrypts the ciphertext."""
        if len(payload) <= self.NONCE_SIZE:
            raise ValueError("Payload is corrupted or incomplete.")

        nonce = payload[:self.NONCE_SIZE]
        ciphertext = payload[self.NONCE_SIZE:]
        aesgcm = AESGCM(key)

        try:
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext
        except Exception as e:
            raise ValueError("Decryption failed: Invalid key or tampered payload.") from e

    # ==========================================
    # 2. Ephemeral Key Exchange (ECDH)
    # ==========================================

    def generate_ephemeral_keypair(self):
        """Generates ephemeral private and public keys for the current session."""
        private_key = ec.generate_private_key(ec.SECP384R1())
        public_key = private_key.public_key()

        # Serialize the public key to bytes for network transmission
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return private_key, public_key_bytes

    def derive_session_key(self, my_private_key, peer_public_key_bytes: bytes) -> bytes:
        """Derives the final session key using the local private key and peer's public key."""
        # Deserialize the peer's public key
        peer_public_key = serialization.load_pem_public_key(peer_public_key_bytes)

        # Perform ECDH key agreement to generate the shared secret
        shared_secret = my_private_key.exchange(ec.ECDH(), peer_public_key)

        # Apply HKDF to derive a strong 256-bit (32-byte) session key
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'handshake data',
        ).derive(shared_secret)

        return derived_key

    # ==========================================
    # 3. Memory Management & Security Hardening
    # ==========================================

    def generate_usb_master_key(self) -> bytes:
        """Generates a master key for USB storage (used once during initial setup)."""
        return AESGCM.generate_key(bit_length=256)

    @staticmethod
    def secure_wipe_memory(byte_array: bytearray):
        """Zeroes out byte arrays in memory to prevent key leakage before garbage collection."""
        if byte_array:
            for i in range(len(byte_array)):
                byte_array[i] = 0
