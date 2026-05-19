from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from db.models import Request, Record, Action, User, Status, Role
from db.database import session


async def create_request(
    s, user_id: int, request_text: str, attach_path: Optional[str]
) -> Request:
    """assuming session: s is already begun"""
    req = Request(request=request_text, requester_id=user_id)
    s.add(req)
    await s.flush()
    await create_record(
        s,
        request_id=req.id,
        action=Action.CREATED,
        request=request_text,
        status=Status.CREATED,
        attach_path=attach_path,
        user_id=user_id,
    )
    return req


async def update_request_status(
    s,
    request_id: int,
    status: str,
    action: str,
    action_by: int,
    policy_ids: list[str],
    reason: Optional[str] = None,
    decision: Optional[str] = None,
    decider_id: Optional[int] = None,
) -> Request:
    """assuming session: s is already begun"""
    result = await s.execute(select(Request).where(Request.id == request_id))
    req = result.scalar_one()
    if reason:
        req.reason = reason
    req.status = status
    if decision:
        req.decision = decision
        req.decided_at = datetime.now(timezone.utc)
        req.decider_id = decider_id
    if policy_ids:
        req.policy_ids = policy_ids
    s.add(req)
    await create_record(
        s,
        request_id=req.id,
        action=action,
        reason=req.reason,
        decision=req.decision,
        status=status,
        user_id=action_by,
    )
    return req


async def create_record(
    session,
    request_id: int,
    action: str,
    user_id: int,
    status: str,
    request: Optional[str] = None,
    decision: Optional[str] = None,
    reason: Optional[str] = None,
    attach_path: Optional[str] = None,
) -> Record:
    """assuming session is already begun. record is not synced yet"""
    rec = Record(
        action=action,
        request=request,
        request_id=request_id,
        decision=decision,
        reason=reason,
        status=status,
        attach_path=attach_path,
        user_id=user_id,
    )
    session.add(rec)
    return rec


async def get_user(s, username: str) -> User:
    """assuming session: s is already begun"""
    result = await s.execute(select(User).where(User.name == username))
    usr = result.scalar_one()
    return usr


async def get_user_by_id(s, user_id: int) -> User:
    result = await s.execute(select(User).where(User.id == user_id))
    return result.scalar_one()


async def get_users(s) -> List[User]:
    """assuming session: s is already begun"""
    result = await s.execute(select(User).where(User.role != Role.LLM))
    return result.scalars().all()


async def get_requests(s, user_id: int) -> List[Request]:
    """assuming session: s is already begun"""
    result = await s.execute(
        select(Request).where(Request.requester_id == user_id).order_by(Request.id)
    )
    return result.scalars().all()


async def get_request(s, request_id: int) -> Request:
    """assuming session: s is already begun"""
    result = await s.execute(select(Request).where(Request.id == request_id))
    return result.scalar_one()


async def get_records(s, request_id: int) -> List[Record]:
    """assuming session: s is already begun"""
    result = await s.execute(
        select(Record).where(Record.request_id == request_id).order_by(Record.action_at)
    )
    return result.scalars().all()
