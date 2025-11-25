# AIDE: AI Development Ensemble 🚀

A multi-agent system that collaboratively builds complete web applications by specializing in different technical domains. Powered by Ollama for local AI processing.

![AIDE Architecture](https://img.shields.io/badge/Architecture-Multi--Agent-blue)
![Ollama Powered](https://img.shields.io/badge/Powered%20By-Ollama-orange)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Vue.js](https://img.shields.io/badge/Frontend-Vue.js-brightgreen)

## 🌟 What is AIDE?

AIDE (AI Development Ensemble) is an innovative framework where specialized AI agents work together to understand your requirements and generate complete, functional web applications. Each agent focuses on a specific domain, ensuring comprehensive coverage from user experience to deployment.

## 🏗️ Architecture Overview

AIDE-V2-DEMO/
├── 🎯 Agent Server (Backend)
│ ├── Orchestrator - Routes messages between agents
│ ├── Requirements Evolver - Understands project goals
│ ├── UX Architect - Designs user experience flows
│ ├── UI Designer - Creates visual design specifications
│ ├── Frontend Engineer - Handles technical implementation
│ ├── Data Architect - Designs data structures
│ ├── API Designer - Creates backend APIs
│ └── DevOps - Plans deployment strategies
├── 🌐 Web UI (Frontend)
│ ├── Vue.js 3 with Vite
│ ├── Real-time chat interface
│ ├── Live code preview
│ └── File explorer
└── 🔧 Project Builder
├── Generates complete Flask applications
├── Manages preview servers
└── Validates and integrates generated code

## 🎯 Multi-Agent Specialization

| Agent | Role | Focus Area |
|-------|------|------------|
| **Requirements Evolver** | 📋 Project Scoping | Understanding goals, features, user needs |
| **UX Architect** | 🎯 User Experience | Navigation flows, information architecture |
| **UI Designer** | 🎨 Visual Design | Colors, typography, layout, styling |
| **Frontend Engineer** | ⚡ Technical Implementation | JavaScript, frameworks, interactivity |
| **Data Architect** | 💾 Data Design | Database schemas, storage solutions |
| **API Designer** | 🔗 Backend API | REST endpoints, authentication, logic |
| **DevOps** | 🚀 Deployment | Hosting, servers, deployment pipelines |

## ✨ Key Features

### 🤖 Intelligent Agent Coordination
- **Context-Aware Routing**: Agents maintain conversation context and project state
- **Progressive Refinement**: Requirements evolve through structured dialogue
- **Manual Code Generation**: Explicit control over when to generate code

### 🎨 Modern Web Stack
- **Flask Backend**: Python-based web framework
- **Vue.js 3 Frontend**: Reactive, modern user interface
- **Real-time WebSockets**: Live communication between frontend and agents
- **Template Rendering**: Proper Flask template support

### 🔧 Smart Project Generation
- **File Structure Planning**: Intelligent project scaffolding
- **Context-Aware Code Generation**: Files reference each other properly
- **Validation & Integration**: Ensures working, integrated code
- **Live Preview**: Instant project preview with hot reload

### 🛡️ Ollama Integration
- **Local Processing**: No API quotas or external dependencies
- **Privacy Focused**: All AI processing happens locally
- **Configurable Models**: Use any Ollama-supported model
- **Error Resilience**: Graceful handling of model responses

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Ollama (with at least one model installed)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/AIDE-AI-Development-Ensemble.git
   cd AIDE-AI-Development-Ensemble
Backend Setup

bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
Frontend Setup

bash
cd web-ui
npm install
cd ..
Ollama Setup

bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/

# Pull a model (example with llama2)
ollama pull llama2
Configuration

bash
# Edit config/settings.py with your preferred model
OLLAMA_MODEL = "llama2"  # or your preferred model
Running AIDE
Start the Backend Server

bash
python run.py
Start the Frontend (in a new terminal)

bash
cd web-ui
npm run dev
Access AIDE

Open http://localhost:3000 (or your Vite dev server URL)

Start chatting with the AI ensemble!

🎮 How to Use
1. Create a New Project
Click "New Project" and give it a name

The Requirements Evolver agent will greet you and start understanding your needs

2. Collaborative Dialogue
Describe what you want to build

Agents will automatically switch based on context:

Requirements: "I want a BMI calculator app"

UX: "How should users navigate through it?"

UI: "What colors and styling do you prefer?"

Technical: "Any specific technical requirements?"

3. Generate Code
When you have sufficient requirements, the Generate button activates

Click to generate complete, working code

View generated files in the file explorer

See live preview of your application

4. Iterate and Refine
Continue chatting to refine features

Regenerate code as needed

All project state is preserved

🔧 Configuration
Model Settings (config/settings.py)
python
# Ollama Configuration
OLLAMA_MODEL = "llama2"  # or "mistral", "codellama", etc.
TEMPERATURE = 0.7
MAX_RESPONSE_TOKENS = 2000

# Server Configuration
WS_SERVER_PORT = 8765
PREVIEW_PORT_RANGE = (5000, 6000)
Supported Ollama Models
llama2, llama2:13b, llama2:70b

mistral, mixtral

codellama (recommended for code generation)

Any other Ollama-supported model

📁 Project Structure
text
AIDE-AI-Development-Ensemble/
├── run.py                          # Main application entry point
├── config/
│   └── settings.py                 # Configuration settings
├── agent-server/
│   ├── main.py                     # WebSocket server
│   ├── agents/
│   │   ├── orchestrator.py         # Agent coordination
│   │   └── integration_agent.py    # Code generation
│   ├── services/
│   │   └── project_builder.py      # Project building logic
│   └── storage/
│       └── local_storage.py        # Project data storage
└── web-ui/
    ├── src/
    │   ├── App.vue                 # Main Vue component
    │   ├── stores/
    │   │   └── project-store.js    # State management
    │   ├── services/
    │   │   └── agent-service.js    # WebSocket communication
    │   └── components/
    │       ├── ChatInterface.vue   # Chat UI
    │       ├── AgentStatus.vue     # Agent indicators
    │       ├── LivePreview.vue     # Project preview
    │       └── FileExplorer.vue    # File browser
    └── package.json
    
🎯 Use Cases
🏥 Healthcare Applications
Patient symptom checkers

Medication trackers

Health monitoring dashboards

📊 Business Tools
CRM systems

Inventory management

Reporting dashboards

🎓 Educational Platforms
Quiz applications

Learning management systems

Interactive tutorials

🛍️ E-commerce
Product catalogs

Shopping carts

Order management

🔄 Development Workflow
Requirement Gathering: Multiple agents extract comprehensive requirements

Design Phase: UX and UI agents create user experience and visual design

Technical Specification: Frontend, Data, and API agents define implementation

Code Generation: Integration agent generates working Flask application

Preview & Iteration: Live preview allows real-time refinement

🛠️ Technical Details
Agent Communication
WebSocket Protocol: Real-time bidirectional communication

Message Types: user_message, generate_code, get_preview, etc.

State Management: Project state persists across sessions

Code Generation
Flask Applications: Python backend with Jinja2 templates

Vanilla JavaScript: Framework-free frontend code

Responsive CSS: Mobile-first styling

RESTful APIs: Clean backend architecture

Validation & Safety
Content Validation: Ensures generated code is syntactically valid

Framework Restrictions: Prevents unwanted dependencies

Error Handling: Graceful degradation on generation failures

🤝 Contributing
We welcome contributions! Please see our Contributing Guidelines for details.

Areas for Contribution
New agent specializations

Additional framework support

Enhanced validation systems

UI/UX improvements

Documentation

🙏 Acknowledgments
Ollama for providing local AI inference capabilities

Vue.js and Flask communities for excellent frameworks

The AI/ML community for continuous inspiration

🐛 Troubleshooting
Common Issues
Ollama Connection Issues

# Check if Ollama is running
ollama list

# Restart Ollama service
ollama serve
Port Conflicts

# Check available ports
lsof -i :8765  # WebSocket port
lsof -i :3000  # Frontend port
Model Performance

Use larger models (13b+) for better code generation

Ensure sufficient RAM for model loading

Consider using codellama for programming tasks

📞 Support

📧 Email: narendren2006@gmail.com

💬 Discussions: GitHub Discussions

🐛 Issues: GitHub Issues

<div align="center">
Built with ❤️ using Ollama, Flask, and Vue.js

Empowering developers to build better applications, faster.

🏠 Home • 📖 Docs • 🚀 Getting Started • 🤖 Agents

</div>
