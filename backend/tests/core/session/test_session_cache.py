from app.core.session.cache import SubsystemSessionCache
import requests
import time


def test_cache_get_miss():
    cache = SubsystemSessionCache(ttl_seconds=60)
    result = cache.get("user1", "jwc")
    assert result is None


def test_cache_set_and_get():
    cache = SubsystemSessionCache(ttl_seconds=60)
    session = requests.Session()
    cache.set("user1", "jwc", session)

    cached = cache.get("user1", "jwc")
    assert cached is not None
    assert cached.session is session


def test_cache_key_separation():
    cache = SubsystemSessionCache(ttl_seconds=60)
    session1 = requests.Session()
    session2 = requests.Session()
    cache.set("user1", "jwc", session1)
    cache.set("user2", "jwc", session2)

    assert cache.get("user1", "jwc").session is session1
    assert cache.get("user2", "jwc").session is session2


def test_cache_expiration():
    cache = SubsystemSessionCache(ttl_seconds=1)
    session = requests.Session()
    cache.set("user1", "jwc", session)

    time.sleep(1.1)
    result = cache.get("user1", "jwc")
    assert result is None


def test_invalidate():
    cache = SubsystemSessionCache(ttl_seconds=60)
    session = requests.Session()
    cache.set("user1", "jwc", session)

    cache.invalidate("user1", "jwc")
    assert cache.get("user1", "jwc") is None
