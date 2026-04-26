@echo off
REM Compilation script for Java algorithms (Windows)

echo Compiling Java algorithms...

REM Navigate to the script directory
cd /d "%~dp0"

REM Check if JSON library exists
if not exist "json-20231013.jar" (
    echo Downloading org.json library...
    powershell -Command "(New-Object System.Net.ServicePointManager).SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; Invoke-WebRequest -Uri 'https://github.com/stleary/JSON-java/releases/download/20231013/json-20231013.jar' -OutFile 'json-20231013.jar'"
)

REM Compile all Java files
javac -cp "json-20231013.jar" Graph.java
if errorlevel 1 goto error

javac -cp "json-20231013.jar" LocationHashtable.java
if errorlevel 1 goto error

javac -cp "json-20231013.jar" DijkstraAlgorithm.java
if errorlevel 1 goto error

javac -cp "json-20231013.jar" BellmanFordAlgorithm.java
if errorlevel 1 goto error

javac -cp "json-20231013.jar" FloydWarshallAlgorithm.java
if errorlevel 1 goto error

javac -cp "json-20231013.jar" AlgorithmRunner.java
if errorlevel 1 goto error

echo Compilation complete!
goto end

:error
echo Compilation failed!
exit /b 1

:end
