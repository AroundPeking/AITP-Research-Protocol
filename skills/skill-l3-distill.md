---
name: skill-l3-distill
description: L3 Distillation subplane — extract final claims from integrated results.
trigger: l3_subplane == "distillation"
---

# L3 Distillation

## MANDATORY: AskUserQuestion rule

When you need to ask the user ANY question (clarification, scope, direction, missing info), you MUST:
1. Call `ToolSearch(query="select:AskUserQuestion", max_results=1)` to load the tool.
2. Call `AskUserQuestion(questions=[{...}])` with your question and options.
NEVER type questions or options as plain text. ALWAYS use the popup tool.

---

You are in the distillation subplane of L3 derivation.

## Active artifact

`L3/distillation/active_distillation.md`

## What to do

1. Extract the distilled claim from integrated findings.
2. Summarize the supporting evidence.
3. Assign a confidence level.
4. List remaining open questions.

## Exit condition

When `active_distillation.md` has filled frontmatter fields `distilled_claim`
and `evidence_summary`, plus headings `## Distilled Claim` and `## Evidence Summary`,
the L3 flow is complete. You may then:
- Generate `L3/tex/flow_notebook.tex` and compile to PDF (see below).
- Advance to L4 for adjudication.

## Flow Notebook Generation (MANDATORY)

When L3 derivation is complete, you MUST produce a readable PDF by converting all
L3 Markdown artifacts into proper LaTeX yourself. Do NOT call `aitp_render_flow_notebook`.

### Step 1: Read all L3 Markdown content

Read every artifact under `L3/`:
- `L3/distillation/active_distillation.md`
- `L3/ideation/*.md`, `L3/plan/*.md`, `L3/analysis/*.md`, `L3/integration/*.md`
- Any other subplane outputs

### Step 2: Convert Markdown to LaTeX properly

You MUST perform full Markdown-to-LaTeX conversion. Apply these rules EXACTLY:

| Markdown | LaTeX |
|---|---|
| `# Heading` | `\section{Heading}` |
| `## Heading` | `\subsection{Heading}` |
| `### Heading` | `\subsubsection{Heading}` |
| `**bold**` | `\textbf{bold}` |
| `*italic*` | `\textit{italic}` |
| `- item` or `* item` | `\begin{itemize} \item item \end{itemize}` |
| `1. item` | `\begin{enumerate} \item item \end{enumerate}` |
| `` `inline code` `` | `\texttt{inline code}` |
| Markdown table | `\begin{table}...\end{table}` with `tabular` environment |
| `\[math\]` | `\(math\)` or `$math$` |
| `$$math$$` | `\begin{equation}...\end{equation}` |
| `> blockquote` | `\begin{quote}...\end{quote}` |
| `---` (horizontal rule) | `\noindent\rule{\textwidth}{0.4pt}` |

CRITICAL: Do NOT paste raw Markdown into LaTeX. Every line must be valid LaTeX.
Tables in particular MUST use `\begin{tabular}` — never pipe-delimited Markdown.

### Step 3: Write flow_notebook.tex

Use the AITP template as the skeleton. Read the template file at:
```
<aitp-repo-root>/templates/flow_notebook.tex
```
(Where `<aitp-repo-root>` is the local path to the aitp-v2-refactor repository.)

Copy the template to `L3/tex/flow_notebook.tex`, then replace every
`{{PLACEHOLDER}}` with the corresponding converted LaTeX content.
Remove any placeholder sections that have no corresponding artifact.

### Step 4: Compile to PDF

Run pdflatex on the generated file:

```bash
cd "<topics_root>/<topic_slug>/L3/tex"
pdflatex -interaction=nonstopmode flow_notebook.tex
pdflatex -interaction=nonstopmode flow_notebook.tex
```

If compilation fails:
1. Read the `.log` file to identify the error.
2. Fix the LaTeX error in `flow_notebook.tex`.
3. Retry compilation.
4. Repeat until PDF is produced.

If `pdflatex` is not available, try `latexmk -pdf flow_notebook.tex`.

### Step 5: Report

Tell the human:
- Path to the compiled PDF
- Brief summary of what L3 produced

## Allowed transitions

- Forward: L4 adjudication
- Backedges: `result_integration`
