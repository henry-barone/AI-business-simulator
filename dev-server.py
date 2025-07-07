#!/usr/bin/env python3
"""
Development server script to run both frontend and backend simultaneously.
"""

import subprocess
import sys
import os
import signal
import time
import threading
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class DevServer:
    def __init__(self):
        self.processes = []
        self.base_path = Path(__file__).parent
        self.backend_path = self.base_path / "backend"
        self.frontend_path = self.base_path / "frontend"
        
    def print_banner(self):
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
        print("🚀 AI Business Simulation - Development Server")
        print(f"{'='*60}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}Backend: {Colors.ENDC}http://localhost:5001")
        print(f"{Colors.OKGREEN}Frontend: {Colors.ENDC}http://localhost:8080")
        print(f"{Colors.WARNING}Press Ctrl+C to stop all servers{Colors.ENDC}\n")
        
    def check_dependencies(self):
        """Check if required dependencies are available"""
        print(f"{Colors.OKCYAN}🔍 Checking dependencies...{Colors.ENDC}")
        
        # Check if backend directory exists
        if not self.backend_path.exists():
            print(f"{Colors.FAIL}❌ Backend directory not found: {self.backend_path}{Colors.ENDC}")
            return False
            
        # Check if frontend directory exists
        if not self.frontend_path.exists():
            print(f"{Colors.FAIL}❌ Frontend directory not found: {self.frontend_path}{Colors.ENDC}")
            return False
            
        # Check if package.json exists in frontend
        if not (self.frontend_path / "package.json").exists():
            print(f"{Colors.FAIL}❌ Frontend package.json not found{Colors.ENDC}")
            return False
            
        # Check if app.py exists in backend
        if not (self.backend_path / "app.py").exists():
            print(f"{Colors.FAIL}❌ Backend app.py not found{Colors.ENDC}")
            return False
            
        print(f"{Colors.OKGREEN}✅ All dependencies found{Colors.ENDC}")
        return True
        
    def start_backend(self):
        """Start the Flask backend server"""
        print(f"{Colors.OKCYAN}🔧 Starting backend server...{Colors.ENDC}")
        
        try:
            # Change to backend directory and start Flask
            backend_env = os.environ.copy()
            backend_env['PYTHONPATH'] = str(self.backend_path)
            
            process = subprocess.Popen(
                [sys.executable, "-c", 
                 "from app import create_app; app = create_app(); app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)"],
                cwd=self.backend_path,
                env=backend_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes.append(('Backend', process))
            
            # Start a thread to monitor backend output
            def monitor_backend():
                for line in process.stdout:
                    if line.strip():
                        print(f"{Colors.OKBLUE}[Backend]{Colors.ENDC} {line.strip()}")
                        
            threading.Thread(target=monitor_backend, daemon=True).start()
            
            # Wait a moment for backend to start
            time.sleep(2)
            print(f"{Colors.OKGREEN}✅ Backend server started on port 5001{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to start backend: {e}{Colors.ENDC}")
            return False
            
        return True
        
    def start_frontend(self):
        """Start the React frontend server"""
        print(f"{Colors.OKCYAN}🔧 Starting frontend server...{Colors.ENDC}")
        
        try:
            # Check if node_modules exists, if not run npm install
            if not (self.frontend_path / "node_modules").exists():
                print(f"{Colors.WARNING}📦 Installing frontend dependencies...{Colors.ENDC}")
                install_process = subprocess.run(
                    ["npm", "install"],
                    cwd=self.frontend_path,
                    capture_output=True,
                    text=True
                )
                if install_process.returncode != 0:
                    print(f"{Colors.FAIL}❌ Failed to install frontend dependencies{Colors.ENDC}")
                    return False
                print(f"{Colors.OKGREEN}✅ Frontend dependencies installed{Colors.ENDC}")
            
            # Start the frontend dev server
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=self.frontend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes.append(('Frontend', process))
            
            # Start a thread to monitor frontend output
            def monitor_frontend():
                for line in process.stdout:
                    if line.strip():
                        print(f"{Colors.OKGREEN}[Frontend]{Colors.ENDC} {line.strip()}")
                        
            threading.Thread(target=monitor_frontend, daemon=True).start()
            
            # Wait a moment for frontend to start
            time.sleep(3)
            print(f"{Colors.OKGREEN}✅ Frontend server started on port 8080{Colors.ENDC}")
            
        except Exception as e:
            print(f"{Colors.FAIL}❌ Failed to start frontend: {e}{Colors.ENDC}")
            return False
            
        return True
        
    def wait_for_exit(self):
        """Wait for user to press Ctrl+C and handle graceful shutdown"""
        try:
            print(f"\n{Colors.BOLD}🎉 Development servers are running!{Colors.ENDC}")
            print(f"{Colors.OKBLUE}Backend API: {Colors.ENDC}http://localhost:5001")
            print(f"{Colors.OKGREEN}Frontend App: {Colors.ENDC}http://localhost:8080")
            print(f"\n{Colors.WARNING}Press Ctrl+C to stop all servers{Colors.ENDC}\n")
            
            # Keep the main thread alive
            while True:
                time.sleep(1)
                # Check if any process has died
                for name, process in self.processes:
                    if process.poll() is not None:
                        print(f"{Colors.FAIL}❌ {name} server has stopped unexpectedly{Colors.ENDC}")
                        self.cleanup()
                        return
                        
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}🛑 Shutting down servers...{Colors.ENDC}")
            self.cleanup()
            
    def cleanup(self):
        """Clean up all running processes"""
        for name, process in self.processes:
            try:
                print(f"{Colors.OKCYAN}Stopping {name} server...{Colors.ENDC}")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"{Colors.WARNING}Force killing {name} server...{Colors.ENDC}")
                    process.kill()
                    
            except Exception as e:
                print(f"{Colors.FAIL}Error stopping {name}: {e}{Colors.ENDC}")
                
        print(f"{Colors.OKGREEN}✅ All servers stopped{Colors.ENDC}")
        
    def run(self):
        """Main run method"""
        self.print_banner()
        
        if not self.check_dependencies():
            print(f"{Colors.FAIL}❌ Dependency check failed{Colors.ENDC}")
            return 1
            
        # Start backend first
        if not self.start_backend():
            print(f"{Colors.FAIL}❌ Failed to start backend{Colors.ENDC}")
            return 1
            
        # Start frontend
        if not self.start_frontend():
            print(f"{Colors.FAIL}❌ Failed to start frontend{Colors.ENDC}")
            self.cleanup()
            return 1
            
        # Wait for exit signal
        self.wait_for_exit()
        return 0

def main():
    """Main entry point"""
    dev_server = DevServer()
    try:
        exit_code = dev_server.run()
        sys.exit(exit_code)
    except Exception as e:
        print(f"{Colors.FAIL}❌ Unexpected error: {e}{Colors.ENDC}")
        dev_server.cleanup()
        sys.exit(1)

if __name__ == "__main__":
    main()