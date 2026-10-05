@echo off
setlocal

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r build_requirements.txt

pyinstaller --onefile --windowed --name "GameBoy Rail Shooter Editor" run_editor.py

if exist dist\GameBoy Rail Shooter Editor.exe (
    echo Build complete: dist\GameBoy Rail Shooter Editor.exe
) else (
    echo Build failed. Check PyInstaller output.
)

pause
