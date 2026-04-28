@echo off
REM AITP SessionStart hook — Windows entry point for Claude Code plugin system
REM Starts HTTP MCP server if not running, then runs session_start.py

set "HOOK_DIR=%~dp0"
set "AITP_REPO_ROOT=%HOOK_DIR%.."
set "PYTHONPATH=%AITP_REPO_ROOT%;%PYTHONPATH%"
set "AITP_MCP_PORT=9876"

REM --- Ensure HTTP MCP server is running ---
REM Check if already running by hitting health endpoint
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:%AITP_MCP_PORT%/health' -TimeoutSec 2 -UseBasicParsing; exit 0 } catch { exit 1 }" 2>NUL
if %ERRORLEVEL% neq 0 (
    REM Start HTTP MCP server in background (detached)
    if defined AITP_PYTHON (
        start "" /B "%AITP_PYTHON%" "%AITP_REPO_ROOT%\brain\aitp_mcp_http.py"
    ) else (
        where python >NUL 2>NUL
        if %ERRORLEVEL% equ 0 (
            start "" /B python "%AITP_REPO_ROOT%\brain\aitp_mcp_http.py"
        ) else (
            where py >NUL 2>NUL
            if %ERRORLEVEL% equ 0 (
                start "" /B py -3 "%AITP_REPO_ROOT%\brain\aitp_mcp_http.py"
            )
        )
    )
    REM Give server time to start
    timeout /t 3 /nobreak >NUL
)

REM --- Run session_start.py ---
if defined AITP_PYTHON (
    "%AITP_PYTHON%" "%HOOK_DIR%session_start.py" %*
    exit /b %ERRORLEVEL%
)

where python >NUL 2>NUL
if %ERRORLEVEL% equ 0 (
    python "%HOOK_DIR%session_start.py" %*
    exit /b %ERRORLEVEL%
)

where py >NUL 2>NUL
if %ERRORLEVEL% equ 0 (
    py -3 "%HOOK_DIR%session_start.py" %*
    exit /b %ERRORLEVEL%
)

echo WARNING: AITP SessionStart: python not found >&2
exit /b 0
