@echo off
rem BORU yukleyicisini derler: once ..\derle.bat ile dist\BORU.exe uretilmis olmali
cd /d "%~dp0"
set ISCC="%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
%ISCC% boru.iss
