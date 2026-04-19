import json
with open('tool_schemas.json', encoding='utf-8') as f:
    data = json.load(f)

for t in data:
    s = json.dumps(t['inputSchema'])
    if '"title"' in s:
        print('TITLE:', t['name'])
        print(json.dumps(t['inputSchema'], indent=2))
