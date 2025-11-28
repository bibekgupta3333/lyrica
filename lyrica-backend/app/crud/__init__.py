"""
CRUD operations package.
"""

from app.crud.api_key import api_key
from app.crud.feedback import feedback
from app.crud.lyrics import lyrics
from app.crud.user import user

__all__ = ["user", "lyrics", "feedback", "api_key"]
