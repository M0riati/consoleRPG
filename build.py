import PyInstaller.__main__
import shutil
import pyogg
import pyfiglet

pyoggPath = pyogg.__path__[0]
pyfigletPath = pyfiglet.__path__[0]

PyInstaller.__main__.run([
    'main.py',
    '--noconfirm',
    '--onefile',
    '--add-data',
    pyoggPath + ';./pyogg',
    '--add-data',
    pyfigletPath + ';./pyfiglet',
    '-i',
    'NONE'
])

shutil.rmtree('dist/assets')
shutil.copytree('assets', 'dist/assets')