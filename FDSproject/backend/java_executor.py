"""
Java Algorithm Wrapper
Handles compilation and execution of Java shortest path algorithms
"""

import subprocess
import json
import os
import sys
import platform
from pathlib import Path
import urllib.request

class JavaAlgorithmExecutor:
    def __init__(self):
        self.algorithm_dir = Path(__file__).parent / 'algorithms'
        self.json_jar = self.algorithm_dir / 'json-20231013.jar'
        self.compiled = False
        self._ensure_json_library()
    
    def _ensure_json_library(self):
        """Download JSON library if not present"""
        if self.json_jar.exists():
            return
        
        print("Downloading org.json library...")
        try:
            url = 'https://github.com/stleary/JSON-java/releases/download/20231013/json-20231013.jar'
            urllib.request.urlretrieve(url, str(self.json_jar))
            print("JSON library downloaded successfully")
        except Exception as e:
            print(f"Warning: Could not download JSON library: {e}")
    
    def compile_algorithms(self):
        """Compile all Java algorithm files"""
        if self.compiled and all(self._get_class_file(name).exists() 
                                 for name in ['Graph', 'DijkstraAlgorithm', 
                                            'BellmanFordAlgorithm', 'FloydWarshallAlgorithm',
                                            'LocationHashtable', 'AlgorithmRunner']):
            return True
        
        print("Compiling Java algorithms...")
        
        # Prepare classpath
        classpath = str(self.json_jar) + (';' if platform.system() == 'Windows' else ':')
        classpath += str(self.algorithm_dir)
        
        # Get all Java files
        java_files = [
            'Graph.java',
            'LocationHashtable.java',
            'DijkstraAlgorithm.java',
            'BellmanFordAlgorithm.java',
            'FloydWarshallAlgorithm.java',
            'AlgorithmRunner.java'
        ]
        
        # Compile
        try:
            for java_file in java_files:
                source_file = self.algorithm_dir / java_file
                cmd = ['javac', '-cp', classpath, str(source_file)]
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.algorithm_dir))
                
                if result.returncode != 0:
                    print(f"Compilation error in {java_file}:")
                    print(result.stderr)
                    return False
            
            self.compiled = True
            print("Java algorithms compiled successfully")
            return True
        except FileNotFoundError:
            print("Error: Java compiler (javac) not found. Make sure Java JDK is installed.")
            return False
        except Exception as e:
            print(f"Compilation error: {e}")
            return False
    
    def _get_class_file(self, class_name):
        """Get path to compiled class file"""
        return self.algorithm_dir / f'{class_name}.class'
    
    def run_algorithms(self, vertices, edges, source, destination):
        """
        Run all three algorithms and return results
        
        Args:
            vertices: list of vertex names
            edges: list of dicts with keys 'from', 'to', 'weight'
            source: source vertex name
            destination: destination vertex name
        
        Returns:
            dict with results from all three algorithms
        """
        if not self.compiled and not self.compile_algorithms():
            return {'error': 'Failed to compile Java algorithms'}
        
        # Prepare input JSON
        input_data = {
            'vertices': vertices,
            'edges': edges,
            'source': source,
            'destination': destination
        }
        
        # Run Java program
        try:
            classpath = str(self.json_jar) + (';' if platform.system() == 'Windows' else ':')
            classpath += str(self.algorithm_dir)
            
            cmd = [
                'java',
                '-cp', classpath,
                'AlgorithmRunner',
                json.dumps(input_data)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.algorithm_dir),
                timeout=30
            )
            
            if result.returncode != 0:
                return {'error': f'Java execution error: {result.stderr}'}
            
            # Parse output
            output = result.stdout.strip()
            results = json.loads(output)
            return results
        
        except subprocess.TimeoutExpired:
            return {'error': 'Java execution timeout'}
        except json.JSONDecodeError as e:
            return {'error': f'Invalid JSON output from Java: {e}'}
        except Exception as e:
            return {'error': f'Execution error: {str(e)}'}


# Global executor instance
executor = None

def get_executor():
    """Get or create the global executor instance"""
    global executor
    if executor is None:
        executor = JavaAlgorithmExecutor()
    return executor


def run_all_algorithms(vertices, edges, source, destination):
    """
    Convenience function to run all algorithms
    """
    executor = get_executor()
    return executor.run_algorithms(vertices, edges, source, destination)
