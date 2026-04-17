import asyncio, json
from knowledge_hub.aitp_mcp_server import mcp

async def main():
    tools = await mcp.list_tools()
    for t in tools:
        s = json.dumps(t.inputSchema)
        if 'boolean' in s:
            print('BOOLEAN:', t.name)
            print(json.dumps(t.inputSchema, indent=2))
        if '"title"' in s:
            print('TITLE:', t.name)
            print(json.dumps(t.inputSchema, indent=2))

asyncio.run(main())
