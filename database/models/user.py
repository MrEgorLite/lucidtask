from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base
from database.models.post import PostModel
from validators import accounts as validators
from security.passwords import hash_password, verify_password


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    _password_hash: Mapped[str] = mapped_column(nullable=False)

    posts: Mapped[list["PostModel"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    @classmethod
    def create(cls, email: str, raw_password: str) -> "UserModel":
        """
        Factory method to create a new UserModel instance.

        This method simplifies the creation of a new user by handling
        password hashing and setting required attributes.
        """
        user = cls(email=email)
        user.password = raw_password
        return user

    @property
    def password(self) -> None:
        raise AttributeError("Password is write-only. Use the setter to set the password.")

    @password.setter
    def password(self, raw_password: str) -> None:
        """
        Set the user's password after validating its strength and hashing it.
        """
        validators.validate_password_strength(raw_password)
        self._password_hash = hash_password(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        """
        Verify the provided password against the stored hashed password.
        """
        return verify_password(raw_password, self._password_hash)
