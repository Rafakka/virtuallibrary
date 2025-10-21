@echo off
echo Building Portable Virtual Library...

echo Building React app...
cd virtual-library-frontend
call npm run build
cd ..

pip install pyinstaller

pyinstaller --onefile --console ^
  --name "VirtualLibrary" ^
  --add-data "virtual-library-frontend/build;virtual-library-frontend/build" ^
  --add-data "book_manager.py;." ^
  --add-data "converter.py;." ^
  --add-data "db.py;." ^
  --add-data "config_manager.py;." ^
  --hidden-import=flask ^
  --hidden-import=flask_cors ^
  --hidden-import=jinja2 ^
  --hidden-import=werkzeug ^
  --hidden-import=ebooklib ^
  --hidden-import=bs4 ^
  --hidden-import=html5lib ^
  app.py

echo.
echo ✅ Portable EXE created in 'dist' folder!
echo 📁 Copy VirtualLibrary.exe to any Windows computer
echo 🖱️ Double-click to run - no Python or Node.js required!
pause