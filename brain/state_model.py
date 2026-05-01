"""Thin compatibility re-export for the refactored brain layer.

All functionality lives in sub-modules:
  brain.state       — StageSnapshot + stage/L2/L4 constants
  brain.physicist   — AI physicist checks (correspondence, anomalies, L2 lookup)
  brain.contracts   — artifact templates, required fields, required headings
  brain.checks      — content/frontmatter/heading validation, question checks
  brain.domains     — domain detection, skill mapping, rule extraction
  brain.gates       — stage gate evaluation (L0/L1/L3/L4)
  brain.semantic    — semantic search utilities
  brain.tool_catalog — progressive-disclosure tool catalog

Import from here for backward compatibility with mcp_server.py and hooks.
"""

from brain.state import (
    StageSnapshot,
    L3_ACTIVITIES,
    L3_ACTIVITY_ARTIFACT_NAMES,
    L3_ACTIVITY_REQUIRED_HEADINGS,
    L3_ACTIVITY_SKILL_MAP,
    L3_ACTIVITY_TEMPLATES,
    L3_ARTIFACT_TEMPLATES,
    L3_SUBPLANES,
    L3_ACTIVE_ARTIFACT_NAMES,
    STUDY_L3_SUBPLANES,
    STUDY_L3_ACTIVE_ARTIFACT_NAMES,
    STUDY_CANDIDATE_TYPES,
    L2_NODE_TYPES,
    L2_EDGE_TYPES,
    DOMAIN_TAXONOMY,
    L2_QUERY_HIDDEN_FIELDS,
    VALID_DOMAINS,
    DIAGRAM_TEMPLATE,
    JUSTIFICATION_TYPES,
    STEP_TEMPLATE,
    L2_TOWER_TEMPLATE,
    L2_CORRESPONDENCE_TEMPLATE,
    STUDY_L4_CHECKS,
    TRUST_EVOLUTION,
    L4_OUTCOMES,
    PHYSICS_CHECK_FIELDS,
    _LANE_PHYSICS_CHECK_FIELDS,
    _get_l3_config,
)

from brain.physicist import (
    _check_physicist_l2_lookup,
    _check_physicist_correspondence,
    _check_physicist_anomalies,
    PHYSICIST_CHECKPOINTS,
    PHYSICIST_FOUR_QUESTIONS,
    CORRESPONDENCE_LIMIT_KEYWORDS,
)

from brain.contracts import (
    L0_ARTIFACT_TEMPLATES,
    L0_SOURCE_TYPES,
    _L0_CONTRACTS,
    L1_ARTIFACT_TEMPLATES,
    L1_INTAKE_TEMPLATE,
    _L1_CONTRACTS,
    _L1_INTENSITY_CONTRACTS,
    INTERACTION_LEVELS,
    VALIDATION_DEPTHS,
    _DIRECT_SUBMIT_ACTIVITIES,
)

from brain.checks import (
    _missing_frontmatter_keys,
    _missing_required_headings,
    _check_heading_content,
    _check_derivation_steps,
    _extract_domain_rules,
    _check_question_semantic_validity,
    _generate_physics_next_action,
    _QUESTION_STEMS,
)

from brain.domains import (
    DOMAIN_ID_TO_SKILL,
    _SLUG_FALLBACK_PATTERNS,
    _detect_domains_from_contracts,
    _detect_domains_from_state,
    resolve_domain_prerequisites,
    topics_dir,
    validate_topic_slug,
    topic_root,
)

from brain.gates import (
    evaluate_l0_stage,
    evaluate_l1_stage,
    evaluate_l3_stage,
    evaluate_l4_stage,
    _load_manifest,
)

from brain.semantic import (
    PHYSICS_CONCEPT_ALIASES,
    normalize_latex,
    tokenize_for_search,
    semantic_score,
)

from brain.tool_catalog import (
    TOOL_CATALOG,
    PATTERN_B_INSTRUCTIONS,
    get_tool_catalog,
    get_pattern_b_instructions,
)
