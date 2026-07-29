@echo off
REM Safe dry-run: counts keystrokes and shows the live speed WITHOUT sending
REM any keys anywhere. Use it to check your setup before playing for real.
cd /d "%~dp0"
call "%~dp0_setup.bat"
if not %errorlevel%==0 exit /b 1
"%~dp0.venv\Scripts\python.exe" "%~dp0automaton_attack_bot.py" --dry-run --no-guard
pause
