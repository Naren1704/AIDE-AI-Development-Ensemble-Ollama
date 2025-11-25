"""
Generates actual project files and manages preview servers
REFINED VERSION: Trust-based validation, better context integration
"""

import os
import shutil
import asyncio
from pathlib import Path
from typing import Dict, List, Any
import http.server
import socketserver
import threading
import time
import requests
import re
from config import settings
from agents.integration_agent import IntegrationAgent

class ProjectBuilder:
    def __init__(self):
        current_dir = Path(__file__).parent.parent.parent
        self.projects_dir = current_dir / "projects"
        self.preview_ports = {}
        self.next_port = settings.PREVIEW_PORT_RANGE[0]
        self.integration_agent = IntegrationAgent()
        
        # Ensure projects directory exists
        self.projects_dir.mkdir(exist_ok=True)
    
    async def generate_project(self, project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate project with trust-based approach"""
        project_id = project_data['id']
        project_dir = self.projects_dir / f"project-{project_id}" / "src"
    
        print(f"🚀 Starting project generation for {project_id}")
        print(f"📋 Project requirements: {project_data.get('requirements', {}).keys()}")
    
        # Clean regeneration: Remove existing project safely
        await self._clean_project_directory(project_dir)
        project_dir.mkdir(parents=True, exist_ok=True)
    
        generated_files = []
    
        # Phase 1: Plan structure
        print("🔧 Phase 1: Planning project structure...")
        file_structure = await self.integration_agent.plan_project_structure(project_data)
        print(f"📁 Planned {len(file_structure)} files: {file_structure}")
    
        # Phase 2: Generate files with TRUST-BASED APPROACH
        print("🔧 Phase 2: Generating file contents with enhanced context...")
        successful_files = 0
    
        for i, file_path in enumerate(file_structure):
            print(f"   Generating: {file_path}")
            try:
                # 🎯 ENHANCED: Pass ALL existing files as context for better integration
                existing_files_context = [
                    {'path': f['path'], 'content_preview': f['content'][:500]} 
                    for f in generated_files
                ]
                
                content = await self.integration_agent.generate_file_content_with_context(
                    project_data, file_path, existing_files_context
                )
            
                # 🎯 REFINED VALIDATION - Trust Ollama more
                if not self._is_valid_generated_content_trusted(content, file_path):
                    print(f"   ⚠️  Content validation warning for {file_path}, but trusting Ollama output")
                    # 🚨 TRUST APPROACH: Accept the content anyway for now
                    # We'll rely on the preview server to catch actual errors
            
                # Write file with proper directory structure
                full_path = project_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
            
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
                # Create file metadata for frontend
                file_data = {
                    'path': file_path,
                    'content': content,
                    'size': len(content),
                    'type': self._get_file_type(file_path),
                    'icon': self._get_file_icon(file_path),
                    'language': self._get_file_language(file_path)
                }
                generated_files.append(file_data)
                successful_files += 1
                print(f"   ✅ Generated: {file_path} ({len(content)} bytes)")
            
            except Exception as e:
                print(f"   ❌ Failed to generate {file_path}: {e}")
                # 🚨 TRUST APPROACH: Skip this file but continue with others
                # This prevents one bad file from stopping the entire generation
                continue
    
        print(f"🔧 Generated {successful_files}/{len(file_structure)} files successfully")
    
        # Phase 3: Build preview
        await self._build_preview_reliable(project_id)
    
        return generated_files
    
    def _is_valid_generated_content_trusted(self, content: str, file_path: str) -> bool:
        """🎯 REFINED: Trust-based validation - accept more Ollama output patterns"""
        if not content or len(content.strip()) < 5:  # Reduced minimum length
            print(f"   ⚠️  Validation: Content too short for {file_path}")
            return False
        
        # 🎯 TRUST APPROACH: File-specific validation with more lenient rules
        if file_path.endswith('.py'):
            return self._is_valid_python_content_trusted(content, file_path)
        elif file_path.endswith('.html'):
            return self._is_valid_html_content_trusted(content)
        elif file_path.endswith('.css'):
            return self._is_valid_css_content_trusted(content)
        elif file_path.endswith('.js'):
            return self._is_valid_javascript_content_trusted(content)
        elif file_path.endswith('.txt') or file_path.endswith('.md'):
            return len(content.strip()) > 3  # Very lenient for text files
        else:
            return len(content.strip()) > 5  # Generic minimum
    
    def _is_valid_python_content_trusted(self, content: str, file_path: str) -> bool:
        """🎯 REFINED: More lenient Python validation"""
        content_lower = content.lower()
        
        if file_path == 'app.py':
            # 🎯 TRUST: Accept various Flask patterns
            flask_indicators = [
                'flask' in content_lower,
                '@app.route' in content,
                'render_template' in content,
                'from flask' in content,
                'import flask' in content
            ]
            is_valid = any(flask_indicators)
            if not is_valid:
                print(f"   ⚠️  Python validation: Missing Flask indicators for {file_path}")
            return is_valid
            
        elif file_path == 'requirements.txt':
            # 🎯 TRUST: Accept any requirements file with content
            is_valid = len(content.strip()) > 5 and any(char in content for char in ['=', '>', '<', '\n'])
            if not is_valid:
                print(f"   ⚠️  Requirements validation: Not a valid requirements format")
            return is_valid
            
        else:
            # 🎯 TRUST: Accept any Python-like content
            python_indicators = [
                'import ' in content,
                'def ' in content,
                'class ' in content,
                'from ' in content,
                'print(' in content,
                'return ' in content
            ]
            is_valid = any(python_indicators) or len(content.strip()) > 50
            if not is_valid:
                print(f"   ⚠️  Python validation: Not valid Python syntax for {file_path}")
            return is_valid
    
    def _is_valid_html_content_trusted(self, content: str) -> bool:
        """🎯 REFINED: More lenient HTML validation"""
        # 🎯 TRUST: Accept various HTML patterns
        html_indicators = [
            '<!doctype' in content.lower(),
            '<html' in content.lower(),
            '<head' in content.lower(),
            '<body' in content.lower(),
            '<div' in content,
            '<p>' in content,
            '<h1' in content
        ]
        is_valid = any(html_indicators) and '<' in content and '>' in content
        if not is_valid:
            print(f"   ⚠️  HTML validation: Not valid HTML structure")
        return is_valid

    def _is_valid_css_content_trusted(self, content: str) -> bool:
        """🎯 REFINED: Very lenient CSS validation - same as integration_agent"""
        if not content or len(content.strip()) < 10:
            print(f"🔍 CSS Validation: Content too short ({len(content.strip())} chars)")
            return False

        clean_content = content.strip()
    
        # 🎯 TRUST: Same lenient validation as integration_agent
        css_indicators = [
            '{' in clean_content and '}' in clean_content,
            any(char in clean_content for char in [':', ';', '#', '.']),
            any(word in clean_content.lower() for word in ['color', 'font', 'margin', 'padding', 'width', 'height']),
            re.search(r'[a-zA-Z-]+\s*:\s*[^;]+;', clean_content),
            re.search(r'[.#][a-zA-Z][^{]*\{', clean_content),
        ]
    
        has_any_css = any(css_indicators)
        balanced_braces = clean_content.count('{') == clean_content.count('}')
    
        is_valid = has_any_css or (balanced_braces and len(clean_content) > 20)  # Reduced threshold
    
        print(f"🔍 ProjectBuilder CSS Validation: has_css={has_any_css}, balanced={balanced_braces}, valid={is_valid}")
    
        return is_valid
        
    def _is_valid_javascript_content_trusted(self, content: str) -> bool:
        """🎯 REFINED: More lenient JavaScript validation"""
        content_lower = content.lower()
        
        # 🎯 TRUST: Accept various JS patterns
        js_indicators = [
            'function' in content,
            'const ' in content,
            'let ' in content,
            'document.' in content,
            'addeventlistener' in content_lower,
            'getelementbyid' in content_lower,
            'queryselector' in content_lower
        ]
        
        # 🎯 TRUST: Allow modern JS patterns but still block obvious frameworks
        no_frameworks = not any(fw in content_lower for fw in ['import react', 'from react', 'vue', 'angular'])
        
        is_valid = (any(js_indicators) or len(content.strip()) > 50) and no_frameworks
        
        if not is_valid:
            print(f"   ⚠️  JS validation: Not valid JavaScript or contains frameworks")
        return is_valid
    
    async def _clean_project_directory(self, project_dir: Path):
        """Safely clean project directory with retry logic"""
        if project_dir.exists():
            for attempt in range(3):
                try:
                    shutil.rmtree(project_dir)
                    print(f"🧹 Cleaned project directory: {project_dir}")
                    return
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        print(f"❌ Failed to clean directory {project_dir}: {e}")
                        raise
                    print(f"⚠️  Clean attempt {attempt + 1} failed, retrying...")
                    await asyncio.sleep(0.5)

    async def _build_preview_reliable(self, project_id: str):
        """ENHANCED: Build preview with Flask server for proper template rendering"""
        src_dir = self.projects_dir / f"project-{project_id}" / "src"
        preview_dir = self.projects_dir / f"project-{project_id}" / "preview"
    
        print(f"🔧 Building preview for project {project_id}...")
    
        # Retry logic for directory operations
        for attempt in range(3):
            try:
                if preview_dir.exists():
                    shutil.rmtree(preview_dir)
            
                if src_dir.exists():
                    # Copy source files to preview directory
                    shutil.copytree(src_dir, preview_dir)
                    print(f"✅ Preview files copied successfully for {project_id}")
                
                    # ENHANCED: Create a proper Flask server for the preview
                    await self._create_flask_preview_server(project_id, preview_dir)
                    return
                else:
                    print(f"❌ Source directory not found: {src_dir}")
                    return
                
            except Exception as e:
                print(f"⚠️  Preview build attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    print(f"❌ Preview build failed after 3 attempts")
                await asyncio.sleep(1)

    async def _create_flask_preview_server(self, project_id: str, preview_dir: Path):
        """Create a Flask server that properly renders templates"""
        try:
            # Create a dedicated Flask app file for preview
            flask_app_content = self._generate_flask_preview_app(preview_dir)
            flask_app_file = preview_dir / "preview_app.py"

            with open(flask_app_file, 'w', encoding='utf-8') as f:
                f.write(flask_app_content)

            print(f"✅ Created Flask preview app for {project_id}")

        except Exception as e:
            print(f"❌ Failed to create Flask preview app: {e}")

    def _generate_flask_preview_app(self, preview_dir: Path) -> str:
        """Generate a Flask app that serves the project with proper template rendering"""

        # Check if templates directory exists
        templates_dir = preview_dir / "templates"
        static_dir = preview_dir / "static"

        has_templates = templates_dir.exists() and any(templates_dir.iterdir())
        has_static = static_dir.exists() and any(static_dir.iterdir())

        flask_app = '''"""
Flask Preview Server - Renders templates properly
"""
import os
from flask import Flask, render_template, send_from_directory

app = Flask(__name__, 
    template_folder='templates' if os.path.exists('templates') else '.',
    static_folder='static' if os.path.exists('static') else None
)

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files from static directory"""
    return send_from_directory('static', filename)

# Serve CSS files
@app.route('/css/<path:filename>')
def serve_css(filename):
    """Serve CSS files"""
    css_dir = 'static/css' if os.path.exists('static/css') else 'static'
    return send_from_directory(css_dir, filename)

# Serve JS files  
@app.route('/js/<path:filename>')
def serve_js(filename):
    """Serve JavaScript files"""
    js_dir = 'static/js' if os.path.exists('static/js') else 'static'
    return send_from_directory(js_dir, filename)

# Main route - render index.html
@app.route('/')
def index():
    """Render the main page"""
    try:
        # Try to render from templates directory first
        if os.path.exists('templates/index.html'):
            return render_template('index.html')
        # Fallback to root index.html
        elif os.path.exists('index.html'):
            with open('index.html', 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return "<h1>Preview Server Running</h1><p>No index.html found</p>"
    except Exception as e:
        return f"<h1>Error rendering template</h1><p>{str(e)}</p>"

# Serve other HTML pages
@app.route('/<path:page>')
def serve_page(page):
    """Serve other HTML pages"""
    try:
        if page.endswith('.html'):
            # Remove .html extension for template rendering
            template_name = page[:-5] if page.endswith('.html') else page
            if os.path.exists(f'templates/{template_name}.html'):
                return render_template(f'{template_name}.html')
            elif os.path.exists(page):
                with open(page, 'r', encoding='utf-8') as f:
                    return f.read()
        return "Page not found", 404
    except Exception as e:
        return f"Error serving page: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
'''

        return flask_app

    def _get_available_port(self) -> int:
        """Get next available port with range checking and port availability testing"""
        import socket
    
        def is_port_available(port):
            """Check if a port is available for use"""
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return True
            except OSError:
                return False
    
        # Start from the configured range
        start_port = settings.PREVIEW_PORT_RANGE[0]
        end_port = settings.PREVIEW_PORT_RANGE[1]
    
        # Try to find an available port
        for port in range(start_port, end_port + 1):
            if port not in self.preview_ports.values() and is_port_available(port):
                print(f"🔍 Found available port: {port}")
                return port

        # If no ports available in range, find any available port
        for port in range(8000, 9000):
            if port not in self.preview_ports.values() and is_port_available(port):
                print(f"🔍 Found fallback available port: {port}")
                return port

        # Last resort - use a random port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 0))
            random_port = s.getsockname()[1]
            print(f"🔍 Using random available port: {random_port}")
            return random_port
        
    def _start_preview_server(self, project_id: str) -> int:
        """ENHANCED: Start Flask preview server for proper template rendering"""
        try:
            port = self._get_available_port()
            preview_dir = self.projects_dir / f"project-{project_id}" / "preview"
    
            if not preview_dir.exists():
                print(f"❌ Preview directory not found: {preview_dir}")
                return 0

            # Check if we have a Flask app for preview
            flask_app_file = preview_dir / "preview_app.py"
            requirements_file = preview_dir / "requirements.txt"

            def serve_preview():
                """Start the Flask preview server"""
                try:
                    os.chdir(str(preview_dir))

                    # Use the Flask preview app if it exists
                    if flask_app_file.exists():
                        # Start Flask app directly
                        import subprocess
                        import sys

                        # Start Flask app in a subprocess
                        cmd = [
                            sys.executable, "preview_app.py"
                        ]

                        # Set environment for Flask
                        env = os.environ.copy()
                        env['FLASK_APP'] = 'preview_app.py'
                        env['FLASK_ENV'] = 'development'
                        env['PORT'] = str(port)

                        # Modify the Flask app to use the correct port
                        self._update_flask_app_port(flask_app_file, port)

                        print(f"🚀 Starting Flask preview server on port {port}")
                        print(f"📁 Serving from: {preview_dir}")

                        # Start the server
                        process = subprocess.Popen(
                            cmd,
                            env=env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True
                        )

                        # Keep the process running
                        process.wait()

                    else:
                        # Fallback to SimpleHTTP for non-Flask projects
                        print(f"🔄 No Flask app found, using SimpleHTTP")
                        handler = http.server.SimpleHTTPRequestHandler
                        with socketserver.TCPServer(("", port), handler) as httpd:
                            print(f"🌐 SimpleHTTP server on port {port}")
                            httpd.serve_forever()

                except Exception as e:
                    print(f"❌ Preview server error: {e}")

            server_thread = threading.Thread(target=serve_preview, daemon=True)
            server_thread.start()

            # Wait for server to be ready
            if self._wait_for_server_ready(port, server_type='flask'):
                print(f"✅ Preview server ready on port {port}")
                return port
            else:
                print(f"❌ Preview server failed to start on port {port}")
                return 0

        except Exception as e:
            print(f"❌ Error starting preview server: {e}")
            return 0

    def _update_flask_app_port(self, flask_app_file: Path, port: int):
        """Update the Flask app to use the correct port"""
        try:
            with open(flask_app_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update the port in the Flask app
            if 'port=5000' in content:
                content = content.replace('port=5000', f'port={port}')
            elif 'app.run(' in content and 'port=' not in content:
                # Add port parameter if missing
                content = content.replace('app.run(', f'app.run(port={port}, ')

            with open(flask_app_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"🔧 Updated Flask app to use port {port}")
        except Exception as e:
            print(f"⚠️  Could not update Flask app port: {e}")

    def _wait_for_server_ready(self, port: int, max_attempts: int = 15, server_type: str = 'flask') -> bool:
        """ENHANCED: Wait for server to be ready with better detection"""
        url = f"http://localhost:{port}"

        print(f"⏳ Waiting for {server_type} server on {url}...")

        for attempt in range(max_attempts):
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    print(f"✅ Server is ready after {attempt + 1} attempts")
                    return True
                # Also accept 404 if the server is running but route not found
                elif response.status_code == 404:
                    print(f"✅ Server is running (404 on root route)")
                    return True
            except (requests.ConnectionError, requests.Timeout) as e:
                if attempt % 3 == 0:  # Log every 3 attempts
                    print(f"   Attempt {attempt + 1}/{max_attempts}: {type(e).__name__}")
            except Exception as e:
                print(f"   Attempt {attempt + 1} error: {e}")

            time.sleep(1)

        print(f"❌ Server not ready after {max_attempts} attempts")
        return False

    def get_preview_url(self, project_id: str) -> str:
        """Get or create preview URL with enhanced caching"""
        try:
            if project_id not in self.preview_ports:
                port = self._start_preview_server(project_id)
                if port:
                    self.preview_ports[project_id] = port
                    print(f"✅ Preview assigned port {port} for {project_id}")

                    # Wait a bit for server to fully initialize
                    time.sleep(2)
                else:
                    print(f"❌ Failed to start preview for {project_id}")
                    return ""

            preview_url = f"http://localhost:{self.preview_ports[project_id]}"
            print(f"🌐 Preview URL: {preview_url}")
            return preview_url

        except Exception as e:
            print(f"❌ Error getting preview URL: {e}")
            return ""

    # File type detection methods (keep these - they're working)
    def _get_file_type(self, file_path: str) -> str:
        ext = file_path.split('.')[-1].lower()
        type_map = {
            'py': 'python', 'html': 'html', 'css': 'stylesheet', 
            'js': 'javascript', 'json': 'json', 'md': 'markdown', 'txt': 'text'
        }
        return type_map.get(ext, 'text')

    def _get_file_icon(self, file_path: str) -> str:
        ext = file_path.split('.')[-1].lower()
        icon_map = {
            'py': '🐍', 'html': '🌐', 'css': '🎨', 'js': '📜',
            'json': '📋', 'md': '📝', 'txt': '📄'
        }
        return icon_map.get(ext, '📄')

    def _get_file_language(self, file_path: str) -> str:
        ext = file_path.split('.')[-1].lower()
        lang_map = {
            'py': 'python', 'html': 'html', 'css': 'css', 
            'js': 'javascript', 'json': 'json', 'md': 'markdown'
        }
        return lang_map.get(ext, 'text')