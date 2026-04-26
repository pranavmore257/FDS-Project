#!/bin/bash
# Compilation script for Java algorithms

echo "Compiling Java algorithms..."

# Navigate to algorithms directory
cd "$(dirname "$0")"

# Check if JSON library is available, if not download it
if [ ! -f "json-20231013.jar" ]; then
    echo "Downloading org.json library..."
    curl -o json-20231013.jar https://github.com/stleary/JSON-java/releases/download/20231013/json-20231013.jar
fi

# Compile all Java files
javac -cp "json-20231013.jar" Graph.java
javac -cp "json-20231013.jar" LocationHashtable.java
javac -cp "json-20231013.jar" DijkstraAlgorithm.java
javac -cp "json-20231013.jar" BellmanFordAlgorithm.java
javac -cp "json-20231013.jar" FloydWarshallAlgorithm.java
javac -cp "json-20231013.jar" AlgorithmRunner.java

echo "Compilation complete!"
