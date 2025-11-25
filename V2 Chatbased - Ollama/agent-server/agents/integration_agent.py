"""
Integration Agent - Plans project structure and coordinates file generation
REFINED VERSION: Better context integration, more trusting validation
"""

import asyncio
from typing import Dict, List, Any
import ollama
from pathlib import Path
import re
from config import settings

class IntegrationAgent:
    def __init__(self):
        pass
    
    async def plan_project_structure(self, project_data: Dict[str, Any]) -> List[str]:
        """Generate optimal Flask project structure with enhanced context"""
        requirements = project_data.get('requirements', {})
        project_name = project_data['name']
        project_id = project_data['id']
        
        prompt = f"""# TASK: Plan MINIMAL Flask project structure

## PROJECT: {project_name} ({project_id})

## REQUIREMENTS SUMMARY:
{self._build_enhanced_requirements_summary(requirements)}

## INSTRUCTIONS:
1. Analyze ALL requirements below and create ONLY essential files
2. Focus on Flask best practices - keep it simple but functional
3. List ONE file path per line
4. Include ONLY: app.py, requirements.txt, templates/, static/ files
5. NO duplicates, NO unnecessary files
6. Consider the specific features mentioned in requirements

## ESSENTIAL FILES (adapt based on requirements):
app.py
requirements.txt
templates/index.html
static/css/style.css
static/js/app.js
README.md

## FILE LIST:"""
        
        try:
            response = ollama.chat(
                model=settings.OLLAMA_MODEL,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': 0.1,
                    'num_predict': 800
                }
            )
            
            file_list = self._extract_file_list_deduplicated(response['message']['content'])
            return file_list
            
        except Exception as e:
            print(f"❌ Structure planning failed: {e}")
            # Minimal fallback - no complex logic
            return ["app.py", "requirements.txt", "templates/index.html", "static/css/style.css", "static/js/app.js"]
    
    async def generate_file_content_with_context(self, project_data: Dict[str, Any], file_path: str, existing_files: List[Dict[str, Any]]) -> str:
        """🎯 REFINED: Generate file content with enhanced context awareness"""
        requirements = project_data.get('requirements', {})
        project_name = project_data['name']
        
        prompt = self._build_enhanced_prompt(project_name, file_path, requirements, existing_files)
        
        try:
            response = ollama.chat(
                model=settings.OLLAMA_MODEL,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': 0.2,  # Slightly higher for creativity
                    'num_predict': 3000  # More tokens for complex files
                }
            )
            
            clean_code = self._extract_pure_code_enhanced(response['message']['content'])
            
            # 🎯 REFINED VALIDATION - More trusting
            if not self._is_valid_file_content_trusted(clean_code, file_path):
                print(f"⚠️  Content validation warning for {file_path}, but trusting Ollama output")
                # Accept the content anyway - rely on preview server for actual errors
            
            return clean_code
            
        except Exception as e:
            print(f"❌ File generation failed for {file_path}: {e}")
            # Gentle fallback with diagnostic
            return f"# Error generating {file_path}. Please try again.\n# {str(e)}"
    
    def _build_enhanced_prompt(self, project_name: str, file_path: str, requirements: Dict[str, Any], existing_files: List[Dict[str, Any]]) -> str:
        """🎯 REFINED: Enhanced prompt with better context integration"""
        
        # Build comprehensive context
        file_context = self._build_comprehensive_file_context(existing_files)
        requirements_context = self._build_detailed_requirements_context(requirements)
        integration_guidance = self._get_integration_guidance(file_path, existing_files)
        
        prompt = f"""# GENERATE {file_path} for {project_name}

## PROJECT OVERVIEW:
{requirements_context}

## EXISTING FILES (INTEGRATE WITH THESE):
{file_context}

## INTEGRATION GUIDANCE:
{integration_guidance}

## FILE-SPECIFIC REQUIREMENTS:
{self._get_file_specific_requirements_enhanced(file_path, requirements)}

## CRITICAL RULES:
1. Generate COMPLETE, WORKING code for {file_path}
2. NO explanations, NO markdown, NO comments about the code
3. MUST integrate seamlessly with existing file structure
4. MUST follow Flask + Vanilla JavaScript architecture
5. Code must be production-ready and well-structured
6. For CSS: Create complete, responsive styling
7. For HTML: Build functional, accessible pages
8. For JavaScript: Implement robust, error-handled functionality

## OUTPUT:
Pure, complete code only - no additional text:

"""
        return prompt

    def _build_comprehensive_file_context(self, existing_files: List[Dict[str, Any]]) -> str:
        """🎯 ENHANCED: Build comprehensive context about existing files"""
        if not existing_files:
            return "No other files generated yet. Create a complete foundation."

        context = "## Files already created:\n"
        
        # Group by type with content previews
        python_files = [f for f in existing_files if f['path'].endswith('.py')]
        template_files = [f for f in existing_files if 'templates/' in f['path']]
        static_files = [f for f in existing_files if 'static/' in f['path']]
        other_files = [f for f in existing_files if f not in python_files + template_files + static_files]
        
        if python_files:
            context += "\n### Python Files:\n"
            for f in python_files:
                preview = f['content_preview'][:200] + "..." if len(f['content_preview']) > 200 else f['content_preview']
                context += f"- {f['path']}: {preview}\n"
        
        if template_files:
            context += "\n### Template Files:\n"
            for f in template_files:
                preview = f['content_preview'][:150] + "..." if len(f['content_preview']) > 150 else f['content_preview']
                context += f"- {f['path']}: {preview}\n"
        
        if static_files:
            context += "\n### Static Files:\n"
            for f in static_files:
                file_type = "CSS" if f['path'].endswith('.css') else "JS" if f['path'].endswith('.js') else "Static"
                preview = f['content_preview'][:100] + "..." if len(f['content_preview']) > 100 else f['content_preview']
                context += f"- {f['path']} ({file_type}): {preview}\n"
        
        if other_files:
            context += "\n### Other Files:\n"
            for f in other_files:
                context += f"- {f['path']}\n"
        
        return context

    def _build_detailed_requirements_context(self, requirements: Dict[str, Any]) -> str:
        """🎯 ENHANCED: Build detailed requirements context"""
        if not requirements:
            return "Create a complete, functional web application with Flask backend and modern frontend."
            
        context = "## Project Requirements by Domain:\n\n"
        
        agent_descriptions = {
            'requirements_evolver': "📋 Core Features & Goals",
            'ux_architect': "🎯 User Experience & Navigation", 
            'ui_designer': "🎨 Visual Design & Styling",
            'frontend_engineer': "⚡ Frontend Implementation",
            'data_architect': "💾 Data Structure & Storage",
            'api_designer': "🔗 API Design & Backend",
            'devops': "🚀 Deployment & Hosting"
        }
        
        for agent_name, agent_req in requirements.items():
            if agent_req and agent_req.get('full_response'):
                description = agent_descriptions.get(agent_name, agent_name.replace('_', ' ').title())
                full_response = agent_req['full_response']
                
                # Extract key points (first 2-3 sentences)
                sentences = [s.strip() for s in full_response.split('.') if s.strip()]
                key_points = '. '.join(sentences[:3]) + '.' if sentences else full_response[:300]
                
                context += f"### {description}:\n{key_points}\n\n"
        
        return context

    def _get_integration_guidance(self, file_path: str, existing_files: List[Dict[str, Any]]) -> str:
        """🎯 ENHANCED: Provide specific integration guidance"""
        guidance = []
        
        # Check what files exist and provide integration tips
        existing_paths = [f['path'] for f in existing_files]
        
        if file_path == 'app.py':
            if 'templates/index.html' in existing_paths:
                guidance.append("Integrate with existing templates/index.html using render_template()")
            if 'static/css/style.css' in existing_paths:
                guidance.append("Reference static/css/style.css in your templates")
            if 'static/js/app.js' in existing_paths:
                guidance.append("Ensure your routes work with static/js/app.js functionality")
            guidance.extend([
                "Define clear Flask routes with proper error handling",
                "Include all necessary imports (Flask, render_template, request, jsonify)",
                "Implement input validation for all user inputs",
                "Use proper JSON responses for API endpoints"
            ])
        
        elif file_path.endswith('.html') and 'templates/' in file_path:
            if 'app.py' in existing_paths:
                guidance.append("Ensure your HTML forms point to correct Flask routes from app.py")
            if 'static/css/style.css' in existing_paths:
                guidance.append("Link to static/css/style.css using url_for('static', filename='css/style.css')")
            if 'static/js/app.js' in existing_paths:
                guidance.append("Include static/js/app.js using proper script tags")
            guidance.extend([
                "Use semantic HTML5 structure",
                "Implement proper form structure with labels and inputs",
                "Ensure accessibility with proper ARIA labels if needed",
                "Use Jinja2 templating if extending other templates"
            ])
        
        elif file_path.endswith('.css'):
            guidance.extend([
                "Create responsive design that works on mobile and desktop",
                "Use modern CSS features (Flexbox/Grid)",
                "Define clear color scheme and typography",
                "Style all components mentioned in requirements",
                "Ensure good contrast and accessibility"
            ])
        
        elif file_path.endswith('.js'):
            if 'app.py' in existing_paths:
                guidance.append("Connect to Flask backend routes defined in app.py")
            guidance.extend([
                "Use vanilla JavaScript only - no frameworks",
                "Implement proper error handling for API calls",
                "Use modern ES6+ features",
                "Handle form submissions and user interactions",
                "Update DOM elements based on API responses"
            ])
        
        return "\n".join([f"- {item}" for item in guidance])

    def _get_file_specific_requirements_enhanced(self, file_path: str, requirements: Dict[str, Any]) -> str:
        """🎯 ENHANCED: File-specific requirements with project context"""
        base_requirements = {
            'app.py': """- Create complete Flask application
- Define all necessary routes based on project requirements
- Include proper error handling and input validation
- Implement business logic from requirements
- Use render_template() for HTML responses
- Include proper imports and app configuration""",
            
            'templates/index.html': """- Create complete HTML page structure
- Include all UI components mentioned in requirements
- Implement proper form structures if needed
- Ensure responsive design foundation
- Include proper meta tags and accessibility features""",
            
            'static/css/style.css': """- Create comprehensive CSS stylesheet
- Implement responsive design for all screen sizes
- Define complete color scheme and typography
- Style all UI components from requirements
- Include modern CSS features and best practices""",
            
            'static/js/app.js': """- Create complete JavaScript functionality
- Handle all user interactions from requirements
- Implement API communication with Flask backend
- Include proper error handling and user feedback
- Use modern JavaScript patterns""",
            
            'requirements.txt': """- List all Python dependencies for Flask project
- Include Flask and any additional packages needed
- Use proper version pinning for production readiness"""
        }
        
        # Add specific requirements from project context
        specific_needs = self._extract_specific_requirements(file_path, requirements)
        
        return base_requirements.get(file_path, "- Create appropriate content for this file type") + specific_needs

    def _extract_specific_requirements(self, file_path: str, requirements: Dict[str, Any]) -> str:
        """Extract specific requirements relevant to this file"""
        specific = []
        
        for agent_name, agent_req in requirements.items():
            if agent_req and agent_req.get('technical_specs'):
                specs = agent_req['technical_specs']
                
                if file_path == 'app.py' and specs.get('api_type'):
                    specific.append(f"\n- Implement {specs['api_type'].upper()} API design")
                
                if file_path.endswith('.css') and specs.get('colors'):
                    specific.append(f"\n- Use color scheme: {', '.join(specs['colors'])}")
                
                if file_path.endswith('.css') and specs.get('style'):
                    specific.append(f"\n- Implement {specs['style']} design style")
                
                if file_path.endswith('.js') and specs.get('framework'):
                    specific.append(f"\n- Use {specs['framework']} approach (vanilla JS only)")
        
        return ''.join(specific) if specific else ""

    def _extract_pure_code_enhanced(self, raw_response: str) -> str:
        """🎯 REFINED: Enhanced code extraction - trust Ollama more"""
        if not raw_response:
            return ""
    
        # Remove markdown code blocks but KEEP the content
        clean = re.sub(r'```[a-z]*\n?', '', raw_response, flags=re.IGNORECASE)
        clean = re.sub(r'```', '', clean)
    
        # 🎯 TRUST: Be more lenient with explanatory text
        # Only remove obvious non-code patterns at the beginning
        lines = clean.split('\n')
        code_lines = []
        found_code_start = False
    
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Skip obvious explanation lines at the beginning
            if not found_code_start:
                if (stripped.lower().startswith(('this is', 'here is', 'the following', 'sure,', 'certainly,')) and
                    '{' not in stripped and '<' not in stripped and 'import' not in stripped):
                    continue
                else:
                    found_code_start = True
            
            code_lines.append(line)
    
        result = '\n'.join(code_lines).strip()
    
        # Final check - ensure we have some content
        if not result or len(result) < 10:
            return raw_response.strip()  # Fallback to original
    
        return result

    def _is_valid_file_content_trusted(self, content: str, file_path: str) -> bool:
        """🎯 REFINED: Trust-based validation - accept more Ollama patterns"""
        if not content or len(content.strip()) < 15:  # Reduced threshold
            return False
    
        # 🎯 TRUST: File-specific validation with lenient rules
        if file_path.endswith('.py'):
            return self._is_valid_python_content_trusted(content, file_path)
        elif file_path.endswith('.html'):
            return self._is_valid_html_content_trusted(content)
        elif file_path.endswith('.css'):
            return self._is_valid_css_content_trusted(content)
        elif file_path.endswith('.js'):
            return self._is_valid_javascript_content_trusted(content)
        elif file_path.endswith('.txt') or file_path.endswith('.md'):
            return len(content.strip()) > 5
        else:
            return len(content.strip()) > 10

    def _is_valid_python_content_trusted(self, content: str, file_path: str) -> bool:
        """🎯 REFINED: Lenient Python validation"""
        content_lower = content.lower()
        
        if file_path == 'app.py':
            # Accept various Flask patterns
            flask_indicators = [
                'flask' in content_lower,
                '@app' in content,
                'render_template' in content,
                'flask' in content_lower and 'import' in content,
                'from flask' in content
            ]
            return any(flask_indicators) or len(content.strip()) > 100
            
        elif file_path == 'requirements.txt':
            # Accept any requirements-like content
            return any(char in content for char in ['=', '>', '<', '\n']) and len(content.strip()) > 5
            
        else:
            # Accept Python-like content
            python_indicators = [
                'import ' in content,
                'def ' in content, 
                'class ' in content,
                'from ' in content,
                'print(' in content,
                'return ' in content
            ]
            return any(python_indicators) or len(content.strip()) > 50

    def _is_valid_html_content_trusted(self, content: str) -> bool:
        """🎯 REFINED: Lenient HTML validation"""
        html_indicators = [
            '<!doctype' in content.lower(),
            '<html' in content.lower(), 
            '<head' in content.lower(),
            '<body' in content.lower(),
            '<div' in content,
            '<p>' in content,
            '<h1' in content,
            '<form' in content
        ]
        return any(html_indicators) and '<' in content and '>' in content

    def _is_valid_css_content_trusted(self, content: str) -> bool:
        """🎯 REFINED: Very lenient CSS validation"""
        if not content or len(content.strip()) < 10:
            return False

        clean_content = content.strip()
    
        css_indicators = [
            '{' in clean_content and '}' in clean_content,
            any(char in clean_content for char in [':', ';', '#', '.']),
            any(word in clean_content.lower() for word in ['color', 'font', 'margin', 'padding', 'width', 'height']),
        ]
    
        has_any_css = any(css_indicators)
        balanced_braces = clean_content.count('{') == clean_content.count('}')
    
        return has_any_css or (balanced_braces and len(clean_content) > 25)

    def _is_valid_javascript_content_trusted(self, content: str) -> bool:
        """🎯 REFINED: Lenient JavaScript validation"""
        content_lower = content.lower()
        
        js_indicators = [
            'function' in content,
            'const ' in content,
            'let ' in content, 
            'document.' in content,
            'addeventlistener' in content_lower,
            'getelementbyid' in content_lower,
            'fetch' in content,
            'api' in content_lower
        ]
        
        # Allow modern JS but block obvious frameworks
        no_frameworks = not any(fw in content_lower for fw in ['import react', 'from react', 'vue', 'angular'])
        
        return (any(js_indicators) or len(content.strip()) > 50) and no_frameworks

    # Keep existing file planning logic (working well)
    def _build_enhanced_requirements_summary(self, requirements: Dict[str, Any]) -> str:
        """Enhanced requirements summary for planning"""
        summary_parts = []
        for agent_name, agent_req in requirements.items():
            if agent_req and agent_req.get('full_response'):
                response = agent_req['full_response']
                # Extract first meaningful part
                summary = response.split('.')[0] if '.' in response else response[:200]
                if len(summary.strip()) > 20:
                    summary_parts.append(f"{agent_name}: {summary}")
        return "\n".join(summary_parts) if summary_parts else "Create a functional web application."

    def _extract_file_list_deduplicated(self, response: str) -> List[str]:
        """Existing working logic - preserved"""
        lines = response.strip().split('\n')
        file_list = []
        seen_files = set()
    
        valid_extensions = ['.py', '.html', '.css', '.js', '.json', '.md', '.txt']
    
        for line in lines:
            line = line.strip()
            if not line:
                continue
        
            code_patterns = ['from ', 'import ', '@app', 'def ', 'class ', '<!DOCTYPE', '// ', '/*']
            if any(pattern in line for pattern in code_patterns):
                continue
        
            if any(char in line for char in ['(', ')', '{', '}', '[', ']', '==', '=']):
                continue
            
            if line.startswith('#') or '://' in line or line.startswith('//'):
                continue
        
            clean_path = line.split('#')[0].split('[')[0].strip()
        
            if clean_path and (any(ext in clean_path for ext in valid_extensions) or 
                      ('/' in clean_path and '.' in clean_path.split('/')[-1])):
                if (len(clean_path) < 100 and 
                not any(bad_char in clean_path for bad_char in ['*', '?', '"', '<', '>', '|']) and
                not clean_path.endswith('/')):
                
                    normalized_path = self._normalize_file_path(clean_path)
                    file_list.append(normalized_path)
    
        file_list = self._resolve_file_conflicts(file_list)
    
        essential_files = ["app.py", "requirements.txt", "templates/index.html", "static/css/style.css", "static/js/app.js"]
        for essential in essential_files:
            if essential not in file_list:
                file_list.append(essential)
    
        print(f"📁 Final file structure: {file_list}")
        return file_list

    def _normalize_file_path(self, file_path: str) -> str:
        """Existing working logic - preserved"""
        path_mapping = {
            'style.css': 'static/css/style.css',
            'app.js': 'static/js/app.js', 
            'index.html': 'templates/index.html',
            'scripts.js': 'static/js/app.js',
            'styles.css': 'static/css/style.css'
        }
        return path_mapping.get(file_path, file_path)

    def _resolve_file_conflicts(self, file_list: List[str]) -> List[str]:
        """Existing working logic - preserved"""
        conflict_groups = {
            'index.html': ['index.html', 'templates/index.html'],
            'style.css': ['style.css', 'static/css/style.css', 'styles.css'],
            'app.js': ['app.js', 'static/js/app.js', 'scripts.js']
        }
    
        resolved_files = []
    
        for file_path in file_list:
            has_conflict = False
            for conflict_group in conflict_groups.values():
                if file_path in conflict_group:
                    preferred = [f for f in conflict_group if f.startswith(('templates/', 'static/'))]
                    if preferred and preferred[0] not in resolved_files:
                        resolved_files.append(preferred[0])
                    has_conflict = True
                    break
        
            if not has_conflict and file_path not in resolved_files:
                resolved_files.append(file_path)
    
        return resolved_files