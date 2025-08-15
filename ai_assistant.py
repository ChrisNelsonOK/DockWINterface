import os
import json
import logging
from typing import Dict, Any, Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OpenAI = None
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI package not available. AI features will be disabled.")

class AIAssistant:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.client = None
        
        if OPENAI_AVAILABLE and self.api_key and OpenAI:
            self.client = OpenAI(api_key=self.api_key)
        else:
            logging.warning("OpenAI API key not found or OpenAI package not available. AI features disabled.")
    
    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Chat with AI assistant about Docker and Windows container deployment"""
        if not self.client:
            return "AI assistant is not available. Please check your OpenAI API key configuration."
        
        try:
            # System prompt for Docker/Windows container expertise
            system_prompt = """You are DockWINterface AI Assistant, an expert in Docker containerization and Windows container deployments using the Dockur Windows project.

You help users with:
- Configuring Windows containers using Dockur
- Docker and docker-compose best practices
- Troubleshooting container deployment issues
- Security considerations for Windows containers
- Performance optimization
- Network and storage configuration

Provide clear, actionable advice. When suggesting configurations, explain the reasoning behind your recommendations."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Add context if provided
            if context:
                context_message = f"Current configuration context: {json.dumps(context, indent=2)}"
                messages.insert(1, {"role": "assistant", "content": context_message})
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content or "Sorry, I couldn't generate a response."
            
        except Exception as e:
            logging.error(f"AI chat error: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def analyze_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze configuration and provide recommendations"""
        if not self.client:
            return {"error": "AI assistant not available"}
        
        try:
            prompt = f"""Analyze this Docker Windows container configuration and provide recommendations:

Configuration:
{json.dumps(config, indent=2)}

Please provide analysis in JSON format with these fields:
- recommendations: array of improvement suggestions
- security_notes: array of security considerations
- performance_tips: array of performance optimization tips
- warnings: array of potential issues

Focus on Dockur Windows project best practices."""

            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if content:
                return json.loads(content)
            else:
                return {"error": "No response generated"}
            
        except Exception as e:
            logging.error(f"Config analysis error: {str(e)}")
            return {"error": str(e)}
    
    def troubleshoot(self, issue: str, logs: str = "") -> str:
        """Help troubleshoot deployment issues"""
        if not self.client:
            return "AI troubleshooting is not available. Please check your OpenAI API key configuration."
        
        try:
            prompt = f"""Help troubleshoot this Docker Windows container issue:

Issue: {issue}

Logs (if available):
{logs}

Provide step-by-step troubleshooting guidance specific to Dockur Windows containers."""

            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800
            )
            
            return response.choices[0].message.content or "Sorry, I couldn't provide troubleshooting guidance."
            
        except Exception as e:
            logging.error(f"Troubleshooting error: {str(e)}")
            return f"Error during troubleshooting: {str(e)}"
