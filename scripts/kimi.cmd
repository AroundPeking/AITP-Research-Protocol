@ECHO off
REM Entrypoint wrapper — delegates to the local launcher.
CALL "%~dp0kimi-local.cmd" %*
