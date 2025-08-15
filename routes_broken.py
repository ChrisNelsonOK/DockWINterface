from flask import request, jsonify, render_template, send_file, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from io import BytesIO
import zipfile
import os
import time
import json
import logging

# Import components
from docker_config import DockerConfigGenerator
from ai_assistant import AIAssistant
from rollback_manager import RollbackManager

print("ROUTES MODULE LOADING - Rollback features enabled")

# Initialize components
config_generator = DockerConfigGenerator()
ai_assistant = AIAssistant()
rollback_manager = RollbackManager()

def register_routes(app, limiter):
    """Register all routes with the Flask app"""
    print("Registering routes with app and limiter")
    
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
    
    @app.route('/rollback')
    def rollback():
        """Rollback management page"""
        return render_template('rollback.html')
    
    @app.route('/chat')
    def chat():
        """AI Assistant chat interface"""
        return render_template('chat.html')
    
    @app.route('/api/generate-config', methods=['POST'])
    @limiter.limit("10 per minute")  # Limit config generation to prevent abuse
    def generate_config():
        """Generate Docker configuration files"""
        try:
            data = request.get_json()
            logging.info(f"Received config data with keys: {data.keys() if data else 'None'}")
        
        # Check if rollback protection is enabled
        enable_rollback = data.get('enable_rollback', False)
        logging.info(f"enable_rollback value: {enable_rollback}, type: {type(enable_rollback)}")
        print(f"DEBUG: enable_rollback = {enable_rollback}, type = {type(enable_rollback)}")
        checkpoint_id = None
        change_type = 'macvlan' if data.get('network_mode') == 'macvlan' else 'container'
        
        # Create checkpoint if rollback is enabled and on Linux
        if enable_rollback and rollback_manager.is_linux:
            checkpoint_result = rollback_manager.create_checkpoint(
                change_type=change_type,
                config=data,
                description=f"DockWINterface deployment: {data.get('name', 'windows')}"
            )
            
            if checkpoint_result['success']:
                checkpoint_id = checkpoint_result['checkpoint_id']
                # Start monitoring in the background
                rollback_manager.start_monitoring(
                    checkpoint_id=checkpoint_id,
                    connectivity_check=(change_type == 'macvlan')
                )
            else:
                logging.warning(f"Failed to create checkpoint: {checkpoint_result.get('error')}")

        # Process additional network interfaces from form data
        additional_networks = []
        i = 0
        while f'nic_name_{i}' in data:
            if data.get(f'nic_name_{i}') and data.get(f'nic_network_{i}'):
                additional_networks.append({
                    'name': data[f'nic_name_{i}'],
                    'network': data[f'nic_network_{i}'],
                    'ip': data.get(f'nic_ip_{i}'),
                    'subnet': data.get(f'nic_subnet_{i}')
                })
            i += 1

        if additional_networks:
            data['additional_networks'] = additional_networks

        # Validate configuration first
        validation_result = config_generator.validate_config(data)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': 'Configuration validation failed',
                'validation': validation_result
            }), 400

        # Generate configuration files
        docker_compose = config_generator.generate_docker_compose(data)
        env_file = config_generator.generate_env_file(data)

        # Save files (optional)
        config_generator.save_config_files(data)

        response_data = {
            'success': True,
            'docker_compose': docker_compose,
            'env_file': env_file,
            'container_name': data.get('name', 'windows'),
            'validation': validation_result
        }
        
        # Add rollback info if enabled (even if not on Linux, for testing)
        logging.info(f"Before rollback check - enable_rollback: {enable_rollback}, checkpoint_id: {checkpoint_id}")
        print(f"DEBUG: About to check enable_rollback condition: {enable_rollback}")
        
        if enable_rollback:
            logging.info(f"Adding rollback info to response")
            print(f"DEBUG: Inside enable_rollback block, checkpoint_id: {checkpoint_id}")
            if checkpoint_id:
                # Real checkpoint created (on Linux)
                response_data['rollback'] = {
                    'enabled': True,
                    'checkpoint_id': checkpoint_id,
                    'timeout': rollback_manager.timeout_defaults.get(change_type, 300),
                    'message': 'Rollback protection enabled. Confirm deployment within timeout to prevent automatic rollback.'
                }
                print(f"DEBUG: Added real rollback info to response")
            else:
                # Mock checkpoint for testing on non-Linux systems
                mock_checkpoint_id = f"test_{change_type}_{int(time.time())}"
                response_data['rollback'] = {
                    'enabled': False,
                    'checkpoint_id': mock_checkpoint_id,
                    'timeout': data.get('rollback_timeout', 5) * 60,  # Convert minutes to seconds
                    'message': 'Rollback protection not available on this platform (requires Linux)',
                    'mock': True
                }
                print(f"DEBUG: Added mock rollback info to response with checkpoint_id: {mock_checkpoint_id}")
                # Create a mock checkpoint for testing
                rollback_manager.active_checkpoints[mock_checkpoint_id] = {
                    'id': mock_checkpoint_id,
                    'created': time.time(),
                    'timeout': data.get('rollback_timeout', 5) * 60,
                    'type': change_type,
                    'monitoring': False,
                    'confirmed': False,
                    'rolled_back': False,
                    'description': f"Mock deployment: {data.get('name', 'windows')}"
                }
        else:
            print(f"DEBUG: Rollback NOT enabled, enable_rollback={enable_rollback}")
        
        print(f"DEBUG: Final response_data keys before return: {response_data.keys()}")
        return jsonify(response_data)

    except Exception as e:
        logging.error(f"Error generating config: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download-config', methods=['POST'])
@limiter.limit("20 per minute")
def download_config():
    """Download generated configuration files"""
    try:
        data = request.get_json()
        config_generator.save_config_files(data)

        msg = 'Configuration files saved successfully'
        return jsonify({'success': True, 'message': msg})

    except Exception as e:
        logging.error(f"Error saving config files: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
@limiter.limit("30 per minute")
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
@limiter.limit("20 per minute")
def validate_config():
    """Validate configuration parameters"""
    try:
        data = request.get_json()
        validation_result = config_generator.validate_config(data)

        return jsonify(validation_result)

    except Exception as e:
        logging.error(f"Error validating config: {str(e)}")
        return jsonify({'valid': False, 'errors': [str(e)]})


@app.route('/api/rollback/confirm', methods=['POST'])
@limiter.limit("10 per minute")
def confirm_rollback():
    """Confirm a rollback checkpoint to prevent automatic rollback"""
    try:
        data = request.get_json()
        checkpoint_id = data.get('checkpoint_id')
        
        if not checkpoint_id:
            return jsonify({'error': 'Checkpoint ID required'}), 400
        
        result = rollback_manager.confirm_checkpoint(checkpoint_id)
        
        if result['success']:
            logging.info(f"Checkpoint {checkpoint_id} confirmed")
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logging.error(f"Error confirming rollback: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/rollback/trigger', methods=['POST'])
@limiter.limit("5 per minute")
def trigger_rollback():
    """Manually trigger rollback to a checkpoint"""
    try:
        data = request.get_json()
        checkpoint_id = data.get('checkpoint_id')
        reason = data.get('reason', 'Manual trigger via API')
        
        if not checkpoint_id:
            return jsonify({'error': 'Checkpoint ID required'}), 400
        
        result = rollback_manager.trigger_rollback(checkpoint_id, reason)
        
        if result['success']:
            logging.warning(f"Rollback triggered for checkpoint {checkpoint_id}: {reason}")
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logging.error(f"Error triggering rollback: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/rollback/history', methods=['GET'])
@limiter.limit("20 per minute")
def get_rollback_history():
    """Get rollback history"""
    try:
        days = request.args.get('days', 7, type=int)
        history = rollback_manager.get_rollback_history(days)
        
        return jsonify({
            'success': True,
            'history': history,
            'days': days
        })
        
    except Exception as e:
        logging.error(f"Error getting rollback history: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/rollback/status/<checkpoint_id>', methods=['GET'])
@limiter.limit("30 per minute")
def get_rollback_status(checkpoint_id):
    """Get status of a specific rollback checkpoint"""
    try:
        checkpoint = rollback_manager.active_checkpoints.get(checkpoint_id)
        
        if not checkpoint:
            # Try to load from disk
            checkpoint_path = rollback_manager.snapshot_dir / checkpoint_id
            metadata_file = checkpoint_path / 'metadata.json'
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    checkpoint = json.load(f)
            else:
                return jsonify({'error': 'Checkpoint not found'}), 404
        
        return jsonify({
            'success': True,
            'checkpoint': checkpoint
        })
        
    except Exception as e:
        logging.error(f"Error getting rollback status: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
