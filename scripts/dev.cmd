@echo off
setlocal EnableExtensions

rem Sniff + Visa - start the local stack with one command.
rem
rem   scripts\dev.cmd            live search, backend + frontend
rem   scripts\dev.cmd offline    curated catalog, deterministic demo
rem   scripts\dev.cmd mock       frontend only, no backend
rem   scripts\dev.cmd check      print prerequisites and what is already running
rem
rem The backend opens in its own window titled "sniff-visa backend".
rem Ctrl+C in this window stops the frontend only.

pushd "%~dp0.."
set "ROOT=%CD%"
popd

set "PY=%ROOT%\backend\.venv\Scripts\python.exe"
set "HEALTH=http://localhost:8000/api/health"
set "MODE=%~1"
if "%MODE%"=="" set "MODE=live"
if /I "%MODE%"=="off" set "MODE=offline"
if /I "%MODE%"=="demo" set "MODE=offline"

if /I "%MODE%"=="check" goto check
if /I "%MODE%"=="mock" goto mock
if /I "%MODE%"=="live" goto prereqs
if /I "%MODE%"=="offline" goto prereqs

echo [dev] Unknown mode "%MODE%". Use: live, offline, mock, or check.
exit /b 1

:prereqs
if not exist "%PY%" (
  echo [dev] backend\.venv is missing. Create it first:
  echo       python -m venv backend\.venv
  echo       backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
  exit /b 1
)
if not exist "%ROOT%\frontend\node_modules" (
  echo [dev] frontend\node_modules is missing. Run: cd frontend ^&^& npm ci
  exit /b 1
)

call :probe_backend
if not errorlevel 1 goto reuse_backend

if /I "%MODE%"=="offline" (
  set "OFFLINE=1"
  echo [dev] Backend mode: offline catalog, deterministic demo.
) else (
  echo [dev] Backend mode: live search.
)

echo [dev] Starting backend on http://localhost:8000 ...
start "sniff-visa backend" /d "%ROOT%\backend" "%PY%" -m uvicorn app.main:app --reload --workers 1

call :wait_backend
if errorlevel 1 (
  echo [dev] Backend did not answer on :8000 within 40s.
  echo [dev] Read the "sniff-visa backend" window for the error, or run scripts\dev.cmd check.
)
goto frontend

:reuse_backend
if /I "%MODE%"=="offline" (
  echo [dev] A backend is already answering on http://localhost:8000.
  echo [dev] Refusing to assume it is in offline mode. Close the "sniff-visa backend"
  echo [dev] window, or stop that server, then run scripts\dev.cmd offline again.
  exit /b 1
)
echo [dev] A backend is already answering on http://localhost:8000 - reusing it.
goto frontend

:frontend
echo [dev] Frontend: http://localhost:5173/ - this is the URL to open.
echo [dev] Port 5173 is pinned. If Vite says it is busy, close the other Vite window;
echo [dev] this script never falls back to 5174.
cd /d "%ROOT%\frontend"
call npm run dev -- --port 5173 --strictPort
exit /b 0

:mock
echo [dev] Frontend only, mock data, no backend needed.
echo [dev] Open http://localhost:5173/?mock=1 once Vite is up.
cd /d "%ROOT%\frontend"
call npm run dev -- --port 5173 --strictPort
exit /b 0

:check
echo Repo:        %ROOT%
if exist "%PY%" (
  echo [ok]         backend venv
) else (
  echo [MISSING]    backend venv - run: python -m venv backend\.venv
)
if exist "%ROOT%\frontend\node_modules" (
  echo [ok]         frontend node_modules
) else (
  echo [MISSING]    frontend node_modules - run: cd frontend ^&^& npm ci
)
call :probe_backend
if errorlevel 1 (
  echo [--]         no backend on :8000
) else (
  echo [ok]         backend answering on :8000
)
echo.
echo Modes: scripts\dev.cmd [live^|offline^|mock^|check]
exit /b 0

:probe_backend
curl -s -o nul --max-time 2 "%HEALTH%" >nul 2>&1
exit /b %errorlevel%

:wait_backend
set /a "_tries=0"
:wait_loop
curl -s -o nul --max-time 1 "%HEALTH%" >nul 2>&1
if not errorlevel 1 exit /b 0
set /a "_tries+=1"
if %_tries% geq 40 exit /b 1
ping -n 2 127.0.0.1 >nul
goto wait_loop
