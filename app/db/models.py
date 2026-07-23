import enum
from typing import Optional

from sqlalchemy import BigInteger, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class ParticipantRole(str, enum.Enum):
    OWNER = "owner"
    GUEST = "guest"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, autoincrement=True, primary_key=True
    )
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    in_room: Mapped[Optional[int]] = mapped_column(
        ForeignKey("rooms.room_id", ondelete="SET NULL"), nullable=True
    )

    current_room: Mapped[Optional["Room"]] = relationship(
        "Room",
        foreign_keys=[in_room],
        back_populates="current_users",
        lazy="selectin",
    )
    participations: Mapped[list["RoomParticipant"]] = relationship(
        "RoomParticipant",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Room(TimestampMixin, Base):
    __tablename__ = "rooms"

    room_id: Mapped[int] = mapped_column(
        Integer, autoincrement=True, primary_key=True
    )
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content_title: Mapped[str] = mapped_column(String(512), nullable=False)
    password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    invite_code: Mapped[Optional[str]] = mapped_column(
        String(64), unique=True, index=True, nullable=True
    )

    current_users: Mapped[list["User"]] = relationship(
        "User",
        foreign_keys=[User.in_room],
        back_populates="current_room",
        lazy="selectin",
    )
    participants: Mapped[list["RoomParticipant"]] = relationship(
        "RoomParticipant",
        back_populates="room",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="room",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class RoomParticipant(TimestampMixin, Base):
    __tablename__ = "room_participants"

    id: Mapped[int] = mapped_column(
        Integer, autoincrement=True, primary_key=True
    )
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.room_id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[ParticipantRole] = mapped_column(
        Enum(ParticipantRole), default=ParticipantRole.GUEST, nullable=False
    )

    room: Mapped["Room"] = relationship(
        "Room", back_populates="participants", lazy="selectin"
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="participations", lazy="selectin"
    )


class Message(TimestampMixin, Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        Integer, autoincrement=True, primary_key=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    image: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.room_id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="messages", lazy="selectin"
    )
    room: Mapped["Room"] = relationship(
        "Room", back_populates="messages", lazy="selectin"
    )

