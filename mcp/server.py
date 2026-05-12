from pathlib import Path
from mcp.server.fastmcp import FastMCP

POLICY_DIR = Path(__file__).parent.parent / "policy"

mcp = FastMCP("agnt3", json_response=True, port=8000)


@mcp.tool()
def read_policy(filename: str) -> str:
    return (POLICY_DIR / filename).read_text()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
