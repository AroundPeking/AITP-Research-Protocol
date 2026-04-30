"""Semantic search utilities for L2 knowledge graph.
"""

import re

# ---------------------------------------------------------------------------
# Semantic search — physics concept aliases and token-aware matching
# ---------------------------------------------------------------------------

PHYSICS_CONCEPT_ALIASES: dict[str, list[str]] = {
    # Many-body methods
    "rpa": ["random phase approximation"],
    "random phase approximation": ["rpa"],
    "crpa": ["canonical random phase approximation"],
    "canonical random phase approximation": ["crpa"],
    "scrpa": ["self-consistent random phase approximation", "sc-rpa"],
    "self-consistent random phase approximation": ["scrpa", "sc-rpa"],
    "gw": ["g0w0", "gw approximation"],
    "g0w0": ["gw"],
    "qsGW": ["quasiparticle self-consistent gw", "qs-gw"],
    "quasiparticle self-consistent gw": ["qsGW", "qs-gw"],
    "bse": ["bethe-salpeter equation"],
    "bethe-salpeter equation": ["bse"],
    # Density functional
    "dft": ["density functional theory"],
    "density functional theory": ["dft"],
    "lda": ["local density approximation"],
    "local density approximation": ["lda"],
    "gga": ["generalized gradient approximation"],
    "generalized gradient approximation": ["gga"],
    "tddft": ["time-dependent density functional theory"],
    "time-dependent density functional theory": ["tddft"],
    # Quantum field theory
    "qft": ["quantum field theory"],
    "quantum field theory": ["qft"],
    "qed": ["quantum electrodynamics"],
    "quantum electrodynamics": ["qed"],
    "qcd": ["quantum chromodynamics"],
    "quantum chromodynamics": ["qcd"],
    "eft": ["effective field theory"],
    "effective field theory": ["eft"],
    "rg": ["renormalization group"],
    "renormalization group": ["rg"],
    "frg": ["functional renormalization group"],
    "functional renormalization group": ["frg"],
    "dmrg": ["density matrix renormalization group"],
    "density matrix renormalization group": ["dmrg"],
    # Condensed matter
    "sc": ["self-consistent", "superconducting"],
    "bcs": ["bardeen-cooper-schrieffer"],
    "hubbard model": ["hubbard hamiltonian"],
    "heisenberg model": ["heisenberg hamiltonian"],
    "ising model": ["ising hamiltonian"],
    "ssh": ["su-schrieffer-heeger"],
    # Quantum information
    "vm": ["von neumann"],
    "mipt": ["measurement-induced phase transition"],
    "measurement-induced phase transition": ["mipt"],
    "lqg": ["loop quantum gravity"],
    "loop quantum gravity": ["lqg"],
    "entanglement entropy": ["von neumann entropy", "ee"],
    # Green's functions
    "gf": ["green's function", "green function"],
    "green's function": ["gf", "green function", "propagator"],
    "propagator": ["green's function", "gf"],
    "self-energy": ["self energy"],
    "dyson equation": ["dyson's equation"],
    # Geometry / topology
    "berry phase": ["geometric phase", "berry connection"],
    "chern number": ["chern invariant", "tknn invariant"],
    "chern insulator": ["quantum anomalous hall"],
    # Computational
    "vasp": ["vienna ab initio simulation package"],
    "qe": ["quantum espresso"],
    "wannier": ["wannier90", "maximally localized wannier functions"],
    "lcao": ["linear combination of atomic orbitals"],
    "paw": ["projector augmented wave"],
    # LaTeX symbol → concept aliases
    "sigma": ["self-energy", "correlation", "many-body", "dyson"],
    "chi": ["susceptibility", "response", "polarization", "linear response"],
    "g_0": ["free green", "greens function", "propagator", "non-interacting"],
    "w": ["screened coulomb", "screening", "dielectric", "polarization"],
    "epsilon": ["dielectric", "dielectric function", "screening", "permittivity"],
    "gamma": ["vertex correction", "beyond-gw", "electron-hole interaction", "vertex"],
    "v_c": ["bare coulomb", "coulomb interaction", "unscreened", "hartree"],
    "partial sigma partial e": ["quasiparticle", "z-factor", "mass renormalization", "spectral weight"],
    "delta n": ["density response", "charge fluctuation", "screening", "polarization"],
    "chi_0": ["bare susceptibility", "rpa", "non-interacting response", "lindhard"],
}

