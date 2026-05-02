---
arxiv_id: ''
fidelity: local_source
registered: '2026-04-24T16:29:17+08:00'
source_id: current-mcp-server-codebase
title: 'Current AITP MCP Server v2: 50 tools, brain/mcp_server.py + brain/state_model.py'
type: code
---
# Current AITP MCP Server v2: 50 tools, brain/mcp_server.py + brain/state_model.py

50 @mcp.tool() functions, file-based persistence (Markdown+YAML), L0-L5 stage machine, 12 test files ~5000 lines. Key problems: gate evaluation only checks field existence not content quality, L4 self-validation risk, L2 empty, no math verification, naive substring search, trust model too linear.

