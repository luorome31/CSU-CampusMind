import pytest
import os
import tempfile
from app.core.session.password import PasswordManager


def test_save_and_retrieve():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        manager = PasswordManager(storage_path=temp_path, encryption_key="test-key-12345")
        manager.save_password("user1", "mypassword")

        password = manager.get_password("user1")
        assert password == "mypassword"
    finally:
        os.unlink(temp_path)


def test_get_missing():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        manager = PasswordManager(storage_path=temp_path, encryption_key="test-key-12345")
        password = manager.get_password("nonexistent")
        assert password is None
    finally:
        os.unlink(temp_path)


def test_delete():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = f.name

    try:
        manager = PasswordManager(storage_path=temp_path, encryption_key="test-key-12345")
        manager.save_password("user1", "mypassword")
        manager.delete_password("user1")

        password = manager.get_password("user1")
        assert password is None
    finally:
        os.unlink(temp_path)
