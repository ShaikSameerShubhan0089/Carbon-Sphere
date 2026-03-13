import uvicorn
import threading
import webbrowser
import time
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Configuration
BACKEND_PORT = 2020
FRONTEND_PORT = 3000
BACKEND_HOST = "127.0.0.1"
FRONTEND_DIR = "frontend"

def start_backend():
    print(f"🚀 Starting Backend on http://localhost:{BACKEND_PORT}")
    # Run Uvicorn
    # Use 127.0.0.1 to match frontend calls and avoid IPv6 issues
    uvicorn.run("backend.main:app", host="127.0.0.1", port=2020, reload=False, log_level="info")

def start_frontend():
    print(f"🎨 Starting Frontend on http://localhost:{FRONTEND_PORT}")
    # Change dir to frontend to serve index.html at root
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), FRONTEND_DIR))
    
    class CORSRequestHandler(SimpleHTTPRequestHandler):
        def end_headers(self):
            # Optional: Add CORS headers if usually needed, though here we are just serving static files
            self.send_header("Access-Control-Allow-Origin", "*")
            super().end_headers()

    httpd = HTTPServer(("0.0.0.0", FRONTEND_PORT), CORSRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    # 0. Auto-Activate Virtual Environment (Fix for Windows Long Path Issues)
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv")
    if os.path.exists(venv_path):
        # Check if we are already running from the venv
        # Normalize paths for comparison
        current_python = os.path.normpath(sys.executable)
        venv_python = os.path.normpath(os.path.join(venv_path, "Scripts", "python.exe"))
        
        if venv_python != current_python:
            print(f"🔄 Switching to Virtual Environment: {venv_path}...")
            # Re-execute the script with the venv python
            import subprocess
            subprocess.call([venv_python] + sys.argv)
            sys.exit()

    print("==================================================")
    print("   CarbonSphere AI - Enterprise Platform Launcher")
    print("==================================================")

    # 1. Start Backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()

    # 2. Wait a moment for backend to initialize
    time.sleep(2)

    # 3. Start Frontend in a separate thread
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    frontend_thread.start()

    # 4. Open Browser
    print("🌐 Opening Application in Browser...")
    webbrowser.open(f"http://localhost:{FRONTEND_PORT}")

    print("\n✅ System Running!")
    print(f"👉 Frontend Dashboard: http://localhost:{FRONTEND_PORT}")
    print(f"👉 Backend API Root:   http://localhost:{BACKEND_PORT}")
    print("Press CTRL+C to stop.")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        sys.exit(0)
