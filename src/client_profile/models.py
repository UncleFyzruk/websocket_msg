import enum
import uuid
import datetime

from sqlalchemy import UniqueConstraint, CheckConstraint
from sqlalchemy import UUID, Column, JSON, Integer, String, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base

default_avatar = "JoJo"


# Декларативный стиль объявления модели "Пользователи"
# Base - созданный ранее базовый класс
class User(Base):
    """
    :param __tablename__: название таблицы в бд
    :param id: уникальный идентификатор
    :param username: уникальное имя пользователя
    :param hashed_password: зашифрованный пароль
    :param email: электронная почта. Должна быть уникальна
    :param avatar: Ссылка, где хранится картинка аватара на жестком диске
    :param is_active: Активный аккаунт, нужен для FastApi-users
    :param is_superuser: обладает ли правами админа, нужен для FastApi-users
    :param is_verified: прошел верификацию, нужен для FastApi-users

    :param user_chat: Отношение с таблицей PrivateChatORM, back_populates-двунаправленное
            secondary - таблица через которую связываются. в многие ко многим
    :param messages: Отношение с таблицей MessageORM
    :param users_friends: Отношение с таблицей FriendsOrm
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(length=30),unique=True)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    email: Mapped[str | None]
    registered_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)
    avatar: Mapped[str] = mapped_column(default=default_avatar, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)

    user_chat: Mapped[list["PrivateChatORM"]] = relationship(
        back_populates="chat_user",
        secondary="users_private_chat"
    )

    messages: Mapped[list["MessageORM"]] = relationship(
        back_populates="sender"
    )

    users_friends: Mapped[list["FriendsOrm"]] = relationship(
        back_populates="friend_user",
        secondary="users_relationship"
    )


class FriendshipStatus(enum.Enum):
    friend_request = "friend_request"
    blocked = "blocked"
    friend = "friend"


class FriendsOrm(Base):
    __tablename__ = "friends"

    id_friendship: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    friendship_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)

    friend_user: Mapped[list["User"]] = relationship(
        back_populates="users_friends",
        secondary="users_relationship",
        overlaps="users_relationship"
    )

    useres_relationship: Mapped[list["UsersRelationshipOrm"]] = relationship(
        back_populates="friendship",
        cascade="all, delete-orphan",
        overlaps="friend_user,users_friends"
    )


class UsersRelationshipOrm(Base):
    __tablename__ = "users_relationship"

    friendship_id: Mapped[int] = mapped_column(ForeignKey("friends.id_friendship", ondelete="CASCADE"),
                                               primary_key=True)
    user_username: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="CASCADE"),
                                               primary_key=True)

    status_friendship: Mapped[FriendshipStatus | None]
    is_initiator: Mapped[bool | None]

    friendship: Mapped["FriendsOrm"] = relationship(
        back_populates="useres_relationship",
        overlaps="friend_user,users_friends"
    )