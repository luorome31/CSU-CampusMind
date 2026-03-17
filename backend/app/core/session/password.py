import os
import json
import base64
import hashlib
import threading
from typing import Optional
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


class PasswordManager:
    """CAS 密码加密存储"""

    def __init__(self, storage_path: str = "./data/csu_passwords.json", encryption_key: str = ""):
        self._storage_path = storage_path
        # 使用 SHA256 将密钥哈希为 32 字节 (256 位)
        self._encryption_key = hashlib.sha256(
            encryption_key.encode("utf-8") if encryption_key else b"default-key-change-me"
        ).digest()
        self._lock = threading.Lock()

        # 确保目录存在
        os.makedirs(os.path.dirname(storage_path) or ".", exist_ok=True)

    def _encrypt(self, password: str) -> str:
        """AES 加密"""
        cipher = AES.new(self._encryption_key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(password.encode("utf-8"))
        return base64.b64encode(cipher.nonce + ciphertext + tag).decode("utf-8")

    def _decrypt(self, encrypted: str) -> str:
        """AES 解密"""
        data = base64.b64decode(encrypted.encode("utf-8"))
        nonce = data[:16]
        ciphertext = data[16:-16]
        tag = data[-16:]

        cipher = AES.new(self._encryption_key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode("utf-8")

    def save_password(self, user_id: str, password: str) -> None:
        with self._lock:
            data = self._load_all()
            data[user_id] = self._encrypt(password)
            self._save_all(data)

    def get_password(self, user_id: str) -> Optional[str]:
        with self._lock:
            data = self._load_all()
            if user_id not in data:
                return None
            return self._decrypt(data[user_id])

    def delete_password(self, user_id: str) -> None:
        with self._lock:
            data = self._load_all()
            if user_id in data:
                del data[user_id]
                self._save_all(data)

    def _load_all(self) -> dict:
        if not os.path.exists(self._storage_path):
            return {}
        try:
            with open(self._storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _save_all(self, data: dict) -> None:
        with open(self._storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
