"""
WebSocket Server for Agent Communication - FIXED VERSION
Manual code generation via Generate button only
"""

import asyncio
import websockets
import json
import logging
from pathlib import Path
import sys

# Add agent modules to path
sys.path.append(str(Path(__file__).parent))

from agents.orchestrator import Orchestrator
from services.project_builder import ProjectBuilder
from storage.local_storage import LocalStorage
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIDEServer:
    def __init__(self):
        self.orchestrator = Orchestrator()
        self.project_builder = ProjectBuilder()
        self.storage = LocalStorage()
        self.active_connections = set()
    
    async def handle_connection(self, websocket):
        """Handle new WebSocket connection - FIXED SIGNATURE"""
        self.active_connections.add(websocket)
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"🟢 Client connected: {client_info}. Total: {len(self.active_connections)}")
        
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔴 Client disconnected: {client_info}")
        except Exception as e:
            logger.error(f"❌ Error with client {client_info}: {str(e)}")
        finally:
            self.active_connections.remove(websocket)
            logger.info(f"🟡 Client removed: {client_info}. Remaining: {len(self.active_connections)}")
    
    async def process_message(self, websocket, message):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)
            await self.process_request(websocket, data)
        except json.JSONDecodeError:
            await self.send_error(websocket, "Invalid JSON format")
        except Exception as e:
            logger.error(f"❌ Message processing error: {str(e)}")
            await self.send_error(websocket, f"Processing error: {str(e)}")
    
    async def process_request(self, websocket, data):
        """Process different types of requests"""
        message_type = data.get('type', 'message')
        
        if message_type == 'new_project':
            await self.handle_new_project(websocket, data)
        elif message_type == 'user_message':
            await self.handle_user_message(websocket, data)
        elif message_type == 'get_preview':
            await self.handle_get_preview(websocket, data)
        elif message_type == 'check_generation_status':
            await self.handle_check_generation_status(websocket, data)
        elif message_type == 'generate_code':
            await self.handle_generate_code(websocket, data)
        elif message_type == 'ping':
            await self.send_pong(websocket)
        else:
            await self.send_error(websocket, f"Unknown message type: {message_type}")
    
    async def handle_new_project(self, websocket, data):
        """Start a new project - SIMPLIFIED FIX"""
        project_id = None
        try:
            project_name = data.get('project_name', 'New Project')
            project_id = self.storage.create_project(project_name)
        
            response = {
                'type': 'project_created',
                'project_id': project_id,
                'project_name': project_name
            }
            await websocket.send(json.dumps(response))
        
            # Send welcome message after project creation
            welcome_msg = await self.orchestrator.start_conversation(project_id)
            await self.send_agent_response(websocket, welcome_msg, 'requirements_evolver')
        
        except Exception as e:
            logger.error(f"❌ New project error: {str(e)}")
        
            # Clean up failed project
            if project_id:
                self.storage.cleanup_project(project_id)
            
            await self.send_error(websocket, f"Failed to create project: {str(e)}")  
                          
    async def handle_user_message(self, websocket, data):
        """Process user message through agents - NO AUTO CODE GENERATION"""
        try:
            project_id = data.get('project_id')
            user_message = data.get('message', '')
            
            if not project_id:
                await self.send_error(websocket, "No project ID provided")
                return
            
            # Store user message immediately
            self.storage.add_message(project_id, 'user', user_message)
            
            # Get CURRENT project data BEFORE processing
            current_project_data = self.storage.get_project(project_id)
            
            # Route to appropriate agent - this now handles requirements extraction internally
            agent_response = await self.orchestrator.route_message(project_id, user_message)
            
            # Store agent response
            self.storage.add_message(project_id, 'agent', agent_response['message'])
            
            # Send response to frontend
            await self.send_agent_response(websocket, agent_response['message'], agent_response['agent'])
            
            # 🚨 CRITICAL CHANGE: NEVER auto-generate code from chat messages
            # Code generation only happens via explicit Generate button
            logger.info(f"💬 Chat message processed - no auto-generation for {project_id}")
            
            # Send generation status update after processing message
            generation_status = await self.orchestrator.can_generate_code(project_id)
            await self.send_generation_status(websocket, project_id, generation_status)
                
        except Exception as e:
            logger.error(f"❌ User message error: {str(e)}")
            await self.send_error(websocket, f"Failed to process message: {str(e)}")
    
    async def handle_check_generation_status(self, websocket, data):
        """Check if we can generate code based on collected requirements"""
        try:
            project_id = data.get('project_id')
            
            if not project_id:
                await self.send_error(websocket, "No project ID provided")
                return
            
            generation_status = await self.orchestrator.can_generate_code(project_id)
            await self.send_generation_status(websocket, project_id, generation_status)
            
        except Exception as e:
            logger.error(f"❌ Generation status check error: {str(e)}")
            await self.send_error(websocket, f"Failed to check generation status: {str(e)}")
    
    async def handle_generate_code(self, websocket, data):
        """Generate code for project - ONLY via explicit Generate button"""
        try:
            project_id = data.get('project_id')
            
            if not project_id:
                await self.send_error(websocket, "No project ID provided")
                return
            
            # First check if we can generate code
            generation_status = await self.orchestrator.can_generate_code(project_id)
            
            if not generation_status['can_generate']:
                # Send error if requirements are insufficient
                error_response = {
                    'type': 'generation_failed',
                    'project_id': project_id,
                    'error': 'Insufficient requirements',
                    'message': generation_status['message'],
                    'status': 'failed'
                }
                await websocket.send(json.dumps(error_response))
                logger.warning(f"⚠️  Code generation blocked for {project_id}: {generation_status['message']}")
                return
            
            # If we can generate, proceed with code generation
            logger.info(f"🎯 Manual code generation triggered for project {project_id}")
            await self.generate_project_code(websocket, project_id)
            
        except Exception as e:
            logger.error(f"❌ Generate code error for {project_id}: {str(e)}")
            await self.send_error(websocket, f"Failed to generate code: {str(e)}")
    
    async def handle_get_preview(self, websocket, data):
        """Get project preview URL"""
        try:
            project_id = data.get('project_id')
            preview_url = self.project_builder.get_preview_url(project_id)
            
            response = {
                'type': 'preview_url',
                'preview_url': preview_url
            }
            await websocket.send(json.dumps(response))
        except Exception as e:
            logger.error(f"❌ Preview error: {str(e)}")
            await self.send_error(websocket, f"Failed to get preview: {str(e)}")
    
    async def generate_project_code(self, websocket, project_id):
        """Generate code for project with proper error handling and progress updates"""
        try:
            # Get FRESH project data with updated requirements
            project_data = self.storage.get_project(project_id)
            
            # Send generation started message
            await self.send_generation_started(websocket, project_id)
            
            # Generate project files
            generated_files = await self.project_builder.generate_project(project_data)
            
            # Store generated files
            for file_data in generated_files:
                self.storage.add_generated_file(project_id, file_data['path'], file_data['content'])
            
            # Get preview URL
            preview_url = self.project_builder.get_preview_url(project_id)
        
            response = {
                'type': 'code_generated',
                'files': generated_files,
                'preview_url': preview_url,
                'project_id': project_id,
                'file_count': len(generated_files),
                'total_size': sum(f.get('size', 0) for f in generated_files),
                'status': 'success'
            }
        
            await websocket.send(json.dumps(response))
            logger.info(f"✅ Code generated for project {project_id}: {len(generated_files)} files")
        
        except Exception as e:
            logger.error(f"❌ Code generation error for {project_id}: {str(e)}")
            
            # Send detailed error information
            error_response = {
                'type': 'code_generation_error',
                'project_id': project_id,
                'error': str(e),
                'status': 'failed'
            }
            await websocket.send(json.dumps(error_response))
            
            # Also send as regular error for compatibility
            await self.send_error(websocket, f"Failed to generate code: {str(e)}")
    
    async def send_generation_status(self, websocket, project_id, status):
        """Send generation status to frontend"""
        response = {
            'type': 'generation_status',
            'project_id': project_id,
            'can_generate': status['can_generate'],
            'substantial_agents': status['substantial_agents'],
            'agent_contributions': status['agent_contributions'],
            'has_minimal_requirements': status['has_minimal_requirements'],
            'message': status['message'],
            'timestamp': asyncio.get_event_loop().time()
        }
        await websocket.send(json.dumps(response))
    
    async def send_generation_started(self, websocket, project_id):
        """Notify frontend that code generation has started"""
        response = {
            'type': 'generation_started',
            'project_id': project_id,
            'message': 'Starting code generation...'
        }
        await websocket.send(json.dumps(response))
    
    async def send_agent_response(self, websocket, message, agent_name):
        """Send agent response to frontend"""
        response = {
            'type': 'agent_response',
            'message': message,
            'agent': agent_name,
            'timestamp': asyncio.get_event_loop().time()
        }
        await websocket.send(json.dumps(response))
    
    async def send_error(self, websocket, error_msg):
        """Send error message"""
        response = {
            'type': 'error',
            'message': error_msg,
            'timestamp': asyncio.get_event_loop().time()
        }
        await websocket.send(json.dumps(response))
    
    async def send_pong(self, websocket):
        """Respond to ping"""
        response = {
            'type': 'pong',
            'message': 'pong'
        }
        await websocket.send(json.dumps(response))

    async def run_server(self):
        """Start the WebSocket server"""
        logger.info(f"🚀 Starting AIDE Server on port {settings.WS_SERVER_PORT}")
        async with websockets.serve(self.handle_connection, "localhost", settings.WS_SERVER_PORT):
            logger.info(f"✅ AIDE Server running on ws://localhost:{settings.WS_SERVER_PORT}")
            await asyncio.Future()  # run forever

if __name__ == "__main__":
    server = AIDEServer()
    asyncio.run(server.run_server())
