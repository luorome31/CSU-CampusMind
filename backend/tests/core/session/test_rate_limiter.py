import time
from app.core.session.rate_limiter import LoginRateLimiter

def test_can_login_initially():
    limiter = LoginRateLimiter(max_attempts=5, window_seconds=60)
    assert limiter.can_login("user1") is True

def test_login_blocks_after_limit():
    limiter = LoginRateLimiter(max_attempts=3, window_seconds=60)

    for _ in range(3):
        limiter.record_login("user1")

    assert limiter.can_login("user1") is False

def test_wait_time_calculation():
    limiter = LoginRateLimiter(max_attempts=2, window_seconds=60)

    limiter.record_login("user1")
    limiter.record_login("user1")

    wait = limiter.get_wait_time("user1")
    assert 0 < wait <= 60

def test_window_cleanup():
    limiter = LoginRateLimiter(max_attempts=5, window_seconds=1)

    limiter.record_login("user1")
    time.sleep(1.1)

    assert limiter.can_login("user1") is True
