@echo off
REM Lists every open window title. Use this if the bot says it is WAITING for
REM Dota - copy the distinctive part of the real title into config.json.
cd /d "%~dp0"
call "%~dp0_setup.bat"
if not %errorlevel%==0 exit /b 1
"%~dp0.venv\Scripts\python.exe" "%~dp0automaton_attack_bot.py" --windows
pause
