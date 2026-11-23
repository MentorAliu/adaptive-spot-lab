@echo off
rem The Docker clean-up's starter (ExecPlan 0034): double-click it. It runs tools\docker-cleanup.ps1 as GitHub's
rem main has it, on the app folder: the folder this file is in, or the one above when it lies in tools.
rem Windows asks once for administrator rights (for the disk compaction). The window stays open at the end.
setlocal
set "REPO=%~dp0"
if not exist "%REPO%compose.yaml" set "REPO=%~dp0..\"
pushd "%REPO%" || goto :missing
set "REPO=%CD%"
set "GIT_TERMINAL_PROMPT=0"
where git >nul 2>nul || if exist "%ProgramFiles%\Git\cmd\git.exe" set "PATH=%ProgramFiles%\Git\cmd;%PATH%"
set "STARTER=%TEMP%\asl-docker-cleanup-%RANDOM%%RANDOM%.ps1"
git fetch --quiet origin main
git show origin/main:tools/docker-cleanup.ps1 > "%STARTER%" 2>nul
if errorlevel 1 (
    del "%STARTER%" 2>nul
    set "STARTER=%REPO%\tools\docker-cleanup.ps1"
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%STARTER%" -Repository "%REPO%"
set "RESULT=%ERRORLEVEL%"
if /i not "%STARTER%"=="%REPO%\tools\docker-cleanup.ps1" del "%STARTER%" 2>nul
popd
echo.
if "%RESULT%"=="0" (echo The clean-up is done. You can close this window.) else (echo The clean-up stopped: the lines above say where. You can close this window.)
pause >nul
exit /b %RESULT%

:missing
echo The app folder was not found next to this file.
pause >nul
exit /b 1
