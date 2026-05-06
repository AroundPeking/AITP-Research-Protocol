"""LaTeX escaping, Unicode sanitization, and Markdown frontmatter parsing."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# ── Markdown / YAML parsing ──────────────────────────────────────────────

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _parse_md(path: Path) -> tuple[dict[str, Any], str]:
    if not path.exists():
        return {}, ""
    text = path.read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    import yaml
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, m.group(2)


# ── LaTeX escaping ───────────────────────────────────────────────────────

def _esc(text: str) -> str:
    """Escape plain text for LaTeX and convert Unicode math chars.

    Escapes TeX special chars first, then converts Unicode math chars
    to $...$ wrappers (after escaping, so $ are not double-escaped).
    """
    if not text:
        return text
    text = _esc_tex_special(text)
    text = _sanitize_unicode(text)
    return text


def _esc_tex_special(text: str) -> str:
    """Escape TeX special characters (except $, which sanitize_unicode adds)."""
    if not text:
        return text
    result: list[str] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == '\\':
            if i + 1 < len(text) and text[i + 1].isalpha():
                result.append(ch)
            else:
                result.append(r"\textbackslash{}")
        elif ch == '&':
            result.append(r"\&")
        elif ch == '%':
            result.append(r"\%")
        elif ch == '$':
            result.append(ch)
        elif ch == '#':
            result.append(r"\#")
        elif ch == '_':
            result.append(r"\_")
        elif ch == '^':
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
        elif ch == '\n':
            result.append(ch)
        else:
            result.append(ch)
        i += 1
    return "".join(result)


# ── Unicode to LaTeX converter ───────────────────────────────────────────

_UNICODE_TO_LATEX_OUTSIDE: dict[str, str] = {}
_UNICODE_TO_LATEX_INSIDE: dict[str, str] = {}

for _k, _v in [
    # Greek lowercase
    ("α", "\\alpha"), ("β", "\\beta"), ("γ", "\\gamma"),
    ("δ", "\\delta"), ("ε", "\\varepsilon"), ("ζ", "\\zeta"),
    ("η", "\\eta"), ("θ", "\\theta"), ("ι", "\\iota"),
    ("κ", "\\kappa"), ("λ", "\\lambda"), ("μ", "\\mu"),
    ("ν", "\\nu"), ("ξ", "\\xi"), ("π", "\\pi"),
    ("ρ", "\\rho"), ("σ", "\\sigma"), ("τ", "\\tau"),
    ("υ", "\\upsilon"), ("φ", "\\phi"), ("χ", "\\chi"),
    ("ψ", "\\psi"), ("ω", "\\omega"),
    # Greek uppercase
    ("Γ", "\\Gamma"), ("Δ", "\\Delta"), ("Θ", "\\Theta"),
    ("Λ", "\\Lambda"), ("Ξ", "\\Xi"), ("Π", "\\Pi"),
    ("Σ", "\\Sigma"), ("Φ", "\\Phi"), ("Ψ", "\\Psi"),
    ("Ω", "\\Omega"),
    # Math operators and symbols
    ("∂", "\\partial"), ("∇", "\\nabla"), ("∫", "\\int"),
    ("∑", "\\sum"), ("∏", "\\prod"),
    ("∞", "\\infty"), ("≈", "\\approx"), ("≡", "\\equiv"),
    ("≠", "\\neq"), ("≤", "\\leq"), ("≥", "\\geq"),
    ("±", "\\pm"), ("×", "\\times"), ("·", "\\cdot"),
    ("→", "\\to"), ("←", "\\leftarrow"), ("↔", "\\leftrightarrow"),
    ("⇒", "\\Rightarrow"), ("⇐", "\\Leftarrow"),
    ("∈", "\\in"), ("∉", "\\notin"), ("⊂", "\\subset"),
    ("⊃", "\\supset"), ("∪", "\\cup"), ("∩", "\\cap"),
    ("∧", "\\land"), ("∨", "\\lor"), ("∀", "\\forall"),
    ("∃", "\\exists"), ("∄", "\\nexists"),
    ("⟨", "\\langle"), ("⟩", "\\rangle"),
    ("ħ", "\\hbar"), ("ℏ", "\\hbar"),
    # Subscripts
    ("₀", "_0"), ("₁", "_1"), ("₂", "_2"),
    ("₃", "_3"), ("₄", "_4"), ("₅", "_5"),
    # Superscripts
    ("⁰", "^0"), ("¹", "^1"), ("²", "^2"),
    ("³", "^3"), ("⁴", "^4"), ("⁵", "^5"),
    ("⁻", "^-"), ("⁺", "^+"),
    ("ᵀ", "^T"),
    # Special
    ("−", "-"),  # Unicode minus → ASCII minus
    ("†", "\\dagger"), ("…", "\\dots"),
    ("√", "\\sqrt{}"),
    # Combining chars (accent-like)
    ("̂", "^"),  # combining circumflex
]:
    _UNICODE_TO_LATEX_OUTSIDE[_k] = "$" + _v + "$"
    _UNICODE_TO_LATEX_INSIDE[_k] = _v


def _sanitize_unicode(text: str) -> str:
    """Replace Unicode math/special chars with LaTeX commands.

    Handles chars both inside and outside $...$ math spans.
    Unmapped non-ASCII chars (emoji, etc.) are stripped.
    """
    result: list[str] = []
    in_math = False
    for ch in text:
        if ch == '$':
            in_math = not in_math
            result.append(ch)
        elif in_math and ch in _UNICODE_TO_LATEX_INSIDE:
            result.append(_UNICODE_TO_LATEX_INSIDE[ch])
        elif not in_math and ch in _UNICODE_TO_LATEX_OUTSIDE:
            result.append(_UNICODE_TO_LATEX_OUTSIDE[ch])
        elif ord(ch) < 128:
            result.append(ch)
        elif ord(ch) in (0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D):
            result.append(ch)
        else:
            pass
    return "".join(result)