LATEX_NORM_RE = re.compile(r'\s+')


def normalize_latex(expr: str) -> str:
    """Normalize a LaTeX expression for comparison: collapse whitespace, unify braces."""
    if not expr:
        return ""
    s = expr.strip()
    s = s.replace('\\left', '').replace('\\right', '')
    s = s.replace('{', ' ').replace('}', ' ')
    s = s.replace('[', ' ').replace(']', ' ')
    s = s.replace('(', ' ').replace(')', ' ')
    s = ' '.join(s.split())
    return s.lower()


_ALIAS_LOOKUP: dict[str, list[str]] = {}
for _abbr, _expansions in PHYSICS_CONCEPT_ALIASES.items():
    _key = _abbr.lower()
    if _key not in _ALIAS_LOOKUP:
        _ALIAS_LOOKUP[_key] = []
    _ALIAS_LOOKUP[_key].extend(e.lower() for e in _expansions)


def tokenize_for_search(text: str) -> set[str]:
    """Split text into searchable tokens including concept expansions."""
    if not text:
        return set()
    tokens = set()
    # Split on common delimiters
    for part in re.split(r'[\s,;:.!?()\[\]{}]+', text.lower()):
        part = part.strip('"\'`-_=+*&^%$#@!~<>/\\|')
        if part and len(part) >= 2:
            tokens.add(part)
            # Add alias expansions
            if part in _ALIAS_LOOKUP:
                for alias in _ALIAS_LOOKUP[part]:
                    tokens.add(alias)
                    # Also add individual words from multi-word aliases
                    for alias_word in alias.split():
                        if len(alias_word) >= 2:
                            tokens.add(alias_word)
    # Also add multi-word phrase as single token
    text_lower = text.lower().strip()
    if ' ' in text_lower:
        tokens.add(text_lower)
    return tokens


def semantic_score(query: str, content_fields: list[str]) -> float:
    """Compute relevance score between query and content using token overlap.

    Returns 0.0-1.0 where 1.0 is perfect match.
    Query tokens are matched against each content field; matches in shorter
    fields (like title) are weighted higher than matches in long body text.
    """
    if not query:
        return 0.0
    query_tokens = tokenize_for_search(query)
    if not query_tokens:
        return 0.0

    best_score = 0.0
    for field_text in content_fields:
        if not field_text:
            continue
        field_tokens = tokenize_for_search(field_text)
        if not field_tokens:
            continue
        overlap = query_tokens & field_tokens
        if not overlap:
            continue
        # Jaccard-like: |intersection| / |query|
        recall = len(overlap) / len(query_tokens)
        # Precision: how much of the field matched
        precision = len(overlap) / len(field_tokens)
        # F1-like score
        if recall + precision > 0:
            score = 2 * recall * precision / (recall + precision)
        else:
            score = 0.0
        # Bonus for exact phrase match
        query_lower = query.lower().strip()
        if query_lower in field_text.lower():
            score = max(score, 0.85)
        # Bonus for normalized LaTeX match
        if '$' in query and '$' in field_text:
            q_latex = normalize_latex(query)
            f_latex = normalize_latex(field_text)
            if q_latex and f_latex and q_latex in f_latex:
                score = max(score, 0.9)
        # LaTeX command extraction bonus
        latex_commands = re.findall(r'\\([a-zA-Z]+)', query)
        if latex_commands:
            for cmd in latex_commands:
                cmd_lower = cmd.lower()
                for alias_key, alias_vals in _ALIAS_LOOKUP.items():
                    if cmd_lower == alias_key or cmd_lower in alias_key:
                        for av in alias_vals:
                            if av in field_text.lower():
                                score = max(score, min(score * 1.5, 1.0))
                                break
                # Direct substring match for LaTeX command name in field
                if cmd_lower in field_text.lower():
                    score = max(score, min(score * 1.5, 1.0))
        best_score = max(best_score, score)

    return best_score

