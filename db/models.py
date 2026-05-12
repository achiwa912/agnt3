from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Integer, String, ForeignKey, DateTime, func, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Role(str, Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    DIRECTOR = "director"
    VP = "vp"
    AUDITOR = "auditor"
    HR = "hr"


class Status(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    PENDING = "pending"
    DECIDED = "decided"


class Decision(str, Enum):
    UNDECIDED = "undecided"
    APPROVED = "approved"
    DENIED = "denied"


class Action(str, Enum):
    CREATED = "created"
    LLM_APPROVED = "llm_approved"
    LLM_REJECTED = "llm_rejected"
    LLM_DEFERRED = "llm_deferred"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUDIT_FLAGGED = "audit_flagged"
    AUDIT_OK = "audit_ok"
    AUDIT_NG = "audit_ng"


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    fullname: Mapped[str] = mapped_column(String(100), nullable=True)
    role: Mapped[Role] = mapped_column(SAEnum(Role))
    requests: Mapped[list["Request"]] = relationship(
        back_populates="requested_by", foreign_keys="Request.requester_id"
    )
    decisions: Mapped[list["Request"]] = relationship(
        back_populates="decided_by", foreign_keys="Request.decider_id"
    )


class Request(Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str] = mapped_column(String)
    status: Mapped["Status"] = mapped_column(SAEnum(Status), default=Status.CREATED)
    decision: Mapped["Decision"] = mapped_column(
        SAEnum(Decision), default=Decision.UNDECIDED
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    decider_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    requested_by: Mapped["User"] = relationship(
        back_populates="requests", foreign_keys=[requester_id]
    )
    decided_by: Mapped[Optional["User"]] = relationship(
        back_populates="decisions", foreign_keys=[decider_id]
    )


class Record(Base):
    __tablename__ = "records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action: Mapped["Action"] = mapped_column(SAEnum(Action))
    action_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    request: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(String)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
