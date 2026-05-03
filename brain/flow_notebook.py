"""Flow notebook generator — JHEP-quality LaTeX from AITP topic artifacts.

Replaces the in-mcp_server.py _build_flow_notebook_content with proper
LaTeX rendering: equations in display environments, code in lstlisting,
tables with booktabs, clean journal-style layout.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# ── Preamble for the JHEP-style flow notebook ─────────────────────────
_NOTEBOOK_PREAMBLE = r"""\documentclass[a4paper,11pt]{article}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{hyperref}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{enumitem}
\usepackage[margin=2.5cm]{geometry}
\usepackage{fancyhdr}
\usepackage{titlesec}

% ── JHEP-inspired styling ──
\definecolor{linkblue}{RGB}{0,102,153}
\hypersetup{
  colorlinks=true, urlcolor=linkblue, citecolor=linkblue,
  linkcolor=linkblue, linktocpage=true
}
\definecolor{codegray}{RGB}{245,245,245}
\definecolor{codeframe}{RGB}{220,220,220}
\definecolor{headblue}{RGB}{20,60,120}

\lstset{
  backgroundcolor=\color{codegray},
  frame=single, rulecolor=\color{codeframe},
  basicstyle=\small\ttfamily, breaklines=true,
  numbers=left, numberstyle=\tiny\color{gray},
  numbersep=5pt, xleftmargin=12pt,
  showstringspaces=false,
}

\titleformat{\section}
  {\normalfont\Large\bfseries\color{headblue}}{}{0pt}{}
\titleformat{\subsection}
  {\normalfont\large\bfseries}{}{0pt}{}

