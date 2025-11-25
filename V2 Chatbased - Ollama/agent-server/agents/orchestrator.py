"""
Main orchestrator that routes messages to appropriate agents
REFINED VERSION: Better requirement collection, fixed generation logic
"""

import asyncio
from typing import Dict, Any
import ollama
import sys
from pathlib import Path
import re
# Add the root directory to Python path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from config import settings
from storage.local_storage import LocalStorage

class Orchestrator:
    def __init__(self):
        self.storage = LocalStorage()
        self.agent_chain = [
            'requirements_evolver',
            'ux_architect', 
            'ui_designer',
            'frontend_engineer',
            'data_architect',
            'api_designer',
            'devops'
        ]
        self.agent_progress = {}  # Track which agents have contributed
    
    async def start_conversation(self, project_id: str) -> str:
        """Enhanced welcome with progress tracking"""
        welcome_message = """🤖 Welcome to AIDE V2! I'm your AI Development Ensemble.

I'll help you build a complete web application by gathering requirements across different domains:

• **Requirements Evolution** - Understanding your goals
• **UX Architecture** - User experience and navigation  
• **UI Design** - Visual design and styling
• **Frontend Engineering** - Technical implementation
• **Data Architecture** - Database and storage
• **API Design** - Backend functionality
• **DevOps** - Deployment and hosting

Let's start with the basics: What kind of application would you like to build?"""
        
        self.storage.set_active_agent(project_id, 'requirements_evolver')
        self.agent_progress[project_id] = set()  # Initialize progress tracking
        return welcome_message
    
    async def route_message(self, project_id: str, user_message: str) -> Dict[str, Any]:
        """REFINED: Route messages - NO AUTO CODE GENERATION"""
        project_data = self.storage.get_project(project_id)
        current_agent = project_data.get('active_agent', 'requirements_evolver')
        
        # Enhanced agent switching logic
        next_agent = self._determine_next_agent_enhanced(current_agent, user_message, project_data)
        
        if next_agent != current_agent:
            self.storage.set_active_agent(project_id, next_agent)
            current_agent = next_agent
            print(f"🔄 Switched to agent: {current_agent}")
        
        # Get agent response with enhanced context
        agent_response = await self._call_agent_enhanced(current_agent, user_message, project_data)
        
        # Extract requirements (but don't auto-generate code)
        requirements_updated = self._extract_requirements_enhanced(project_id, current_agent, agent_response, user_message)
        
        # Track agent progress
        if project_id in self.agent_progress:
            self.agent_progress[project_id].add(current_agent)
        
        print(f"📝 Requirements updated: {requirements_updated}")
        
        # 🚨 CRITICAL: NEVER auto-generate code from chat messages
        # Code generation will only happen via explicit Generate button
        should_generate = False
        
        return {
            'message': agent_response,
            'agent': current_agent,
            'should_generate': should_generate  # Always False for chat messages
        }
    
    async def can_generate_code(self, project_id: str) -> Dict[str, Any]:
        """Check if we have enough requirements to generate code"""
        project_data = self.storage.get_project(project_id)
        requirements = project_data.get('requirements', {})
        
        # Count substantial contributions
        substantial_agents = 0
        agent_contributions = []
        
        for agent_name, req_data in requirements.items():
            if req_data and req_data.get('has_substance', False):
                substantial_agents += 1
                agent_contributions.append(agent_name)
        
        # Define minimum requirements for code generation
        has_minimal_requirements = self._has_minimal_requirements(project_data)
        
        status = {
            'can_generate': has_minimal_requirements,
            'substantial_agents': substantial_agents,
            'agent_contributions': agent_contributions,
            'has_minimal_requirements': has_minimal_requirements,
            'message': self._get_generation_status_message(has_minimal_requirements, substantial_agents)
        }
        
        print(f"🔍 Code generation check: {status}")
        return status
    
    def _has_minimal_requirements(self, project_data: Dict[str, Any]) -> bool:
        """🚨 CRITICAL FIX: Check if we have basic requirements to generate meaningful code"""
        requirements = project_data.get('requirements', {})
        
        # Count substantial agents
        substantial_agents = sum(
            1 for agent_data in requirements.values() 
            if agent_data and agent_data.get('has_substance', False)
        )
        
        # 🎯 SIMPLE & RELIABLE RULES:
        # 1. At least 2 agents with substantial contributions, OR
        # 2. Requirements evolver + any other agent, OR  
        # 3. Any 3 agents regardless of type
        
        has_requirements_evolver = (
            'requirements_evolver' in requirements and 
            requirements['requirements_evolver'].get('has_substance', False)
        )
        
        # 🚨 FIXED: Actually return the result
        return (
            substantial_agents >= 2 or  # Any 2 substantial agents
            (has_requirements_evolver and substantial_agents >= 1) or  # Requirements + any other
            substantial_agents >= 3  # Any 3 agents
        )
    
    def _get_generation_status_message(self, can_generate: bool, substantial_agents: int) -> str:
        """Get user-friendly message about generation readiness"""
        if can_generate:
            return f"Ready to generate! Collected requirements from {substantial_agents} agents."
        elif substantial_agents == 0:
            return "Please describe your project requirements first."
        elif substantial_agents == 1:
            return "Getting there! A bit more detail about design or functionality would help."
        else:
            return "Making progress! A few more details about your preferences would be great."
    
    def _determine_next_agent_enhanced(self, current_agent: str, user_message: str, project_data: Dict[str, Any]) -> str:
        """Enhanced agent switching with context awareness"""
        message_lower = user_message.lower()
        requirements = project_data.get('requirements', {})
    
        # 🚨 CRITICAL FIX: Check for explicit approval to force agent switch
        approval_keywords = ['approved', 'perfect', 'looks good', 'proceed', 'move forward', 'next phase', 'next agent', 'switch to']
        if any(keyword in message_lower for keyword in approval_keywords):
            if current_agent == 'ui_designer':
                print(f"🎯 Explicit approval detected: forcing switch from UI Designer")
                return 'frontend_engineer'
            elif current_agent == 'requirements_evolver':
                return 'ux_architect'
            elif current_agent == 'ux_architect':
                return 'frontend_engineer'
        # Add more approval-based transitions as needed
    
        # Check for explicit agent mentions with priority
        agent_keywords = {
            'ui_designer': ['change design', 'change color', 'ui design', 'ui'],
            'ux_architect': ['navigate', 'user flow', 'ux', 'experience', 'usability', 'interface'],
            'data_architect': ['database', 'data', 'store', 'save', 'storage', 'persist'],
            'api_designer': ['api', 'backend', 'server', 'endpoint', 'rest', 'json'],
            'frontend_engineer': ['javascript', 'react', 'vue', 'frontend', 'client', 'browser', 'technical', 'implementation'],
            'devops': ['deploy', 'host', 'server', 'domain', 'production', 'cloud']
        }
    
        for agent_name, keywords in agent_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                print(f"🎯 Keyword match: switching to {agent_name}")
                return agent_name
    
        # Progress-based switching: Move to next agent in chain if current has contributed
        if current_agent in self.agent_chain:
            current_index = self.agent_chain.index(current_agent)
        
            # Check if current agent has made substantial contribution
            current_has_contributed = (
                current_agent in requirements and 
                requirements[current_agent].get('has_substance', False)
            )
        
            # 🚨 ENHANCEMENT: Also switch if we have multiple messages with this agent
            message_count = len([msg for msg in project_data.get('messages', []) 
                           if msg.get('agent') == current_agent])
        
            if (current_has_contributed or message_count >= 2) and current_index < len(self.agent_chain) - 1:
                next_agent = self.agent_chain[current_index + 1]
                print(f"📈 Progress-based switch: {current_agent} -> {next_agent} (contributions: {current_has_contributed}, messages: {message_count})")
                return next_agent
    
        # Stay with current agent if no better option
        return current_agent
    
    async def _call_agent_enhanced(self, agent_name: str, user_message: str, project_data: Dict[str, Any]) -> str:
        """Enhanced agent calling with better context"""
        context = self._build_enhanced_context(project_data, agent_name)
        
        agent_methods = {
            'requirements_evolver': self._requirements_evolver_enhanced,
            'ux_architect': self._ux_architect_enhanced,
            'ui_designer': self._ui_designer_enhanced,
            'frontend_engineer': self._frontend_engineer_enhanced,
            'data_architect': self._data_architect_enhanced,
            'api_designer': self._api_designer_enhanced,
            'devops': self._devops_enhanced
        }
        
        if agent_name in agent_methods:
            return await agent_methods[agent_name](user_message, context)
        else:
            return "I'm not sure how to help with that. Could you clarify?"
    
    def _build_enhanced_context(self, project_data: Dict[str, Any], agent_name: str) -> str:
        """Build comprehensive context for agents"""
        requirements = project_data.get('requirements', {})
        recent_messages = project_data.get('messages', [])[-3:]  # Last 3 messages
        
        context = f"## PROJECT OVERVIEW\n"
        context += f"Project: {project_data['name']}\n"
        context += f"Current Agent: {agent_name.replace('_', ' ').title()}\n\n"
        
        # Include relevant requirements from other agents
        if requirements:
            context += "## EXISTING REQUIREMENTS\n"
            substantial_requirements = 0
            
            for other_agent, req_data in requirements.items():
                if other_agent != agent_name and req_data.get('has_substance', False):
                    summary = self._create_agent_summary(req_data['full_response'])
                    context += f"- {other_agent.replace('_', ' ').title()}: {summary}\n"
                    substantial_requirements += 1
            
            if substantial_requirements == 0:
                context += "No substantial requirements gathered yet.\n"
            context += "\n"
        
        # Include recent conversation
        if recent_messages:
            context += "## RECENT CONVERSATION\n"
            for msg in recent_messages:
                role = "User" if msg['role'] == 'user' else "Assistant"
                context += f"{role}: {msg['message'][:150]}\n"
            context += "\n"
        
        return context
    
    def _create_agent_summary(self, response: str) -> str:
        """Create intelligent summary of agent responses"""
        if len(response) <= 100:
            return response
        
        # Try to extract the main point (first sentence or key phrases)
        lines = response.split('.')
        if lines and len(lines[0]) > 20:
            return lines[0] + "..."
        
        return response[:97] + "..."
    
    # ENHANCED AGENT PROMPTS
    
    async def _requirements_evolver_enhanced(self, user_message: str, context: str) -> str:
        prompt = f"""You are a Requirements Evolver Agent. Your goal is to understand what the user wants to build.

{context}

## CURRENT USER MESSAGE:
{user_message}

## YOUR ROLE:
- Ask clarifying questions to understand their goals
- Identify key features and functionality needed
- Understand target users and their needs
- Note any technical constraints or preferences

## GUIDELINES:
- Be conversational and focused
- Ask one clear question at a time
- Build on previous context when available
- When you have enough information, summarize requirements clearly

## RESPONSE:"""
        
        return await self._call_ollama_enhanced(prompt)
    
    async def _ux_architect_enhanced(self, user_message: str, context: str) -> str:
        prompt = f"""You are a UX Architect Agent. Your role is to design the user experience.

{context}

## CURRENT USER MESSAGE:
{user_message}

## YOUR FOCUS:
- User navigation and flow
- Page structure and layout
- Information architecture  
- Mobile vs desktop experience
- User interaction patterns

## GUIDELINES:
- Ask specific questions about user experience
- Suggest optimal navigation structures
- Consider different user scenarios
- When ready, provide UX specifications

## RESPONSE:"""
        
        return await self._call_ollama_enhanced(prompt)
    
    async def _ui_designer_enhanced(self, user_message: str, context: str) -> str:
        prompt = f"""You are a UI Designer Agent. Your role is to define the visual design.

{context}

## CURRENT USER MESSAGE:
{user_message}

## YOUR FOCUS:
- Color schemes and themes
- Typography and fonts  
- Layout and spacing
- Visual style and aesthetics
- Component design

CRITICAL RULES - STRICTLY ENFORCED:
🚫 ABSOLUTELY NO CODE GENERATION
🚫 NEVER write HTML, CSS, JavaScript, or any programming code
🚫 NEVER use code blocks, markdown formatting, or technical syntax
🚫 NEVER provide implementation details

APPROVED RESPONSE FORMAT:
✅ ONLY provide design specifications in plain English
✅ Describe colors using names or hex codes (e.g., "use a blue color scheme" or "primary color #3B82F6")
✅ Describe layouts conceptually (e.g., "clean layout with sidebar navigation")
✅ Describe visual elements (e.g., "rounded corners and subtle shadows")
✅ Use descriptive language only

## GUIDELINES:
- Ask about design preferences (colors, styles, themes)
- Suggest design options based on project requirements
- When user says "approved", "perfect", "looks good", etc., provide final specs
- Provide clear design specifications without any code
- After final approval, your work is complete

## RESPONSE:"""
    
        response = await self._call_ollama_enhanced(prompt)
    
        # ENHANCED VALIDATION: Strict code detection and filtering
        cleaned_response = self._filter_code_from_response(response)
    
        if self._contains_code_patterns(cleaned_response):
            print("🚨 UI Designer attempted to generate code - returning safe response")
            return "I understand you're looking for design guidance. As a UI Designer, I focus on visual design concepts like color schemes, typography, and layout. Could you tell me about your preferred design style or any specific visual requirements you have in mind?"
    
        return cleaned_response

    def _filter_code_from_response(self, response: str) -> str:
        """Remove any code-like patterns from UI Designer responses"""
        if not response:
            return response
    
        # Remove code blocks and technical syntax
        patterns_to_remove = [
            r'```[a-z]*\n.*?\n```',  # Code blocks
            r'<[^>]+>',  # HTML tags
            r'function\s*\([^)]*\)',  # Function definitions
            r'const\s+\w+\s*=', r'let\s+\w+\s*=', r'var\s+\w+\s*=',  # Variable declarations
            r'import\s+.*?from', r'from\s+.*?import',  # Import statements
            r'def\s+\w+\s*\([^)]*\):',  # Python functions
            r'class\s+\w+',  # Class definitions
        ]
    
        cleaned = response
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    
        return cleaned.strip()

    def _contains_code_patterns(self, text: str) -> bool:
        """Check if text contains code patterns that should be filtered"""
        if not text:
            return False
    
        code_indicators = [
            '<html', '<div', '<script', 'function(', 'const ', 'let ', 'import ', 'from ', 
            'def ', 'class ', '@app', 'render_template', 'return ', '={', '=>', '();',
            '```python', '```html', '```css', '```js', '```javascript'
        ]
    
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in code_indicators) 
       
    async def _frontend_engineer_enhanced(self, user_message: str, context: str) -> str:
        prompt = f"""You are a Frontend Engineer Agent. Your role is technical implementation.

{context}

## CURRENT USER MESSAGE:
{user_message}

## YOUR FOCUS:
- JavaScript frameworks or vanilla JS
- Interactive features and functionality
- Performance considerations
- Browser compatibility
- Modern web standards

CRITICAL RULES - STRICTLY ENFORCED:
🚫 ABSOLUTELY NO CODE GENERATION
🚫 NEVER write HTML, CSS, JavaScript, or any programming code
🚫 NEVER use code blocks, markdown formatting, or technical syntax
🚫 NEVER provide implementation details

## GUIDELINES:
- Ask technical questions about implementation
- Suggest appropriate technologies
- Consider user experience requirements
- When ready, provide technical specifications

## RESPONSE:"""
        
        return await self._call_ollama_enhanced(prompt)
    
    async def _data_architect_enhanced(self, user_message: str, context: str) -> str:
        prompt = f"""You are a Data Architect Agent. Your role is data design.

{context}

## CURRENT USER MESSAGE:
{user_message}

## YOUR FOCUS:
- Data storage requirements
- Database design (SQL vs NoSQL)
- Data relationships and schema
- Security and privacy considerations
- Data validation and integrity

CRITICAL RULES - STRICTLY ENFORCED:
🚫 ABSOLUTELY NO CODE GENERATION
🚫 NEVER write HTML, CSS, JavaScript, or any programming code
🚫 NEVER use code blocks, markdown formatting, or technical syntax
🚫 NEVER provide implementation details

APPROVED RESPONSE FORMAT:
✅ ONLY provide design specifications in plain English
✅ Use descriptive language only

## GUIDELINES:
- Ask about data needs and storage
- Suggest appropriate database solutions
- Consider scalability requirements
- When ready, provide data architecture specs

## RESPONSE:"""
        
        return await self._call_ollama_enhanced(prompt)
    
    async def _api_designer_enhanced(self, user_message: str, context: str) -> str:
        prompt = f"""You are an API Designer Agent. Your role is backend design.

{context}

## CURRENT USER MESSAGE:
{user_message}

## YOUR FOCUS:
- API endpoints and routes
- Authentication and authorization
- Data formats (JSON, etc.)
- Backend functionality
- Error handling

## GUIDELINES:
- Ask about API requirements
- Suggest RESTful design patterns
- Consider security requirements
- When ready, provide API specifications

## RESPONSE:"""
        
        return await self._call_ollama_enhanced(prompt)
    
    async def _devops_enhanced(self, user_message: str, context: str) -> str:
        prompt = f"""You are a DevOps Agent. Your role is deployment planning.

{context}

## CURRENT USER MESSAGE:
{user_message}

## YOUR FOCUS:
- Deployment platforms and hosting
- Domain and SSL configuration
- Environment setup
- Scalability and performance
- Monitoring and maintenance

## GUIDELINES:
- Ask about deployment preferences
- Suggest appropriate hosting solutions
- Consider budget and scale requirements
- When ready, provide deployment specifications

## RESPONSE:"""
        
        return await self._call_ollama_enhanced(prompt)
    
    async def _call_ollama_enhanced(self, prompt: str) -> str:
        """Enhanced Ollama call with better error handling"""
        try:
            response = ollama.chat(
                model=settings.OLLAMA_MODEL,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': settings.TEMPERATURE,
                    'num_predict': settings.MAX_RESPONSE_TOKENS,
                    'top_k': 40,
                    'top_p': 0.9
                }
            )
            return response['message']['content']
        except Exception as e:
            print(f"❌ Ollama API error: {e}")
            return f"I encountered a technical issue. Please try again or rephrase your request. Error: {str(e)}"
    
    def _extract_requirements_enhanced(self, project_id: str, agent_name: str, response: str, user_message: str) -> bool:
        """Enhanced requirement extraction with substance detection - returns True if updated"""
        # Detect if this response has substantial content
        has_substance = self._has_substantial_content(response, agent_name)
        
        requirements = {
            'full_response': response,
            'user_message': user_message,
            'summary': self._create_intelligent_summary_enhanced(response),
            'technical_specs': self._extract_technical_specs_enhanced(response, agent_name),
            'timestamp': asyncio.get_event_loop().time(),
            'agent': agent_name,
            'has_substance': has_substance  # Track substantial contributions
        }
        
        self.storage.update_requirements(project_id, agent_name, requirements)
        print(f"📝 Stored requirements from {agent_name} (substance: {has_substance})")
        return has_substance
        
    def _create_intelligent_summary_enhanced(self, response: str) -> str:
        """Create better summaries that capture the essence"""
        if len(response) <= 200:
            return response
        
        # Extract the first meaningful paragraph or key statements
        lines = response.split('\n')
        meaningful_lines = []
        
        for line in lines:
            stripped = line.strip()
            if (stripped and 
                not stripped.startswith(('#', '//', '/*')) and
                len(stripped) > 10):
                meaningful_lines.append(stripped)
                if len('\n'.join(meaningful_lines)) > 150:
                    break
        
        summary = '\n'.join(meaningful_lines)
        if len(summary) > 200:
            summary = summary[:197] + "..."
            
        return summary
    
    def _extract_technical_specs_enhanced(self, response: str, agent_name: str) -> Dict[str, Any]:
        """Enhanced technical specification extraction"""
        specs = {}
        response_lower = response.lower()
        
        # Common specifications across agents
        if 'responsive' in response_lower or 'mobile' in response_lower:
            specs['responsive'] = True
        if 'modern' in response_lower:
            specs['style'] = 'modern'
        if 'minimal' in response_lower or 'clean' in response_lower:
            specs['style'] = 'minimal'
        
        # Agent-specific specifications
        if agent_name == 'ui_designer':
            specs.update(self._extract_design_specs_enhanced(response))
        elif agent_name == 'ux_architect':
            specs.update(self._extract_ux_specs_enhanced(response))
        elif agent_name == 'frontend_engineer':
            specs.update(self._extract_frontend_specs_enhanced(response))
        elif agent_name == 'data_architect':
            specs.update(self._extract_data_specs_enhanced(response))
        elif agent_name == 'api_designer':
            specs.update(self._extract_api_specs_enhanced(response))
        elif agent_name == 'devops':
            specs.update(self._extract_devops_specs_enhanced(response))
            
        return specs
    
    def _extract_design_specs_enhanced(self, response: str) -> Dict[str, Any]:
        """Enhanced design specification extraction"""
        specs = {}
        response_lower = response.lower()
        
        # Color detection with better pattern matching
        import re
        color_pattern = r'#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})'
        colors = re.findall(color_pattern, response)
        if colors:
            specs['colors'] = [f"#{color}" for color in colors[:3]]  # Limit to 3 colors
        
        # Layout detection
        if any(word in response_lower for word in ['single page', 'spa']):
            specs['layout'] = 'single-page'
        elif any(word in response_lower for word in ['multi-page', 'multiple pages']):
            specs['layout'] = 'multi-page'
            
        return specs
    
    def _extract_ux_specs_enhanced(self, response: str) -> Dict[str, Any]:
        """Enhanced UX specification extraction"""
        specs = {}
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['simple', 'basic']):
            specs['complexity'] = 'simple'
        elif any(word in response_lower for word in ['complex', 'advanced']):
            specs['complexity'] = 'complex'
            
        return specs
    
    def _extract_frontend_specs_enhanced(self, response: str) -> Dict[str, Any]:
        """Enhanced frontend specification extraction"""
        specs = {}
        response_lower = response.lower()
        
        framework_keywords = {
            'vue': ['vue', 'vue.js'],
            'react': ['react', 'react.js'], 
            'angular': ['angular'],
            'vanilla': ['vanilla', 'plain javascript', 'native javascript']
        }
        
        for framework, keywords in framework_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                specs['framework'] = framework
                break
                
        return specs
    
    def _extract_data_specs_enhanced(self, response: str) -> Dict[str, Any]:
        """Enhanced data specification extraction"""
        specs = {}
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['sql', 'postgres', 'mysql']):
            specs['database'] = 'sql'
        elif any(word in response_lower for word in ['nosql', 'mongodb']):
            specs['database'] = 'nosql'
        elif any(word in response_lower for word in ['local storage', 'browser storage']):
            specs['database'] = 'local'
            
        return specs
    
    def _extract_api_specs_enhanced(self, response: str) -> Dict[str, Any]:
        """Enhanced API specification extraction"""
        specs = {}
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['rest', 'restful']):
            specs['api_type'] = 'rest'
        elif any(word in response_lower for word in ['graphql']):
            specs['api_type'] = 'graphql'
            
        return specs
    
    def _extract_devops_specs_enhanced(self, response: str) -> Dict[str, Any]:
        """Enhanced DevOps specification extraction"""
        specs = {}
        response_lower = response.lower()
        
        platform_keywords = {
            'netlify': ['netlify'],
            'vercel': ['vercel'],
            'heroku': ['heroku'],
            'aws': ['aws', 'amazon'],
            'docker': ['docker', 'container']
        }
        
        for platform, keywords in platform_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                specs['platform'] = platform
                break
                
        return specs
    
    def _has_substantial_content(self, response: str, agent_name: str) -> bool:
        """REFINED: More trusting substance detection"""
        if not response or len(response.strip()) < 20:  # Reduced threshold
            print(f"🔍 {agent_name}: Response too short ({len(response.strip()) if response else 0} chars)")
            return False

        response_lower = response.lower().strip()
        response_clean = response.strip()

        # 🎯 REFINED: Trust more responses, be less restrictive
        # Early agents: Accept most meaningful responses
        if agent_name in ['requirements_evolver', 'ux_architect', 'ui_designer']:
            # Accept if response has reasonable length and isn't purely asking questions
            is_pure_question = (
                response_clean.endswith('?') and 
                len(response_clean) < 80 and
                any(phrase in response_lower for phrase in ['what would', 'can you', 'please provide'])
            )
            
            is_substantial = len(response_clean) >= 30 and not is_pure_question
            print(f"🔍 {agent_name} EARLY AGENT: length={len(response_clean)}, substantial={is_substantial}")
            return is_substantial

        # Technical agents: Still need some technical content but be more lenient
        else:
            technical_indicators = {
                'frontend_engineer': ['javascript', 'framework', 'component', 'interaction'],
                'data_architect': ['database', 'storage', 'data', 'schema'],
                'api_designer': ['endpoint', 'api', 'rest', 'backend'],
                'devops': ['deployment', 'hosting', 'server', 'cloud']
            }
            
            agent_indicators = technical_indicators.get(agent_name, [])
            has_technical_content = any(indicator in response_lower for indicator in agent_indicators)
            
            is_substantial = len(response_clean) >= 40 and has_technical_content
            print(f"🔍 {agent_name} TECHNICAL AGENT: length={len(response_clean)}, technical={has_technical_content}, substantial={is_substantial}")
            return is_substantial

    # Keep original working methods for compatibility
    def _extract_technical_specs(self, response: str, agent_name: str) -> Dict[str, Any]:
        """Original method for compatibility"""
        return self._extract_technical_specs_enhanced(response, agent_name)
    
    def _create_intelligent_summary(self, response: str) -> str:
        """Original method for compatibility"""
        return self._create_intelligent_summary_enhanced(response)