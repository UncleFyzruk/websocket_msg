import datetime

from sqlalchemy import Column, JSON, Integer, String, TIMESTAMP, ForeignKey, Boolean, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.database import Base


class PrivateChatORM(Base):
    __tablename__ = "private_chat"

    chat_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)

    messages: Mapped[list["MessageORM"]] = relationship(
        back_populates="chat",
    )

    chat_user: Mapped[list["User"]] = relationship(
        back_populates="user_chat",
        secondary="users_private_chat",
    )


class MessageORM(Base):
    __tablename__ = "message"

    id_message: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("private_chat.chat_id"))
    username_sender: Mapped[str] = mapped_column(ForeignKey("users.username"))

    text_message: Mapped[str | None]
    message_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)

    chat: Mapped["PrivateChatORM"] = relationship(
        back_populates="messages",
    )

    sender: Mapped["User"] = relationship(
        back_populates="messages",
    )


class UsersPrivateChatOrm(Base):
    __tablename__ = "users_private_chat"

    chat_id: Mapped[int] = mapped_column(ForeignKey("private_chat.chat_id", ondelete="CASCADE"),
                                         primary_key=True)
    user_username: Mapped[str] = mapped_column(ForeignKey("users.username",ondelete="CASCADE"),
                                               primary_key=True)

