@ECHO OFF
SETLOCAL

FOR %%I IN ("%~dp0..") DO SET "AITP_REPO_ROOT=%%~fI"
SET "AITP_KERNEL_ROOT=%AITP_REPO_ROOT%\research\knowledge-hub"

IF DEFINED PYTHONPATH (
  SET "PYTHONPATH=%AITP_KERNEL_ROOT%;%PYTHONPATH%"
) ELSE (
  SET "PYTHONPATH=%AITP_KERNEL_ROOT%"
)

IF DEFINED AITP_PYTHON (
  "%AITP_PYTHON%" -m knowledge_hub.aitp_codex %*
  EXIT /B %ERRORLEVEL%
)

where python >NUL 2>NUL
IF %ERRORLEVEL% EQU 0 (
  python -m knowledge_hub.aitp_codex %*
  EXIT /B %ERRORLEVEL%
)

where py >NUL 2>NUL
IF %ERRORLEVEL% EQU 0 (
  py -3 -m knowledge_hub.aitp_codex %*
  EXIT /B %ERRORLEVEL%
)

ECHO Python 3 launcher not found on PATH.>&2
EXIT /B 127
