"""
Thin bridge: Claude Code Content-Length framing <-> FastMCP 3.x ndjson stdio.

FastMCP 3.x reads/writes newline-delimited JSON on stdout/stdin.
Claude Code reads/writes Content-Length-prefixed JSON per MCP spec.
This adapter translates between the two.
"""
from __future__ import annotations

import os
import subprocess
import sys
import threading


def read_claude_message(stream) -> str | None:
    """Read one Content-Length-framed message from stream."""
    header = b""
    while True:
        ch = stream.read(1)
        if not ch:
            return None
        header += ch
        if header.endswith(b"\r\n\r\n"):
            break
    header_str = header.decode("utf-8")
    content_length = 0
    for line in header_str.split("\r\n"):
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":", 1)[1].strip())
            break
    if content_length <= 0:
        return None
    body = stream.read(content_length)
    return body.decode("utf-8")


def write_claude_message(stream, message: str) -> None:
    """Write one Content-Length-framed message to stream."""
    body = message.encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
    stream.write(header + body)
    stream.flush()


def main():
    server_script = os.path.join(os.path.dirname(__file__), "..", "mcp_server.py")
    server_script = os.path.abspath(server_script)

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    proc = subprocess.Popen(
        [sys.executable, server_script],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=sys.stderr,
        env=env,
        bufsize=0,
    )

    # Forward Claude stdin (Content-Length framed) -> FastMCP stdin (ndjson)
    def forward_to_server():
        while True:
            msg = read_claude_message(sys.stdin.buffer)
            if msg is None:
                break
            proc.stdin.write(msg.encode("utf-8") + b"\n")
            proc.stdin.flush()

    threading.Thread(target=forward_to_server, daemon=True).start()

    # Forward FastMCP stdout (ndjson) -> Claude stdout (Content-Length framed)
    for line in proc.stdout:
        decoded = line.decode("utf-8").strip()
        if decoded:
            write_claude_message(sys.stdout.buffer, decoded)

    proc.wait()


if __name__ == "__main__":
    main()
