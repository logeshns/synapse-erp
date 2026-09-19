from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.exceptions import AuthenticationException
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def authenticate(self, email: str, password: str) -> tuple[str, User]:
        user = self.repo.get_by_email(email)
        if not user or not user.is_active or not verify_password(password, user.password_hash):
            # Same error for "no such user" and "wrong password" on purpose —
            # distinguishing them would let an attacker enumerate valid emails.
            raise AuthenticationException("Invalid email or password.")

        token = create_access_token(subject=str(user.id), role=user.role)
        return token, user