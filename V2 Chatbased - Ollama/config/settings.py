"""
Zero Cost Configuration - Ollama Only
"""

import os
from pathlib import Path

# Project Paths
PROJECTS_DIR = Path("projects")
TEMPLATES_DIR = PROJECTS_DIR / "templates"

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2:1b"  # Free, good for code generation

# Alternative models (all free):
# - "llama3.1:8b" - Balanced quality/speed
# - "mistral:7b" - Strong general purpose
# - "phi3:mini" - Very fast, smaller

# Agent Settings
MAX_RESPONSE_TOKENS = 600
TEMPERATURE = 0.7

# Web Server Settings
WEB_UI_PORT = 3000
WS_SERVER_PORT = 8765
PREVIEW_PORT_RANGE = (3001, 3010)  # Ports for project previews

# Create directories
PROJECTS_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

print("✅ Zero Cost Config Loaded - Using Ollama")