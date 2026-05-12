import asyncio
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

server = MCPServerStreamableHTTP("http://localhost:8000/mcp")
system_prompt = """You are a compliance officer.  When given an HR request, read the relevant policy using your tools (read 'pto_policy.md') and determine if the request complies or violates policy.  Be concise and cite the specific policy rule."""
model = OllamaModel(
    "qwen3:8b", provider=OllamaProvider(base_url="http://localhost:11434/v1")
)
model = "google-gla:gemini-2.5-flash-lite"
print(model)
agent = Agent(model, toolsets=[server], system_prompt=system_prompt)


async def main():
    async with server:
        result = await agent.run(
            "I have 14 PTO days still unused this year.  How many more days and by when should I use so that I wouldn't lose PTO days?"
        )
    print(result.output)


if __name__ == "__main__":
    asyncio.run(main())
