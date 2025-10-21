@echo off
echo Building React app...
cd virtual-library-frontend
call npm run build
cd ..

echo Starting Virtual Library...
start "" "http://localhost:5000"
timeout /t 2
python app.py