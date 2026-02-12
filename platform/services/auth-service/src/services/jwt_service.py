"""JWT service for auth service."""

import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

from shared.logging import get_logger
from .config import settings

logger = get_logger("jwt-service")


class JWTService:
    """JWT service."""
    
    def __init__(self):
        self.private_key = settings.jwt.private_key
        self.public_key = settings.jwt.public_key
        self.algorithm = settings.jwt.algorithm
    
    def encode_access_token(self, data: Dict[str, Any]) -> str:
        """Encode access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.private_key, algorithm=self.algorithm)
    
    def encode_refresh_token(self, data: Dict[str, Any]) -> str:
        """Encode refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.jwt.refresh_token_expire_days)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.private_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode token."""
        try:
            payload = jwt.decode(token, self.public_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("Token expired")
            raise Exception("Token expired")
        except jwt.InvalidTokenError:
            logger.error("Invalid token")
            raise Exception("Invalid token")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify token and return payload."""
        try:
            payload = jwt.decode(token, self.public_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.error("Token expired")
            raise Exception("Token expired")
        except jwt.InvalidTokenError:
            logger.error("Invalid token")
            raise Exception("Invalid token")