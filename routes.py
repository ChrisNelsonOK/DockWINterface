import os
import json
import yaml
from flask import render_template, request, jsonify, flash, redirect, url_for, send_file
from app import app
from docker_config import DockerConfigGenerator
from ai_assistant import AIAssistant
import logging

# Initialize components
config_generator = DockerConfigGenerator()
ai_assistant = AIAssistant()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/wizard')
def wizard():
    """Configuration wizard page"""
    return render_template('wizard.html')

@app.route('/deployments')
def deployments():
    """Deployments management page"""
    return render_template('deployments.html')

@app.route('/chat')
def chat():
    """AI assistant chat page"""
    return render_template('chat.html')

@app.route('/api/generate-config', methods=['POST'])
def generate_config():
    """Generate Docker configuration files"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'version', 'username', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Generate configuration
        docker_compose = config_generator.generate_docker_compose(data)
        env_file = config_generator.generate_env_file(data)
        
        return jsonify({
            'docker_compose': docker_compose,
            'env_file': env_file,
            'success': True
        })
        
    except Exception as e:
        logging.error(f"Error generating config: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-config', methods=['POST'])
def download_config():
    """Download generated configuration files"""
    try:
        data = request.get_json()
        config_generator.save_config_files(data)
        
        return jsonify({'success': True, 'message': 'Configuration files saved successfully'})
        
    except Exception as e:
        logging.error(f"Error saving config files: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """Chat with AI assistant"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message.strip():
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        response = ai_assistant.chat(message)
        
        return jsonify({
            'response': response,
            'success': True
        })
        
    except Exception as e:
        logging.error(f"Error in AI chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate-config', methods=['POST'])
def validate_config():
    """Validate configuration parameters"""
    try:
        data = request.get_json()
        validation_result = config_generator.validate_config(data)
        
        return jsonify(validation_result)
        
    except Exception as e:
        logging.error(f"Error validating config: {str(e)}")
        return jsonify({'valid': False, 'errors': [str(e)]})

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
