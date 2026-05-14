from datetime import datetime
from typing import Optional, List
from sqlalchemy import Integer, String, ForeignKey, DateTime, func, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Role:
    EMPLOYEE = "employee"
    MANAGER = "manager"
    VP = "vp"
    AUDITOR = "auditor"
    HR = "hr"
    LLM = "llm"


class Status:
    CREATED = "created"
    PROCESSING = "processing"
    PENDING_MANAGER = "pending_manager"
    PENDING_VP = "pending_vp"
    DECIDED = "decided"


class Decision:
    UNDECIDED = "undecided"
    APPROVED = "approved"
    DENIED = "denied"


class Action:
    CREATED = "created"
    APPROVED = "approved"
    DENIED = "denied"
    DEFERRED_TO_MANAGER = "deferred_to_manager"
    DEFERRED_TO_VP = "deferred_to_vp"
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
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    pto_assigned: Mapped[float] = mapped_column(default=0.0)
    pto_consumed: Mapped[float] = mapped_column(default=0.0)
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
    reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=Status.CREATED)
    decision: Mapped[Optional[str]] = mapped_column(
        String(20), default=Decision.UNDECIDED
    )
    # poilcy_ids can be [] -> nullable=False
    policy_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    decided_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    required_approval_role: Mapped[Optional[str]] = mapped_column(
        String, default=Role.MANAGER
    )
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
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    action_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    request: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    decision: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    attach_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("requests.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
