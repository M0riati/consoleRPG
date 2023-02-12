echo "Building..."
%~dp0\venv\scripts\pyinstaller.exe --add-data "venv\Lib\site-packages\pyfiglet;./pyfiglet" --add-data "venv\Lib\site-packages\pyogg;./pyogg" main.py --noconfirm --onefile -i "NONE"
echo "Copying Assets..."
xcopy %~dp0\assets\ %~dp0\dist\assets\ /E /H /C /I
