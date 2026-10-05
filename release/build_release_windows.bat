@echo off
setlocal

echo ========================================
echo Game Boy Rail Shooter Editor - Release
echo ========================================
echo.

python -m pip install --upgrade pip > nul 2>&1
python -m pip install -r ..\requirements.txt > nul 2>&1
python -m pip install -r ..\build_requirements.txt > nul 2>&1
pyinstaller --onefile --windowed --name "GameBoy Rail Shooter Editor" ..\run_editor.py

if exist ..\dist\GameBoy Rail Shooter Editor.exe (
    echo [SUCCESS] Release built successfully.
    echo Output: ..\dist\GameBoy Rail Shooter Editor.exe
) else (
    echo [ERROR] Build failed. Check PyInstaller output.
)

echo.
pause
