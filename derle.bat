@echo off
rem BORU.exe dosyasini yeniden derler (Python + PyInstaller gerekir)
cd /d "%~dp0"
python -m PyInstaller --noconfirm --onefile --windowed --name BORU --add-data "betikler;betikler" --add-data "maskot;maskot" --add-data "boru.ico;." --add-data "dil_en.json;." --add-data "bilgi/kurallar.json;bilgi" --icon boru.ico --version-file surum_bilgisi.txt boru.py
echo.
echo Cikti: dist\BORU.exe
