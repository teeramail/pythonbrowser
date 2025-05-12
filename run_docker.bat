@echo off
echo Building and running kiosk browser in Docker...

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Docker is not installed or not in PATH. Please install Docker Desktop for Windows.
    exit /b 1
)

REM Build and run the Docker container
docker-compose up --build

echo.
echo Docker container is running.
echo To view the kiosk browser, connect to localhost:5900 with a VNC viewer.
echo The VNC password is: password
