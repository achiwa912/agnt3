import asyncio
from db.models import Role, Status, Decision, Action
from db.models import User, Request, Record
from db.database import session

initial_users = [
    User(
        name="llm",
        fullname="LLM",
        role=Role.LLM,
        pto_assigned=20.0,
        pto_consumed=0.0,
    ),
    User(
        name="jsmith",
        fullname="John Smith",
        role=Role.EMPLOYEE,
        pto_assigned=20.0,
        pto_consumed=6.0,
    ),
    User(
        name="flake",
        fullname="Fred Lake",
        role=Role.MANAGER,
        pto_assigned=20.0,
        pto_consumed=18.0,
    ),
]


async def main():
    async with session() as s:
        async with s.begin():
            s.add_all(initial_users)


if __name__ == "__main__":
    asyncio.run(main())
