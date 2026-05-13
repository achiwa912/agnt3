import asyncio
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
)
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.exceptions import ModelHTTPError
from db.database import session
from db.crud import get_user_id, create_request

server = MCPServerStreamableHTTP("http://localhost:8000/mcp")
system_prompt = """You are a compliance officer.  When given an HR request, read the relevant policy using your tools (read 'pto_policy.md') and determine if the request complies or violates policy.  Be concise and cite the specific policy rule."""
# model_name = "qwen3:8b"
# model = OllamaModel(
#     model_name, provider=OllamaProvider(base_url="http://localhost:11434/v1")
# )
model_name = "google-gla:gemini-2.5-flash-lite"
model = model_name
print(model_name)
agent = Agent(model, toolsets=[server], system_prompt=system_prompt)


@retry(
    retry=retry_if_exception_type(ModelHTTPError),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    stop=stop_after_attempt(5),
)
async def run_agent(request: str):
    return await agent.run(request)


async def main():
    async with session() as s:
        async with s.begin():
            user_id = await get_user_id(s=s, username="jsmith")
            request = f"My user_id={user_id}.  I'd like to travel to Japan from 8/1 to 8/31, and during the period, I'd like to take 11 PTO days.  Pleae approve."
            async with server:
                result = await run_agent(request)
            print(result.output)
            await create_request(
                s=s, user_id=user_id, request_text=request, attach_path=None
            )


if __name__ == "__main__":
    asyncio.run(main())
