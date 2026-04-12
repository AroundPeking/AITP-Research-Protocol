from __future__ import annotations

import shlex


def _normalized_command_tokens(command: list[str]) -> list[str]:
    return [str(part or "").strip().lower() for part in command]


def _suggested_fixes(command: list[str], *, context: str) -> list[str]:
    tokens = _normalized_command_tokens(command)
    joined = " ".join(tokens)
    suggestions = ["Rerun the command directly to inspect the tool-level output in isolation."]

    if "pip" in tokens and "install" in tokens:
        suggestions.insert(0, "Check that Python and pip can write to the target environment.")
    elif "pip" in tokens and "uninstall" in tokens:
        suggestions.insert(0, "Check that the current Python environment can remove the requested package cleanly.")
    elif tokens and tokens[0] == "git":
        suggestions.insert(0, "Check that git is installed and that the target path is a valid repository.")
    elif any(token.endswith(".py") for token in tokens) or "python" in joined:
        suggestions.insert(0, "Check that the Python environment, script path, and required runtime files are available.")

    if "install-agent" in context:
        suggestions.append("If this is a front-door install issue, retry `aitp doctor` after fixing the environment.")
    elif "migrate-local-install" in context:
        suggestions.append("If migration keeps failing, repair the Python environment first and then rerun `aitp migrate-local-install`.")

    deduped: list[str] = []
    seen: set[str] = set()
    for suggestion in suggestions:
        text = str(suggestion or "").strip()
        if text and text not in seen:
            seen.add(text)
            deduped.append(text)
    return deduped


def format_subprocess_failure(
    command: list[str],
    *,
    returncode: int,
    stdout: str = "",
    stderr: str = "",
    context: str = "subprocess",
) -> str:
    rendered_command = shlex.join([str(part) for part in command])
    trimmed_stderr = str(stderr or "").strip()
    trimmed_stdout = str(stdout or "").strip()

    lines = [
        f"AITP could not finish {context}.",
        f"Command: {rendered_command}",
        f"Exit code: {returncode}",
    ]
    if trimmed_stderr:
        lines.append(f"Error: {trimmed_stderr}")
    elif trimmed_stdout:
        lines.append(f"Output: {trimmed_stdout}")
    else:
        lines.append("Error: the command returned no stdout/stderr.")

    if trimmed_stderr and trimmed_stdout:
        lines.append(f"Additional output: {trimmed_stdout}")

    lines.append("Try:")
    for suggestion in _suggested_fixes(command, context=context):
        lines.append(f"- {suggestion}")
    return "\n".join(lines).rstrip()