% ── Result box (for claims and findings) ──
\newenvironment{resultbox}[1][]
  {\begin{quote}\color{headblue}\bfseries #1\par\small}
  {\end{quote}}

% ── Warning/note box ──
\newenvironment{warningbox}[1][]
  {\begin{quote}\color{orange!80!black}\bfseries #1\par\small\itshape}
  {\end{quote}}

% ── Header/footer ──
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\scshape AITP Research Notebook}
\fancyhead[R]{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}

\begin{document}

% ── Title page ──
"""

_NOTEBOOK_POSTAMBLE = r"""
\end{document}
"""

# ── Preprocessor: sanitize Unicode before conversion ──────────────────

def _preprocess_body(text: str) -> str:
    """Clean and normalize Markdown body text before LaTeX conversion.

    1. Remove box-drawing characters (table borders)
    2. Remove combining diacritical marks
    3. Wrap bare Unicode Greek/math symbols in $...$ ONLY where not already in math mode
    """
    # Step 1 & 2: remove box-drawing and combining chars
    result = []
    for ch in text:
        cp = ord(ch)
        if 0x2500 <= cp <= 0x257F:
            continue
        if 0x0300 <= cp <= 0x036F:
            continue
        result.append(ch)
    cleaned = "".join(result)

    # Step 3: wrap bare Unicode math in $ only outside existing $...$ spans
    math_chars = set(
        "αβγδεζηθικλμνξπρστυφχψω"
        "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΠΡΣΤΥΦΧΨΩ"
        "∂∇∫∏∑√∞≈≡≠≤≥±×·ħℏ→←↔⇒⇐⇔∈∉⊂⊃∪∩∧∨∀∃∄"
    )
    # Step 3: wrap math expressions in $...$
    # A math expression is: Greek chars + optional subscripts/superscripts + operators
    math_chars = set(
        "αβγδεζηθικλμνξπρστυφχψω"
        "ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΠΡΣΤΥΦΧΨΩ"
        "∂∇∫∏∑√∞≈≡≠≤≥±×·ħℏ→←↔⇒⇐⇔∈∉⊂⊃∪∩∧∨∀∃∄"
    )
    math_continuation = set("^_{}[]()+-*/=→·∣‖0123456789αβγδεζηθικλμνξπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΠΡΣΤΥΦΧΨΩ∂∇∫∏∑√∞≈≡≠≤≥±×·ħℏ")
    out = []
    in_dollar = False
    math_buf = []
    for ch in cleaned:
        if ch == '$':
            if math_buf:
                out.append("$" + "".join(math_buf) + "$")
                math_buf = []
            in_dollar = not in_dollar
            out.append(ch)
        elif in_dollar:
            out.append(ch)
        elif ch in math_chars:
            math_buf.append(ch)
        elif math_buf and ch in math_continuation and math_buf:
            math_buf.append(ch)  # continue the math block
        else:
            if math_buf:
                out.append("$" + "".join(math_buf) + "$")
                math_buf = []
            out.append(ch)
    if math_buf:
        out.append("$" + "".join(math_buf) + "$")
    return "".join(out)


# ── Markdown to LaTeX converter ───────────────────────────────────────

def _md_to_latex(text: str) -> list[str]:
    """Convert Markdown body text to LaTeX using pandoc.

    Pandoc handles code blocks, tables, inline/display math, lists,
    and all edge cases correctly — no need for manual parsing.
    """
    import subprocess
    import tempfile

    # Preprocess: remove box-drawing chars and combining accents
    cleaned = _preprocess_body(text)

    try:
        result = subprocess.run(
            ["pandoc", "--from", "markdown", "--to", "latex",
             "--no-highlight", "--wrap=none"],
            input=cleaned, capture_output=True, text=True, timeout=30,
            encoding="utf-8",
        )
        if result.returncode == 0:
            return result.stdout.split("\n")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: simple text conversion
    return [r"\begin{verbatim}", text, r"\end{verbatim}"]


def _esc(text: str) -> str:
    """Escape text for LaTeX — safe for use in tables and regular text."""
    if not text:
        return text
    # Process character by character for safe escaping
    result = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == '\\':
            # Keep backslash-commands (like \omega, \frac) — they're valid LaTeX
            if i + 1 < len(text) and text[i + 1].isalpha():
                result.append(ch)
            else:
                result.append(r"\textbackslash{}")
        elif ch == '&':
            result.append(r"\&")
        elif ch == '%':
            result.append(r"\%")
        elif ch == '$':
            result.append(r"\$")
        elif ch == '#':
            result.append(r"\#")
        elif ch == '_':
            # Don't escape _ in LaTeX command context (e.g. \omega_n, \varepsilon^{\mu\nu})
            if i > 0 and text[i - 1] == '\\':
                result.append(ch)
            elif i > 0 and text[i - 1].isalpha():
                # Check if preceded by \command (backtrack to find \)
                j = i - 1
                while j >= 0 and (text[j].isalpha() or text[j] in '{}[]'):
                    j -= 1
                if j >= 0 and text[j] == '\\':
                    result.append(ch)
                else:
                    result.append(r"\_")
            else:
                result.append(r"\_")
        elif ch == '^':
            # Similar logic: don't escape ^ in LaTeX command context
            if i > 0 and (text[i - 1] == '\\' or text[i - 1].isalpha()):
                j = i - 1
                while j >= 0 and (text[j].isalpha() or text[j] in '{}[]'):
                    j -= 1
                if j >= 0 and (text[j] == '\\' or j >= 0):
                    result.append(ch)
                else:
                    result.append(r"\^{}")
            else:
                result.append(r"\^{}")
        elif ch == '~':
            result.append(r"\textasciitilde{}")
        elif ch == '{':
            result.append(r"\{")
        elif ch == '}':
            result.append(r"\}")
        elif ch == '<':
            result.append(r"\textless{}")
        elif ch == '>':
            result.append(r"\textgreater{}")
        else:
            cp = ord(ch)
            if 0x2500 <= cp <= 0x257F:  # box-drawing chars — skip
                pass
            elif 0x0300 <= cp <= 0x036F:  # combining diacritics — skip
                pass
            elif cp == 0x2014:  # em dash
                result.append("---")
            elif cp == 0x2013:  # en dash
                result.append("--")
            elif cp in (0x2018, 0x2019):  # smart quotes
                result.append("'")
            elif cp in (0x201C, 0x201D):
                result.append('"')
            else:
                result.append(ch)
        i += 1
    return "".join(result)


# ── Section builders ──────────────────────────────────────────────────

def _build_title_page(fm_state: dict) -> list[str]:
    """JHEP-style title page."""
    slug = fm_state.get("topic_slug", "")
    title = fm_state.get("title", slug)
    lane = fm_state.get("lane", "unspecified")
    stage = fm_state.get("stage", "")
    posture = fm_state.get("posture", "")
    created = str(fm_state.get("created_at", ""))

    tex: list[str] = []
    tex.append(r"{\LARGE\flushleft\sffamily\bfseries " + _esc(title) + r"\par}")
    tex.append(r"\vskip10pt")
    tex.append(r"\hrule height 1.2pt")
    tex.append(r"\vskip8pt")
    tex.append(r"{\sffamily\small " + f"Lane: {_esc(lane)} \\quad Stage: {_esc(stage)}/{_esc(posture)} \\quad Started: {_esc(created)}" + r"\par}")
    tex.append(r"\vskip20pt")
    tex.append(r"\noindent\textsc{Abstract:} This is an auto-generated AITP research notebook. It records the complete research trajectory --- sources, derivations, claims, validation evidence --- in a single structured document.")
    tex.append(r"\vskip16pt")
    tex.append(r"\tableofcontents")
    tex.append(r"\newpage")
    return tex


def _build_source_table(sources_list: list[dict]) -> list[str]:
    """Source landscape as a proper longtable."""
    if not sources_list:
        return [r"\noindent\textit{(No sources registered.)}"]
    tex: list[str] = []
    tex.append(r"\begin{longtable}{p{3cm}p{2.5cm}p{8cm}}")
    tex.append(r"\toprule")
    tex.append(r"\textbf{Source ID} & \textbf{Type} & \textbf{Title / Description} \\")
    tex.append(r"\midrule")
    tex.append(r"\endhead")
    for s in sources_list:
        sid = _esc(s.get("source_id", ""))
        stype = _esc(s.get("source_type", ""))
        title = _esc(s.get("title", sid)[:120])
        tex.append(f"{sid} & {stype} & {title} \\\\")
    tex.append(r"\bottomrule")
    tex.append(r"\end{longtable}")
    return tex


def _build_derivation_section(subplanes: list[dict], candidates: list[dict]) -> list[str]:
    """Derivation journey — subplane artifacts and candidate claims."""
    tex: list[str] = []

    # Find derivation-related subplanes
    deriv_names = {"derive", "trace-derivation", "integrate",
                   "analysis", "step_derive", "result_integration"}
    deriv_sps = [sp for sp in subplanes if sp["name"] in deriv_names]

    if deriv_sps:
        tex.append(r"\subsection{Structured Derivation}")
        for sp in deriv_sps:
            label = sp["name"].replace("-", " ").replace("_", " ").title()
            tex.append(r"\subsubsection*{" + label + "}")
            body_text = sp.get("body", "").strip()
            if body_text:
                for line in _md_to_latex(body_text):
                    tex.append(line)

    # Candidates
    if candidates:
        tex.append(r"\subsection{Claims \& Candidates}")
        for i, c in enumerate(candidates, 1):
            ctitle = _esc(c.get("title", c.get("slug", "")))
            claim = c.get("claim", "")
            cstatus = c.get("status", "submitted")
            tex.append(r"\begin{resultbox}[" + f"Claim {i}: {ctitle}" + r"]")
            tex.append(r"\textit{Status:} " + _esc(cstatus) + r"\\")
            if claim:
                tex.append(_esc(claim[:1000]))
            tex.append(r"\end{resultbox}")
            tex.append("")
    elif not deriv_sps:
        tex.append(r"\noindent\textit{(No derivation content recorded yet.)}")

    return tex


def _build_validation_section(reviews: list[dict], numerical_results: list[dict] = None) -> list[str]:
    """Validation evidence from L4 reviews and numerical results."""
    tex: list[str] = []
    if reviews:
        for rv in reviews:
            outcome = rv.get("outcome", "unknown")
            badge = r"\textsf{[PASS]}" if outcome == "pass" else r"\textsf{[FAIL]}" if outcome == "fail" else _esc(outcome)
            tex.append(r"\begin{warningbox}[" + _esc(rv.get("slug", "")) + r" \quad " + badge + "]")
            notes = rv.get("notes", "")
            if notes:
                tex.append(_esc(notes[:800]))
            tex.append(r"\end{warningbox}")
            tex.append("")
    else:
        tex.append(r"\noindent\textit{(No L4 reviews submitted yet. Validation pending.)}")

    if numerical_results:
        tex.append(r"\subsubsection*{Numerical Results}")
        for nr in numerical_results:
            obs = _esc(nr.get("observable", ""))
            val = _esc(str(nr.get("computed_value", "")))
            unc = _esc(str(nr.get("uncertainty", "")))
            units = _esc(str(nr.get("units", "")))
            lit = _esc(str(nr.get("literature_value", "")))
            agree = _esc(str(nr.get("agreement_status", "")))
            tex.append(r"\begin{resultbox}[" + obs + "]")
            tex.append(f"Computed: {val} $\\pm$ {unc} {units}")
            if lit:
                tex.append(f"\\quad Literature: {lit} {units}")
            if agree:
                tex.append(f"\\quad Agreement: {agree}")
            tex.append(r"\end{resultbox}")
            tex.append("")
    return tex


def _build_domain_section(domain_constraints: dict) -> list[str]:
    """Domain constraints section."""
    if not domain_constraints:
        return []
    tex: list[str] = []
    rules = domain_constraints.get("hard_rules", [])
    smoke = domain_constraints.get("smoke_test", [])
    if rules:
        tex.append(r"\subsection{Domain Constraints}")
        tex.append(r"\begin{itemize}")
        for r in rules[:20]:  # top 20 to avoid bloat
            tex.append(r"\item " + _esc(r))
        tex.append(r"\end{itemize}")
    if smoke:
        tex.append(r"\subsubsection*{Smoke Test}")
        for s in smoke:
            tex.append(r"\texttt{" + _esc(s) + r"} \\")
    return tex


# ── Main builder ──────────────────────────────────────────────────────

def build_flow_notebook_content(
    topic_root: Path,
    fm_state: dict,
    subplanes: list[dict],
    ideas_list: list[Path],
    candidates: list[dict],
    reviews: list[dict],
    sources_list: list[dict],
    deferred_body: str,
    domain_constraints: dict,
    l2_nodes: list[dict],
    numerical_results: list[dict] = None,
) -> str:
    """Build the complete flow notebook LaTeX document.

    All data is pre-collected by the caller (mcp_server.py).
    This function only does formatting.
    """
    tex: list[str] = []
    tex.append(_NOTEBOOK_PREAMBLE)

    # Title page
    tex.extend(_build_title_page(fm_state))

    # §1 Research Question
    tex.append(r"\section{Research Question}")
    question = fm_state.get("bounded_question", "") or fm_state.get("question", "")
    if question:
        tex.append(_esc(question))
    else:
        tex.append(r"\textit{(No bounded question recorded.)}")
    tex.append("")

    # §2 Source Landscape
    tex.append(r"\section{Source Landscape}")
    tex.extend(_build_source_table(sources_list))
    tex.append("")

    # §3 Derivation Journey
    tex.append(r"\section{Derivation Journey}")
    tex.extend(_build_derivation_section(subplanes, candidates))
    tex.append("")

    # §4 Validation
    tex.append(r"\section{Validation}")
    tex.extend(_build_validation_section(reviews, numerical_results or []))
    tex.append("")

    # §5 L2 Knowledge
    tex.append(r"\section{Canonical Knowledge (L2)}")
    if l2_nodes:
        tex.append(r"\begin{itemize}")
        for n in l2_nodes[:30]:
            nid = _esc(n.get("node_id", n.get("slug", "")))
            ntype = _esc(n.get("node_type", ""))
            tex.append(r"\item " + f"\\textbf{{{nid}}} ({ntype})")
        tex.append(r"\end{itemize}")
    else:
        tex.append(r"\textit{(No L2 nodes promoted from this topic yet.)}")
    tex.append("")

    # §6 Domain Context
    if domain_constraints:
        tex.append(r"\section{Domain Context}")
        tex.extend(_build_domain_section(domain_constraints))
        tex.append("")

    # §7 Negative Results & Open Questions
    tex.append(r"\section{Negative Results \& Open Questions}")
    if deferred_body.strip():
        for line in _md_to_latex(deferred_body[:3000]):
            tex.append(line)
    else:
        tex.append(r"\textit{(No negative results or open questions formally recorded.)}")
    tex.append("")

    tex.append(_NOTEBOOK_POSTAMBLE)
    return "\n".join(tex)
