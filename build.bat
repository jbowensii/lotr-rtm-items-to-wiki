@echo off
echo Building Moria Wiki Generator...
echo.

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Build with PyInstaller
pyinstaller --clean MoriaWikiGenerator.spec

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build successful!
    echo Executable created at: dist\MoriaWikiGenerator.exe
) else (
    echo.
    echo Build failed with error code %ERRORLEVEL%
)

pause
