from typing import Optional
from sqlalchemy import select
from db.models import Request, Record, Action, User
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
        reason=None,
        attach_path=attach_path,
        user_id=user_id,
    )
    return req


async def create_record(
    session,
    request_id: int,
    action: str,
    request: Optional[str],
    reason: Optional[str],
    attach_path: Optional[str],
    user_id: int,
) -> Record:
    """assuming session is already begun. record is not synced yet"""
    rec = Record(
        action=action,
        request=request,
        request_id=request_id,
        reason=reason,
        attach_path=attach_path,
        user_id=user_id,
    )
    session.add(rec)
    return rec


async def get_user_id(s, username: str) -> int:
    """assuming session: s is already begun"""
    result = await s.execute(select(User).where(User.name == username))
    usr = result.scalar_one()
    return usr.id
