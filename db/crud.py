from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from db.models import Request, Record, Action, User, Status, Role, Decision
from db.database import session


async def update_user(s, user_id: int, requested_days_delta: float) -> User:
    u = await get_user_by_id(s, user_id)
    if requested_days_delta:
        u.pto_planned += requested_days_delta
    return u


async def create_request(
    s,
    user_id: int,
    request_text: str,
    attach_path: Optional[str],
) -> Request:
    """assuming session: s is already begun"""
    req = Request(request=request_text, requester_id=user_id)
    s.add(req)
    await s.flush()  # materialize request ID
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


async def update_request(
    s,
    request_id: int,
    action: str,
    action_by: int,
    request: Optional[str] = None,
    reason: Optional[str] = None,
    status: Optional[str] = None,
    decision: Optional[str] = None,
    requested_days: Optional[float] = 0.0,
    policy_ids: Optional[list[str]] = None,
    requester_id: Optional[int] = None,
    decider_id: Optional[int] = None,
) -> Request:
    """assuming session: s is already begun"""
    result = await s.execute(select(Request).where(Request.id == request_id))
    req = result.scalar_one()
    prev_requested_days = req.requested_days
    prev_status = req.status
    prev_decision = req.decision
    if request:
        req.request = request
    if reason:
        req.reason = reason
    if requested_days:
        req.requested_days = requested_days
    if status:
        req.status = status
    if decision:
        req.decision = decision
        req.decided_at = datetime.now(timezone.utc)
        req.decider_id = decider_id
    if policy_ids:
        req.policy_ids = policy_ids
    if requester_id:
        req.requester_id = requester_id

    delta = 0.0
    if (
        prev_status in [Status.PENDING_MANAGER, Status.PENDING_VP]
        or prev_decision == Decision.APPROVED
    ):
        delta -= prev_requested_days
    if (
        status in [Status.PENDING_MANAGER, Status.PENDING_VP]
        or decision == Decision.APPROVED
    ):
        delta += requested_days
    if delta:
        await update_user(s, req.requester_id, delta)

    await create_record(
        s,
        request_id=req.id,
        action=action,
        user_id=action_by,
        status=req.status,
        request=req.request,
        decision=req.decision,
        reason=req.reason,
        requested_days=delta,
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
    requested_days: Optional[float] = 0.0,
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
        requested_days=requested_days,
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


async def get_users(s, exclude_llm: Optional[bool] = True) -> List[User]:
    """assuming session: s is already begun"""
    if exclude_llm:
        result = await s.execute(select(User).where(User.role != Role.LLM))
    else:
        result = await s.execute(select(User))
    return result.scalars().all()


async def get_requests(
    s,
    user_id: int,
    statuses: Optional[List[str]] = None,
    exclude_role: Optional[str] = None,
) -> List[Request]:
    """assuming session: s is already begun"""
    if exclude_role:  # manager override
        stmt = (
            select(Request)
            .outerjoin(User, User.id == Request.decider_id)
            .where(
                Request.status.in_(statuses),
                ((User.role != Role.VP) | (Request.decider_id.is_(None))),
            )
            .order_by(Request.id)
        )
    elif statuses:  # for other cases
        stmt = select(Request).where(Request.status.in_(statuses)).order_by(Request.id)
    else:  # list my requests
        stmt = (
            select(Request).where(Request.requester_id == user_id).order_by(Request.id)
        )

    result = await s.execute(stmt)
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
