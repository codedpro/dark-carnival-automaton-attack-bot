@echo off
REM Double-click this to play. First run auto-installs everything (one-time).
cd /d "%~dp0"
call "%~dp0_setup.bat"
if not %errorlevel%==0 exit /b 1
"%~dp0.venv\Scripts\python.exe" "%~dp0automaton_attack_bot.py" %*
pause
