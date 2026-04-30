"""Progressive-disclosure tool catalog for agent guidance.
"""

from __future__ import annotations

from typing import Any



# ---------------------------------------------------------------------------
# Progressive-disclosure tool catalog
# ---------------------------------------------------------------------------
# Integration patterns (A/B/C) control how the agent interacts with each tool:
#
#   A = Catalog-only     — list in menu, agent loads on demand via ToolSearch
#   B = Skill reference  — catalog + explicit invoke instruction in AITP skill
#   C = Workflow absorbed — already embedded in AITP skill, catalog is FYI only
#
# Each entry: (tool_name, one_line_desc, integration_pattern)
#
# Pattern A: Tool is optional reference. Missing it doesn't break results.
# Pattern B: Tool should be invoked at specific subplane checkpoints.
#            The AITP skill file references it with an invoke instruction.
# Pattern C: Tool's workflow is already part of the AITP skill's mandatory
#            steps. Catalog entry is informational only.

TOOL_CATALOG: dict[tuple[str, str], list[tuple[str, str, str]]] = {
    # L0 — source discovery and registration
    ("L0", "discover"): [
        ("arxiv-latex-mcp", "Read paper sections and abstracts from arXiv", "A"),
        ("paper-search-mcp", "Multi-source paper search (arXiv, PubMed, Semantic Scholar, etc.)", "B"),
        ("knowledge-hub", "Query existing knowledge base for related sources", "C"),
    ],
    # L1 — reading and framing
    ("L1", "read"): [
        ("arxiv-latex-mcp", "Read paper sections and abstracts from arXiv", "A"),
        ("paper-search-mcp", "Multi-source paper search (arXiv, PubMed, Semantic Scholar, etc.)", "A"),
        ("knowledge-hub", "Query existing knowledge base for related sources", "C"),
    ],
    ("L1", "frame"): [
        ("arxiv-latex-mcp", "Read paper sections and abstracts from arXiv", "A"),
        ("paper-search-mcp", "Search for related papers across multiple databases", "A"),
        ("knowledge-hub", "Query existing knowledge base for related sources", "C"),
    ],
    # L3 — derivation subplanes
    ("L3", "ideation"): [
        ("scientific-brainstorming", "Physics brainstorming and idea exploration", "B"),
        ("arxiv-latex-mcp", "Check related papers and formulas", "A"),
        ("paper-search-mcp", "Search for related work to avoid duplication", "A"),
        ("knowledge-hub", "Query validated knowledge from L2", "A"),
        ("jupyter-mcp-server", "Quick feasibility estimates during ideation", "A"),
    ],
    ("L3", "planning"): [
        ("arxiv-latex-mcp", "Check related papers and formulas", "A"),
        ("knowledge-hub", "Query validated knowledge from L2", "A"),
        ("ssh-mcp", "Connect to Fisher server for compute-heavy tasks", "A"),
        ("jupyter-mcp-server", "Run numerical experiments (toy_numeric/code_method lanes)", "C"),
    ],
    ("L3", "analysis"): [
        ("arxiv-latex-mcp", "Reference papers during computation", "A"),
        ("knowledge-hub", "Query validated knowledge from L2", "A"),
        ("jupyter-mcp-server", "Run numerical experiments and analysis", "C"),
        ("ssh-mcp", "Connect to Fisher server for remote computation", "A"),
        ("mcp-server-chart", "Generate scientific charts and visualizations", "A"),
    ],
    ("L3", "result_integration"): [
        ("arxiv-latex-mcp", "Cross-check findings against papers", "A"),
        ("knowledge-hub", "Compare against validated L2 knowledge", "A"),
        ("mcp-server-chart", "Generate comparison charts", "A"),
    ],
    ("L3", "distillation"): [
        ("arxiv-latex-mcp", "Verify distilled claims against literature", "A"),
        ("knowledge-hub", "Check if claim duplicates existing L2 knowledge", "A"),
    ],
    # L4 — validation
    ("L4", "validate"): [
        ("jupyter-mcp-server", "Run independent validation scripts", "C"),
        ("ssh-mcp", "Run validation on Fisher server", "A"),
        ("arxiv-latex-mcp", "Check claims against published results", "A"),
        ("knowledge-hub", "Compare against validated L2 knowledge", "A"),
        ("mcp-server-chart", "Generate validation comparison charts", "A"),
    ],
    # L2 — promotion
    ("L2", "promote"): [
        ("knowledge-hub", "Store validated knowledge to L2", "C"),
    ],
}

# Pattern B tools that should be explicitly invoked at specific subplanes.
# Key: tool_name, Value: list of (stage, subplane, invoke_instruction)
PATTERN_B_INSTRUCTIONS: dict[str, list[tuple[str, str, str]]] = {
    "paper-search-mcp": [
        ("L0", "discover",
         "Invoke 'paper-search-mcp' to systematically search for relevant sources "
         "during the discovery phase."),
    ],
    "scientific-brainstorming": [
        ("L3", "ideation",
         "Invoke skill 'scientific-brainstorming' BEFORE discussion round 1 "
         "to structure the idea exploration workflow."),
    ],
}


def get_tool_catalog(stage: str, posture_or_subplane: str) -> list[tuple[str, str, str]]:
    """Return the tool catalog for the given stage and posture/subplane."""
    return TOOL_CATALOG.get((stage, posture_or_subplane), [])


def get_pattern_b_instructions(stage: str, subplane: str) -> list[tuple[str, str]]:
    """Return Pattern B invoke instructions for the current stage/subplane."""
    result = []
    for tool_name, entries in PATTERN_B_INSTRUCTIONS.items():
        for s, sp, instruction in entries:
            if s == stage and sp == subplane:
                result.append((tool_name, instruction))
    return result

