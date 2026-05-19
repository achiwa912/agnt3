from datetime import datetime
import asyncio
from typing import Optional, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db.models import Request
from db.crud import (
    get_requests,
    get_request,
    get_user,
    get_users,
    create_request,
    get_user_by_id as get_user_by_id_db,
    get_records,
)
from db.database import session
from agent.agent import run_agent, process_request, server

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestSchema(BaseModel):
    id: int
    request: str
    reason: Optional[str]
    status: str
    decision: Optional[str]
    policy_ids: Optional[List[str]]
    created_at: datetime
    decided_at: Optional[datetime]
    requester_id: int
    decider_id: Optional[int]
    decider: Optional[str] = None


@app.get("/users/{user_id}/requests")
async def list_requests(user_id: int) -> List[RequestSchema]:
    async with session() as s:
        async with s.begin():
            requests = await get_requests(s, user_id)

    reqs = []
    for r in requests:
        req = RequestSchema(
            id=r.id,
            request=r.request,
            reason=r.reason,
            status=r.status,
            decision=r.decision,
            policy_ids=r.policy_ids,
            created_at=r.created_at,
            decided_at=r.decided_at,
            requester_id=r.requester_id,
            decider_id=r.decider_id,
            decider="",
        )
        reqs.append(req)
    return reqs


class NewRequestBody(BaseModel):
    user_id: int
    req_text: str


@app.post("/requests", response_model=RequestSchema)
async def new_request(body: NewRequestBody):
    async with session() as s:
        async with s.begin():
            request = await create_request(
                s, body.user_id, body.req_text, attach_path=None
            )
            async with server:
                result = await run_agent(body.req_text)
            llm = await get_user(s=s, username="llm")
            await process_request(s, request.id, body.user_id, result, llm.id)
    return request


class PatchRequestBody(BaseModel):
    request: Optional[str]
    reason: Optional[str]
    status: Optional[str]
    decision: Optional[str]
    decider_id: Optional[int]


@app.get("/requests/{request_id}")
async def read_request(request_id: int) -> RequestSchema:
    async with session() as s:
        async with s.begin():
            r = await get_request(s, request_id)
            decider = ""
            if r.decider_id:
                decider = await get_user_by_id_db(s, r.decider_id)
                decider = decider.fullname
    req = RequestSchema(
        id=r.id,
        request=r.request,
        reason=r.reason,
        status=r.status,
        decision=r.decision,
        policy_ids=r.policy_ids,
        created_at=r.created_at,
        decided_at=r.decided_at,
        requester_id=r.requester_id,
        decider_id=r.decider_id,
        decider=decider,
    )
    return req


@app.patch("/requests/{request_id}", response_model=RequestSchema)
async def patch_request(request_id: int, body: PatchRequestBody):
    async with session() as s:
        async with s.begin():
            request = await get_request(s, request_id)
            if body.reason:
                request.reason = body.reason
            if body.status:
                request.status = body.status
            if body.decision:
                request.decision = body.decision
                request.decider_id = body.decider_id
            if body.request:
                request.request = body.request
                async with server:
                    result = await run_agent(body.request)
                    llm = await get_user(s=s, username="llm")
                    await process_request(
                        s, request.id, request.requester_id, result, llm.id
                    )
            return request


class UserSchema(BaseModel):
    id: int
    name: str
    fullname: Optional[str]
    role: Optional[str]
    pto_assigned: Optional[float]
    pto_consumed: Optional[float]


@app.get("/users")
async def list_users() -> List[UserSchema]:
    async with session() as s:
        async with s.begin():
            users = await get_users(s)
    usrs = []
    for u in users:
        usr = UserSchema(
            id=u.id,
            name=u.name,
            fullname=u.fullname,
            role=u.role,
            pto_assigned=u.pto_assigned,
            pto_consumed=u.pto_consumed,
        )
        usrs.append(usr)
    return usrs


@app.get("/users/{user_id}", response_model=UserSchema)
async def get_user_by_id(user_id: int) -> UserSchema:
    async with session() as s:
        async with s.begin():
            user = await get_user_by_id_db(s, user_id)
    return UserSchema(
        id=user_id,
        name=user.name,
        fullname=user.fullname,
        role=user.role,
        pto_assigned=user.pto_assigned,
        pto_consumed=user.pto_consumed,
    )


class RecordSchema(BaseModel):
    id: int
    action: str
    action_at: datetime
    request: Optional[str]
    decision: Optional[str]
    reason: Optional[str]
    status: str
    attach_path: Optional[str]
    request_id: int
    user_id: int
    user_name: str


@app.get("/requests/{request_id}/records")
async def list_records(request_id: int) -> List[RecordSchema]:
    async with session() as s:
        async with s.begin():
            records = await get_records(s, request_id)
            rcds = []
            for r in records:
                u = await get_user_by_id_db(s, r.user_id)
                rcd = RecordSchema(
                    id=r.id,
                    action=r.action,
                    action_at=r.action_at,
                    request=r.request,
                    decision=r.decision,
                    reason=r.reason,
                    status=r.status,
                    attach_path=r.attach_path,
                    request_id=r.request_id,
                    user_id=r.user_id,
                    user_name=u.fullname,
                )
                rcds.append(rcd)
    return rcds
