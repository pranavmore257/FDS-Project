#!/usr/bin/env python3
"""
Setup Verification Script
Checks if all components are properly installed and configured
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        print(f"   Current: Python {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_java_installed():
    """Check if Java JDK is installed"""
    try:
        result = subprocess.run(['javac', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Java JDK installed")
            print(f"   {result.stderr.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Java JDK not found")
    print("   Install from: https://www.oracle.com/java/technologies/downloads/")
    return False

def check_flask_installed():
    """Check if Flask is installed"""
    try:
        import flask
        print(f"✅ Flask {flask.__version__} installed")
        return True
    except ImportError:
        print("❌ Flask not installed")
        print("   Run: pip install -r requirements.txt")
        return False

def check_json_library():
    """Check if JSON library exists"""
    json_jar = Path(__file__).parent / 'algorithms' / 'json-20231013.jar'
    if json_jar.exists():
        print(f"✅ JSON library found")
        return True
    print("❌ JSON library not found")
    print(f"   Expected: {json_jar}")
    return False

def check_java_compilation():
    """Try to compile Java files"""
    algorithms_dir = Path(__file__).parent / 'algorithms'
    
    if not algorithms_dir.exists():
        print("❌ Algorithms directory not found")
        return False
    
    # Check for source files
    source_files = list(algorithms_dir.glob('*.java'))
    if not source_files:
        print("❌ No Java source files found in algorithms/")
        return False
    
    print(f"ℹ️  Found {len(source_files)} Java source files")
    
    # Try compiling one small file
    test_file = algorithms_dir / 'Graph.java'
    if not test_file.exists():
        print("❌ Graph.java not found")
        return False
    
    json_jar = algorithms_dir / 'json-20231013.jar'
    if not json_jar.exists():
        print("⚠️  JSON library missing, skipping compilation test")
        return False
    
    classpath = str(json_jar) + (';' if sys.platform == 'win32' else ':')
    classpath += str(algorithms_dir)
    
    try:
        # Try to compile
        result = subprocess.run(
            ['javac', '-cp', classpath, str(test_file)],
            capture_output=True,
            text=True,
            cwd=str(algorithms_dir)
        )
        
        if result.returncode == 0:
            # Check if class file was created
            if (algorithms_dir / 'Graph.class').exists():
                print("✅ Java compilation works")
                return True
            else:
                print("⚠️  Compilation succeeded but no .class file found")
                return False
        else:
            print("❌ Java compilation failed")
            print(f"   Error: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"❌ Compilation test failed: {e}")
        return False

def check_api_endpoints():
    """Check if backend API can be reached"""
    try:
        import requests
        print("ℹ️  Checking if backend is running on http://127.0.0.1:5000...")
        response = requests.get('http://127.0.0.1:5000/', timeout=2)
        if response.status_code == 200:
            print("✅ Backend API is running")
            return True
    except:
        print("⚠️  Backend not running (start with: python app.py)")
        return False

def check_frontend_files():
    """Check if frontend files exist"""
    frontend_dir = Path(__file__).parent.parent / 'frontend'
    
    required_files = [
        'index.html',
        'script.js',
        'styles.css'
    ]
    
    missing = []
    for file in required_files:
        if not (frontend_dir / file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ Frontend files missing: {', '.join(missing)}")
        return False
    
    print("✅ All frontend files present")
    return True

def main():
    """Run all checks"""
    print("=" * 60)
    print("FDS Project Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Java JDK", check_java_installed),
        ("Flask", check_flask_installed),
        ("JSON Library", check_json_library),
        ("Java Compilation", check_java_compilation),
        ("Frontend Files", check_frontend_files),
        ("Backend API", check_api_endpoints),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[Checking] {name}...")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Check failed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All checks passed! Ready to use.")
        return 0
    elif passed >= total - 2:
        print("\n⚠️  Some checks failed, but application may still work.")
        print("   Check the errors above and follow the instructions.")
        return 1
    else:
        print("\n❌ Multiple checks failed. See instructions above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
