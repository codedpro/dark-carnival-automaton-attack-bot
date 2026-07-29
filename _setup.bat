@echo off
REM ============================================================
REM  Automaton Attack Bot - one-time environment setup
REM  Finds (or installs) Python, then builds a local .venv with
REM  all dependencies. Called by run.bat / test.bat.
REM  Nothing here touches your system Python or global packages.
REM ============================================================
set "VENV=%~dp0.venv"
set "PYEXE=%VENV%\Scripts\python.exe"

REM Fast path: environment already built.
if exist "%PYEXE%" if exist "%VENV%\.deps_ok" exit /b 0

REM --- Locate a base Python interpreter --------------------------------------
set "BASEPY="
where py >nul 2>nul
if %errorlevel%==0 set "BASEPY=py -3"
if defined BASEPY goto :got_base
where python >nul 2>nul
if %errorlevel%==0 set "BASEPY=python"
if defined BASEPY goto :got_base
goto :install_python

:install_python
echo.
echo Python was not found on this PC.
where winget >nul 2>nul
if not %errorlevel%==0 goto :no_winget
echo Installing Python 3.12 automatically (this can take a couple of minutes)...
winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
echo.
echo ============================================================
echo   Python is installed.
echo   Please CLOSE this window and double-click the file again
echo   to finish setup.
echo ============================================================
pause
exit /b 1

:no_winget
echo.
echo Could not install Python automatically ^(winget is unavailable^).
echo Please install Python 3.12 from:  https://www.python.org/downloads/
echo IMPORTANT: on the first install screen, TICK "Add python.exe to PATH".
echo Then double-click this file again.
echo.
pause
exit /b 1

:got_base
if exist "%PYEXE%" goto :deps
echo Creating a local Python environment (one-time)...
%BASEPY% -m venv "%VENV%"
if not exist "%PYEXE%" (
  echo [error] Failed to create the local environment.
  pause
  exit /b 1
)

:deps
if exist "%VENV%\.deps_ok" exit /b 0
echo Installing dependencies (one-time, needs internet)...
"%PYEXE%" -m pip install --upgrade pip
"%PYEXE%" -m pip install -r "%~dp0requirements.txt"
if not %errorlevel%==0 (
  echo [error] Could not install dependencies. Check your internet and try again.
  pause
  exit /b 1
)
> "%VENV%\.deps_ok" echo ok
exit /b 0
