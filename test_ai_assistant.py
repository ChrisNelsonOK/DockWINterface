#!/usr/bin/env python3
"""Unit tests for AIAssistant"""

import unittest
import os
from unittest.mock import patch, MagicMock
import ai_assistant
from ai_assistant import AIAssistant


class TestAIAssistant(unittest.TestCase):
    """Test cases for AIAssistant class"""
    
    def setUp(self):
        """Set up test environment"""
        # Save original environment
        self.original_env = os.environ.get('OPENAI_API_KEY')
        # Set API key for testing
        os.environ['OPENAI_API_KEY'] = 'test-key-123'
    
    def tearDown(self):
        """Clean up after tests"""
        # Restore original environment
        if self.original_env:
            os.environ['OPENAI_API_KEY'] = self.original_env
        elif 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
    
    def test_initialization_without_api_key(self):
        """Test AIAssistant initialization without API key"""
        del os.environ['OPENAI_API_KEY']
        assistant = AIAssistant()
        self.assertIsNone(assistant.client)
    
    @patch('ai_assistant.OPENAI_AVAILABLE', True)
    @patch('ai_assistant.OpenAI')
    def test_initialization_with_api_key(self, mock_openai):
        """Test configuration analysis"""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Test response"))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create assistant with mocked client
        assistant = AIAssistant()
        
        # Test initialization
        self.assertIsNotNone(assistant.client)
        mock_openai.assert_called_once_with(api_key='test-key-123')
    
    @patch('ai_assistant.OPENAI_AVAILABLE', True)
    @patch('ai_assistant.OpenAI')
    def test_chat_success(self, mock_openai):
        """Test successful chat interaction"""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Test response"))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create assistant with mocked client
        assistant = AIAssistant()
        
        # Test chat
        response = assistant.chat("Hello")
        
        self.assertEqual(response, "Test response")
    
    @patch('ai_assistant.OPENAI_AVAILABLE', True)
    @patch('ai_assistant.OpenAI')
    def test_chat_error_handling(self, mock_openai):
        """Test chat error handling"""
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Create assistant with mocked client
        assistant = AIAssistant()
        
        # Test chat error
        response = assistant.chat("Test")
        
        self.assertIn("Sorry, I encountered an error", response)
    
    def test_chat_disabled(self):
        """Test chat when AI is disabled"""
        # Remove the API key to test disabled state
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        assistant = AIAssistant()
        
        response = assistant.chat("Hello")
        
        self.assertIn("AI assistant is not available", response)
    
    def test_chat_with_context_disabled(self):
        """Test chat with context when disabled"""
        # Remove the API key to test disabled state
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        assistant = AIAssistant()
        
        result = assistant.chat("Test", context={'key': 'value'})
        
        self.assertIsNotNone(result)
        self.assertIn('AI assistant is not available', result)
    
    @patch('ai_assistant.OPENAI_AVAILABLE', True)
    @patch('ai_assistant.OpenAI')
    def test_analyze_config(self, mock_openai):
        """Test configuration analysis"""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='{"recommendations": [], "security_notes": [], "performance_tips": [], "warnings": []}'))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create assistant with mocked client
        assistant = AIAssistant()
        
        # Test config analysis
        config = {
            'name': 'test-windows',
            'version': 'win11',
            'cpu_cores': 4,
            'ram_gb': 8
        }
        result = assistant.analyze_config(config)
        
        self.assertIsNotNone(result)
        self.assertIn('recommendations', result)
    
    def test_analyze_config_disabled(self):
        """Test config analysis when AI is disabled"""
        # Remove the API key to test disabled state
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        assistant = AIAssistant()
        
        config = {'name': 'test'}
        result = assistant.analyze_config(config)
        
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'AI assistant not available')
    
    @patch('ai_assistant.OPENAI_AVAILABLE', True)
    @patch('ai_assistant.OpenAI')
    def test_troubleshoot(self, mock_openai):
        """Test troubleshooting functionality"""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Try restarting the container"))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create assistant with mocked client
        assistant = AIAssistant()
        
        # Test troubleshooting        
        error = "Container won't start"
        result = assistant.troubleshoot(error)
        
        self.assertEqual(result, "Try restarting the container")
    
    def test_troubleshoot_disabled(self):
        """Test troubleshooting when AI is disabled"""
        # Remove the API key to test disabled state
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        assistant = AIAssistant()
        
        error = "Test error"
        result = assistant.troubleshoot(error)
        
        self.assertIsNotNone(result)
        self.assertIn('AI troubleshooting is not available', result)
    
    @patch('ai_assistant.OPENAI_AVAILABLE', True)
    @patch('ai_assistant.OpenAI')
    def test_model_configuration(self, mock_openai):
        """Test that correct model is configured"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Response"))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        
        assistant = AIAssistant()
        assistant.chat("Test")
        
        # Verify model parameter was used
        call_args = mock_client.chat.completions.create.call_args
        self.assertEqual(call_args[1]['model'], 'gpt-4o')
    
    @patch('ai_assistant.OPENAI_AVAILABLE', True)
    @patch('ai_assistant.OpenAI')
    def test_chat_with_context(self, mock_openai):
        """Test chat with context"""
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Response with context"))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        
        assistant = AIAssistant()
        
        # Test with context
        result = assistant.chat("Test", context={'key': 'value'})
        
        self.assertEqual(result, "Response with context")
    
    def test_assistant_initialization_without_key(self):
        """Test assistant initialization without API key"""
        # Remove API key
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        assistant = AIAssistant()
        
        # Assistant should initialize but with disabled state
        self.assertIsNone(assistant.client)



if __name__ == '__main__':
    unittest.main()
