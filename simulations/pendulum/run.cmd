@echo off
setlocal
cd /d "%~dp0..\.."
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -m simulations.pendulum
    exit /b
)
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
    "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m simulations.pendulum
    exit /b
)
for /f "delims=" %%P in ('where python 2^>nul ^| findstr /v /i "WindowsApps"') do (
    "%%P" -m simulations.pendulum
    exit /b
)
echo Python 3.10 or newer with Tkinter is required.
exit /b 1
