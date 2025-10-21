"""
LLM Agent configuration and initialization.

This module provides the configured Pydantic AI agent for content extraction.
Configuration is loaded from /etc/secrets/vapourizer_llm.json with proper error handling.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import httpx
from anthropic import AsyncAnthropic
from pydantic_ai import Agent
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.models.anthropic import AnthropicModel

from llm.prompts import SYSTEM_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration file path
CONFIG_PATH = Path("/etc/secrets/.json")


class LLMConfigError(Exception):
    """Exception raised for LLM configuration errors."""
    pass


def load_llm_config() -> Dict[str, Any]:
    """
    Load LLM configuration from the secrets file.
    
    Returns:
        Dict[str, Any]: Configuration dictionary
        
    Raises:
        LLMConfigError: If configuration cannot be loaded or is invalid
    """
    try:
        if not CONFIG_PATH.exists():
            raise LLMConfigError(f"Configuration file not found: {CONFIG_PATH}")
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Validate required fields
        required_fields = ['base_url', 'api_key']
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            raise LLMConfigError(f"Missing required configuration fields: {missing_fields}")
        
        logger.info("LLM configuration loaded successfully")
        return config
        
    except json.JSONDecodeError as e:
        raise LLMConfigError(f"Invalid JSON in configuration file: {e}")
    except Exception as e:
        raise LLMConfigError(f"Failed to load configuration: {e}")


def create_http_client(config: Dict[str, Any]) -> httpx.AsyncClient:
    """
    Create an HTTP client with optional headers and certificate verification.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        httpx.AsyncClient: Configured HTTP client
    """
    client_kwargs = {}
    
    # Add headers if provided
    if 'headers' in config and config['headers']:
        client_kwargs['headers'] = config['headers']
        logger.info("HTTP client configured with custom headers")
    
    # Add certificate verification if provided
    if 'ca_certs_path' in config and config['ca_certs_path']:
        ca_path = Path(config['ca_certs_path'])
        if ca_path.exists():
            client_kwargs['verify'] = str(ca_path)
            logger.info(f"HTTP client configured with CA certificates: {ca_path}")
        else:
            logger.warning(f"CA certificates file not found: {ca_path}")
    
    return httpx.AsyncClient(**client_kwargs)


def create_agent() -> Agent:
    """
    Create and configure the Pydantic AI agent.
    
    Returns:
        Agent: Configured Pydantic AI agent
        
    Raises:
        LLMConfigError: If agent creation fails
    """
    try:
        # Load configuration
        config = load_llm_config()
        
        # Create HTTP client
        http_client = create_http_client(config)
        
        # Create Anthropic client
        anthropic_client = AsyncAnthropic(
            base_url=config['base_url'],
            http_client=http_client,
            api_key=config['api_key'],
        )
        
        # Create provider and model
        provider = AnthropicProvider(anthropic_client=anthropic_client)
        model = AnthropicModel(
            model_name="claude-sonnet-4",
            provider=provider,
        )
        
        # Create agent
        agent = Agent(
            model=model,
            instructions=SYSTEM_PROMPT,
            retries=3
        )
        
        logger.info("LLM agent created successfully")
        return agent
        
    except Exception as e:
        raise LLMConfigError(f"Failed to create agent: {e}")


# Create the agent instance
try:
    agent = create_agent()
except LLMConfigError as e:
    logger.error(f"Failed to initialize LLM agent: {e}")
    raise