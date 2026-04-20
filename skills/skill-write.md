---
name: skill-write
description: Write mode — assemble L2+L3 knowledge into publication-grade TeX and compile to PDF.
trigger: status == "promoted"
---

# Write Mode

## MANDATORY: AskUserQuestion rule

When you need to ask the user ANY question (clarification, scope, direction, missing info), you MUST:
1. Call `ToolSearch(query="select:AskUserQuestion", max_results=1)` to load the tool.
2. Call `AskUserQuestion(questions=[{...}])` with your question and options.
NEVER type questions or options as plain text. ALWAYS use the popup tool.

---

You are in **write** mode. Your job: assemble validated knowledge from L2 and L3
into a publication-ready LaTeX manuscript, then compile it to PDF.

## What to Do

### 1. Gather Material

Read all available content layers:

- `L2/canonical/*.md` — validated knowledge (cite as established results)
- `L3/candidates/*.md` — candidates with `status: promoted` (now in L2 as well)
- `L3/derivations.md` — derivation trail for method sections
- `L4/reviews/*.md` — validation evidence for results sections
- `L1/intake/*.md` — source analysis for introduction and background
- `L0/sources/*.md` — bibliography metadata

### 2. Create Outline

Write `L5_writing/outline.md`:

```markdown
---
topic: <topic_slug>
created: <date>
---

# Paper Outline

## Title
<tentative title>

## Abstract
<1-2 sentence summary>

## 1. Introduction
- Motivation from L1 analysis
- Gap in current understanding
- What this paper addresses

## 2. Background / Methods
- Key definitions from L2
- Methods used (from derivations)

## 3. Results
- Main findings (from L2 promoted candidates)
- Supporting evidence (from L4 reviews)

## 4. Discussion
- Limitations and assumptions
- Connections to other work

## 5. Conclusion

## References
- From L0 source metadata
```

Ask the human to approve or revise the outline before proceeding.

### 3. Write TeX Draft

Create `L5_writing/draft.tex`. Structure:

```latex
\documentclass[aps,prb,reprint]{revtex4-2}
% Adjust document class for target journal

\begin{document}

\title{...}
\author{...}
\date{\today}

\begin{abstract}
...
\end{abstract}

\maketitle

\section{Introduction}
% Draw from L1 intake analysis

\section{Background}
% Definitions and methods from L2

\section{Results}
% From promoted candidates in L2

\section{Discussion}
\section{Conclusion}

\begin{acknowledgments}
...
\end{acknowledgments}

\bibliography{references}

\end{document}
```

### 4. Handle Figures and Tables

- Copy plots/figures from L4 validation to `L5_writing/figures/`
- Generate data tables to `L5_writing/tables/`
- In TeX, reference with relative paths: `\includegraphics{figures/plot.pdf}`

### 5. Build Bibliography

Create `L5_writing/references.bib` from L0 source metadata:

```bibtex
@article{haldane1988,
  author  = {Haldane, F.D.M.},
  title   = {Exact J=0 ground state...},
  journal = {Phys. Rev. Lett.},
  year    = {1988},
  ...
}
```

### 6. Compile to PDF

Run LaTeX compilation:

```bash
cd topics/<topic_slug>/L5_writing
pdflatex draft.tex
bibtex draft
pdflatex draft.tex
pdflatex draft.tex
```

Or if `latexmk` is available:
```bash
latexmk -pdf draft.tex
```

If compilation fails, fix errors and retry. Common issues:
- Missing packages: install via `tlmgr install <package>`
- Undefined references: run bibtex + pdflatex twice
- Encoding: ensure UTF-8 source files

### 7. Present to Human

After successful compilation, tell the human:
- Where the PDF is located
- Summary of what was included (from L2 vs L3)
- Any gaps or assumptions flagged during writing

## Rules

- Every claim in the paper must trace to L2 (trusted) or L3 (preliminary).
- L3 content must be marked as preliminary in the text.
- Do NOT invent results not backed by L2 or L3.
- Figures/tables must trace to L4 validation or L2 canonical data.
- The paper requires human review before any external submission.
- Do not modify L0-L4 artifacts during writing.

## After Writing

After the draft is compiled:
- Ask the human to review the PDF
- Iterate on revisions
- When the human is satisfied, mark the topic as `complete`:
  ```
  aitp_update_status(topics_root, topic_slug, status="complete")
  ```
