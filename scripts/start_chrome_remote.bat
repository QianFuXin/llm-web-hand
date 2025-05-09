@echo off
set PROFILE_DIR=%USERPROFILE%\.chrome-remote-profile

if not exist "%PROFILE_DIR%" (
    mkdir "%PROFILE_DIR%"
)

if exist "%PROFILE_DIR%\SingletonLock" (
    echo Removing stale lock file...
    del /f "%PROFILE_DIR%\SingletonLock"
)

start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --remote-debugging-port=9222 ^
  --user-data-dir="%PROFILE_DIR%" ^
  --no-first-run ^
  --no-default-browser-check

echo Chrome started in background with remote debugging on port 9222.