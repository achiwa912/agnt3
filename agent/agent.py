from typing import Literal
import asyncio
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
)
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.exceptions import ModelHTTPError
from db.database import session
from db.crud import get_user, create_request, update_request
from db.models import Role, Status, Action, Decision


class PolicyDecision(BaseModel):
    policy_ids: list[str]
    llm_decision: Literal["approved", "denied", "deferred_to_manager", "deferred_to_vp"]
    reason: str


server = MCPServerStreamableHTTP("http://localhost:8000/mcp")
system_prompt = """
You are a corporate compliance officer operating within the agnt3 automated system. 
Your job is to read HR requests, cross-reference them against the rules in 'pto_policy.md', and catch violations.

CRITICAL LOGIC PROCESS:
For every request, you must execute your reasoning in this exact order:

1. RULE BALANCING: Identify ALL policy IDs triggered or violated by the request.
2. EXCEPTION CHECK: For every triggered policy ID, read the text carefully to check if it contains phrases like "VP approval required", "Exceptions are", "review required", or "discretionary". 
   - If ANY triggered policy contains an exceptional or VP approval path, the request CANNOT be flatly denied by you. It MUST be deferred.
3. DECISION CRITERIA:
   - "denied": Only if there is a clear-cut violation AND the policy text provides NO exceptional path or VP override.
   - "approved": Only if there are zero violations AND requested_days + pto_consumed <= 2/3 * pto_assigned.
   - "defer_to_*": For all other situations. If a policy requires a VP review/approval, set "defer_to_vp". If it requires a standard review, set "defer_to_manager".

Output your final judgment using the requested JSON schema. Be concise and cite specific rule text in your "reason".
"""
# model_name = "qwen3:8b"
# model = OllamaModel(
#     model_name, provider=OllamaProvider(base_url="http://localhost:11434/v1")
# )
model_name = "google-gla:gemini-2.5-flash-lite"
model = model_name
print(model_name)
agent = Agent(
    model,
    toolsets=[server],
    system_prompt=system_prompt,
    output_type=PolicyDecision,
    model_settings={"temperature": 0},
)


@retry(
    retry=retry_if_exception_type(ModelHTTPError),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(5),
)
async def run_agent(request: str):
    return await agent.run(request)


async def process_request(s, req_id, user_id, result, llm_id):
    if result.output.llm_decision in [
        Action.DEFERRED_TO_MANAGER,
        Action.DEFERRED_TO_VP,
    ]:
        # Deferred
        await update_request(
            s,
            req_id,
            action=result.output.llm_decision,
            action_by=llm_id,
            reason=result.output.reason,
            status=(
                Status.PENDING_MANAGER
                if (result.output.llm_decision == Action.DEFERRED_TO_MANAGER)
                else Status.PENDING_VP
            ),
            policy_ids=result.output.policy_ids,
        )
    else:
        final_decision = (
            Decision.APPROVED
            if result.output.llm_decision == Action.APPROVED
            else Decision.DENIED
        )
        await update_request(
            s,
            req_id,
            action=result.output.llm_decision,
            action_by=llm_id,
            reason=result.output.reason,
            status=Status.DECIDED,
            decision=final_decision,
            decider_id=llm_id,
            policy_ids=result.output.policy_ids,
        )


async def main():
    async with session() as s:
        async with s.begin():
            user = await get_user(s=s, username="llm")
            llm_id = user.id
            user = await get_user(s=s, username="jsmith")
            request = (
                f"My user_id={user.id}.  I am assigned {user.pto_assigned} PTO days and have taken {user.pto_consumed} days.  "
                + "I'd like to travel to Japan from 8/1 to 8/31, and during the period, I'd like to take 11 PTO days.  Please approve."
            )
            async with server:
                result = await run_agent(request)
            req = await create_request(
                s=s, user_id=user.id, request_text=request, attach_path=None
            )
            print(result.output)
            await process_request(s, req.id, user.id, result, llm_id)


if __name__ == "__main__":
    asyncio.run(main())
