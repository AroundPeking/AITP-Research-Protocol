@echo off
:: AITP shortcut — runs aitp-pm.py with all forwarded args
:: Tries multiple Python detection strategies before giving up
set "PM_PATH=%~dp0aitp-pm.py"

:: 1. Explicit override
if defined AITP_PYTHON (
    "%AITP_PYTHON%" "%PM_PATH%" %*
    exit /b %ERRORLEVEL%
)

:: 2. python (standard)
where python >NUL 2>NUL
if %ERRORLEVEL% equ 0 (
    python "%PM_PATH%" %*
    exit /b %ERRORLEVEL%
)

:: 3. python3 (some Unix-on-Windows setups)
where python3 >NUL 2>NUL
if %ERRORLEVEL% equ 0 (
    python3 "%PM_PATH%" %*
    exit /b %ERRORLEVEL%
)

:: 4. py launcher (Windows Python)
where py >NUL 2>NUL
if %ERRORLEVEL% equ 0 (
    py -3 "%PM_PATH%" %*
    exit /b %ERRORLEVEL%
)

echo AITP: Could not find Python. Install Python 3.10+ or set AITP_PYTHON env var. 1>&2
exit /b 1
