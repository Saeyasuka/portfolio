@echo off
REM Double-click this after adding or removing photos in the images folder.
cd /d "%~dp0"
python build_gallery.py
echo.
echo Done! Refresh your website (Ctrl+F5) to see the changes.
pause
