import os
import tempfile
import json
from app.core.session.persistence import FileSessionPersistence
import requests


def test_save_and_load():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        persistence = FileSessionPersistence(storage_path=temp_path)
        session = requests.Session()
        session.cookies.set("JSESSIONID", "test123", domain="example.com")

        persistence.save("user1", "jwc", session, ttl_seconds=60)

        loaded = persistence.load("user1", "jwc")
        assert loaded is not None
        assert loaded.cookies.get("JSESSIONID") == "test123"
    finally:
        os.unlink(temp_path)


def test_load_missing():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        persistence = FileSessionPersistence(storage_path=temp_path)
        result = persistence.load("user1", "jwc")
        assert result is None
    finally:
        os.unlink(temp_path)


def test_expiration():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        persistence = FileSessionPersistence(storage_path=temp_path)
        session = requests.Session()
        session.cookies.set("test", "value")

        # 保存一个过期的 session (expires_at = now - 1)
        data = {"user1": {"jwc": {"cookies": {"test": {"value": "value"}}, "saved_at": 0, "expires_at": 0}}}
        with open(temp_path, 'w') as f:
            json.dump(data, f)

        result = persistence.load("user1", "jwc")
        assert result is None
    finally:
        os.unlink(temp_path)
