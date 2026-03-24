"""
Session Tracker - Track user sessions for Personal Center

Stores session metadata in Redis for multi-device session management.
"""
import json
import uuid
import time
from dataclasses import dataclass
from typing import List, Optional

from app.core.session.redis_client import get_redis


@dataclass
class SessionInfo:
    """Session information for Personal Center"""
    session_id: str
    user_id: str
    device: str
    location: str
    created_at: float
    user_agent: str

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "device": self.device,
            "location": self.location,
            "created_at": self.created_at,
            "user_agent": self.user_agent,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SessionInfo":
        return cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            device=data.get("device", "Unknown"),
            location=data.get("location", "Unknown"),
            created_at=data.get("created_at", time.time()),
            user_agent=data.get("user_agent", ""),
        )


def parse_device_from_user_agent(user_agent: str) -> str:
    """Parse device info from User-Agent string"""
    ua = user_agent.lower()
    if "mobile" in ua or "iphone" in ua or "android" in ua:
        if "ipad" in ua:
            return "iPad"
        return "Mobile Device"
    if "chrome" in ua:
        return "Chrome Browser"
    if "firefox" in ua:
        return "Firefox Browser"
    if "safari" in ua:
        return "Safari Browser"
    if "edge" in ua:
        return "Edge Browser"
    return "Unknown Device"


def create_session(user_id: str, user_agent: str = "", ip: str = "") -> SessionInfo:
    """Create a new session for a user"""
    session_id = str(uuid.uuid4())
    device = parse_device_from_user_agent(user_agent)
    location = ip if ip else "Unknown"

    session = SessionInfo(
        session_id=session_id,
        user_id=user_id,
        device=device,
        location=location,
        created_at=time.time(),
        user_agent=user_agent,
    )

    # Store in Redis
    import asyncio
    redis = get_redis()
    key = f"user_sessions:{user_id}"
    asyncio.get_event_loop().run_until_complete(
        redis.hset(key, session_id, json.dumps(session.to_dict()))
    )
    # Set expiry to 7 days
    asyncio.get_event_loop().run_until_complete(
        redis.expire(key, 7 * 24 * 3600)
    )

    return session


async def get_user_sessions(user_id: str) -> List[SessionInfo]:
    """Get all active sessions for a user"""
    redis = get_redis()
    key = f"user_sessions:{user_id}"
    sessions_data = await redis.hgetall(key)

    sessions = []
    for session_id, data in sessions_data.items():
        session_data = json.loads(data)
        # Check if session is still valid (7 days)
        if time.time() - session_data.get("created_at", 0) < 7 * 24 * 3600:
            sessions.append(SessionInfo.from_dict(session_data))

    return sessions


async def get_session_by_id(user_id: str, session_id: str) -> Optional[SessionInfo]:
    """Get a specific session by ID"""
    redis = get_redis()
    key = f"user_sessions:{user_id}"
    data = await redis.hget(key, session_id)

    if data:
        return SessionInfo.from_dict(json.loads(data))
    return None


async def delete_session(user_id: str, session_id: str) -> bool:
    """Delete a specific session"""
    redis = get_redis()
    key = f"user_sessions:{user_id}"
    result = await redis.hdel(key, session_id)
    return result > 0


async def delete_all_sessions(user_id: str) -> int:
    """Delete all sessions for a user"""
    redis = get_redis()
    key = f"user_sessions:{user_id}"
    result = await redis.delete(key)
    return result
