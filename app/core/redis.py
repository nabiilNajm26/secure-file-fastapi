import json
from typing import Optional, Any
import redis
from app.core.config import settings


class RedisClient:
    def __init__(self):
        self.client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return self.client.set(key, value, ex=expire)
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
    
    def set_refresh_token(self, user_id: int, token: str, expire: int = 604800) -> bool:
        """Store refresh token with 7 days expiry by default"""
        key = f"refresh_token:{user_id}:{token[:8]}"
        return self.set(key, token, expire)
    
    def verify_refresh_token(self, user_id: int, token: str) -> bool:
        """Verify if refresh token exists and is valid"""
        key = f"refresh_token:{user_id}:{token[:8]}"
        stored_token = self.get(key)
        return stored_token == token if stored_token else False
    
    def revoke_refresh_token(self, user_id: int, token: str) -> bool:
        """Revoke a specific refresh token"""
        key = f"refresh_token:{user_id}:{token[:8]}"
        return self.delete(key)
    
    def revoke_all_user_tokens(self, user_id: int) -> int:
        """Revoke all refresh tokens for a user"""
        pattern = f"refresh_token:{user_id}:*"
        keys = self.client.keys(pattern)
        if keys:
            return self.client.delete(*keys)
        return 0


# Global Redis client instance
redis_client = RedisClient()