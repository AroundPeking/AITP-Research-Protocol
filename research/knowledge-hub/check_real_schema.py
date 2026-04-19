import json
from knowledge_hub.aitp_mcp_server import mcp

for name, tool in mcp._tool_manager._tools.items():
    s = json.dumps(tool.parameters, ensure_ascii=False)
    if '"type": "boolean"' in s or '"type":"boolean"' in s:
        print('REAL BOOLEAN:', name)
    if '"type": "integer"' in s or '"type":"integer"' in s:
        print('REAL INTEGER:', name)
    if 'additionalProperties' in s:
        print('REAL ADDITIONALPROPS:', name)
    if 'anyOf' in s:
        print('REAL ANYOF:', name)
    if 'oneOf' in s:
        print('REAL ONEOF:', name)
    if 'allOf' in s:
        print('REAL ALLOF:', name)

print('check complete')
