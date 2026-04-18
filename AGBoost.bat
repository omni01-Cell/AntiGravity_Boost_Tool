@echo off
setlocal
cd /d "%~dp0"
py agboost_cli.py %*
endlocal
