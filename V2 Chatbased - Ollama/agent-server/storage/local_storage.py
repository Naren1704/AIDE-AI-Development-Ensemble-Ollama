"""
Local JSON-based storage for projects and conversations - FIXED FOR WINDOWS
"""
import time
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from config import settings

class LocalStorage:
    def __init__(self):
        current_dir = Path(__file__).parent.parent.parent  # Goes up to project root
        self.projects_dir = current_dir / "projects"
        
        # Ensure projects directory exists
        self.projects_dir.mkdir(exist_ok=True)
        print(f"📁 Projects directory: {self.projects_dir.absolute()}")
        
    def create_project(self, name: str) -> str:
        """Create a new project and return project ID"""
        project_id = str(uuid.uuid4())[:8]  # Short ID for URLs
    
        project_data = {
            'id': project_id,
            'name': name,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'status': 'active',
            'requirements': {},
            'messages': [],
            'generated_files': [],
            'active_agent': 'requirements_evolver'
        }
    
        # Save project file
        project_file = self.projects_dir / f"project-{project_id}.json"
        try:
            print(f"💾 Creating project file: {project_file}")
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2)
            # 🚨 REMOVE the broken file sync - the file is already closed here
            print(f"✅ Project file created: {project_file.exists()}")
        except Exception as e:
            print(f"❌ Failed to create project file: {str(e)}")
            raise Exception(f"Failed to create project file: {str(e)}")
    
        # Create project directory
        project_dir = self.projects_dir / f"project-{project_id}"
        try:
            print(f"📁 Creating project directory: {project_dir}")
            project_dir.mkdir(parents=True, exist_ok=True)
            (project_dir / "src").mkdir(exist_ok=True)
            (project_dir / "preview").mkdir(exist_ok=True)
            print(f"✅ Project directory created: {project_dir.exists()}")
        except Exception as e:
            print(f"❌ Failed to create project directories: {str(e)}")
            raise Exception(f"Failed to create project directories: {str(e)}")
    
        print(f"🎉 Created project: {name} ({project_id})")
        time.sleep(0.1)
        return project_id
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project data by ID"""
        project_file = self.projects_dir / f"project-{project_id}.json"
        
        if not project_file.exists():
            raise FileNotFoundError(f"Project {project_id} not found at {project_file}")
            
        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to read project file: {str(e)}")
    
    def update_project(self, project_id: str, updates: Dict[str, Any]):
        """Update project data"""
        project_data = self.get_project(project_id)
        project_data.update(updates)
        project_data['updated_at'] = datetime.now().isoformat()
        
        project_file = self.projects_dir / f"project-{project_id}.json"
        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to update project file: {str(e)}")
    
    def add_message(self, project_id: str, role: str, message: str):
        """Add message to project conversation"""
        project_data = self.get_project(project_id)
        
        message_data = {
            'role': role,  # 'user' or 'agent'
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'agent': project_data.get('active_agent', 'orchestrator')
        }
        
        project_data['messages'].append(message_data)
        project_data['updated_at'] = datetime.now().isoformat()
        
        project_file = self.projects_dir / f"project-{project_id}.json"
        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to save message: {str(e)}")
    
    def update_requirements(self, project_id: str, agent_name: str, requirements: Dict[str, Any]):
        """Update requirements from specific agent"""
        project_data = self.get_project(project_id)
        
        if 'requirements' not in project_data:
            project_data['requirements'] = {}
            
        project_data['requirements'][agent_name] = requirements
        project_data['updated_at'] = datetime.now().isoformat()
        
        project_file = self.projects_dir / f"project-{project_id}.json"
        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to update requirements: {str(e)}")
    
    def set_active_agent(self, project_id: str, agent_name: str):
        """Set the currently active agent"""
        self.update_project(project_id, {'active_agent': agent_name})
    
    def add_generated_file(self, project_id: str, file_path: str, content: str):
        """Track generated files"""
        project_data = self.get_project(project_id)
        
        file_data = {
            'path': file_path,
            'content': content[:500] + "..." if len(content) > 500 else content,  # Store preview
            'generated_at': datetime.now().isoformat(),
            'size': len(content)
        }
        
        project_data['generated_files'].append(file_data)
        project_data['updated_at'] = datetime.now().isoformat()
        
        project_file = self.projects_dir / f"project-{project_id}.json"
        try:
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2)
        except Exception as e:
            raise Exception(f"Failed to track generated file: {str(e)}")
    
    def get_conversation_history(self, project_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        project_data = self.get_project(project_id)
        return project_data['messages'][-limit:]
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        projects = []
        try:
            for project_file in self.projects_dir.glob("project-*.json"):
                try:
                    with open(project_file, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)
                        projects.append({
                            'id': project_data['id'],
                            'name': project_data['name'],
                            'created_at': project_data['created_at'],
                            'status': project_data['status'],
                            'message_count': len(project_data['messages'])
                        })
                except Exception as e:
                    print(f"⚠️  Skipping corrupt project file {project_file}: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ Error listing projects: {e}")
        
        return sorted(projects, key=lambda x: x['created_at'], reverse=True)
    
    def cleanup_project(self, project_id: str):
        """Clean up a project that failed to create properly"""
        project_file = self.projects_dir / f"project-{project_id}.json"
        project_dir = self.projects_dir / f"project-{project_id}"
        
        try:
            if project_file.exists():
                project_file.unlink()
            if project_dir.exists():
                import shutil
                shutil.rmtree(project_dir)
            print(f"🧹 Cleaned up failed project: {project_id}")
        except Exception as e:
            print(f"⚠️  Failed to cleanup project {project_id}: {e}")