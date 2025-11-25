#!/usr/bin/env python3
"""
AIDE V2 - Zero Cost Ollama Demo
Single command to start entire system
"""

import os
import sys
import subprocess
import threading
from pathlib import Path

def check_ollama():
    """Verify Ollama is installed and running"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ Ollama not running. Starting Ollama...")
            subprocess.Popen(['ollama', 'serve'])
            import time
            time.sleep(3)
        print("✅ Ollama is ready")
        return True
    except Exception as e:
        print(f"❌ Ollama check failed: {e}")
        print("Please install Ollama from https://ollama.ai/")
        return False

def start_backend():
    """Start the Python WebSocket server"""
    print("🚀 Starting Agent Server...")
    backend_dir = Path('agent-server')
    subprocess.run([sys.executable, 'main.py'], cwd=backend_dir)

def start_frontend():
    """Start the Vue frontend"""
    print("🎨 Starting Web UI...")
    frontend_dir = Path('web-ui')
    subprocess.run(['npm', 'run', 'dev'], shell=True, cwd=frontend_dir)
    
def main():
    print("=" * 50)
    print("🤖 AIDE V2 - Zero Cost AI Agent Demo")
    print("=" * 50)
    
    # Check dependencies
    if not check_ollama():
        return
    
    # Create necessary directories
    Path("projects").mkdir(exist_ok=True)
    Path("projects/templates").mkdir(exist_ok=True)
    
    print("📁 Project structure verified")
    
    # Start services in threads
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    
    backend_thread.start()
    frontend_thread.start()
    
    print("✅ Both services starting...")
    print("🌐 Web UI will open at: http://localhost:3000")
    print("🔧 Agent Server at: ws://localhost:8765")
    
    try:
        # Keep main thread alive
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AIDE V2...")

if __name__ == "__main__":
    main()