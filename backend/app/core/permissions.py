import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.exceptions import AuthenticationException, AuthorizationException
from app.models.user import User
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AuthenticationException("Missing authentication token.")

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.PyJWTError:
        raise AuthenticationException("Invalid or expired token.")

    user_id = payload.get("sub")
    user = UserRepository(db).get_by_id(int(user_id)) if user_id else None

    # Re-checked against the DB, not just the token, so a deactivated
    # account is rejected even if their token hasn't expired yet.
    if not user or not user.is_active:
        raise AuthenticationException("Invalid or expired token.")

    return user


def require_roles(*allowed_roles: str):
    """Usage: Depends(require_roles(UserRole.WAREHOUSE, UserRole.OWNER))"""

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise AuthorizationException(
                f"Role '{current_user.role}' is not permitted to perform this action."
            )
        return current_user

    return dependency