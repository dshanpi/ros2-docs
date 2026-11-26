@echo off
cd /d "%~dp0"
call npm run serve -- --host 127.0.0.1 --port 3000 --no-open
