"""
Discord AI Agent Bot - Library for creating AI-powered Discord bots

This package provides a framework for creating Discord bots powered by
Claude Agent SDK with support for multiple specialized agent profiles.

Usage:
    # As a library
    from discord_ai_agent import DiscordAIBot, load_agent_config

    # Create and run a bot
    config = load_agent_config("./agents/my-agent")
    bot = DiscordAIBot(config)
    bot.run(token)

    # Or use CLI
    $ discord-ai-agent --agent ./agents/my-agent
    $ discord-ai-agent --config bots.yaml  # Multiple bots
"""

__version__ = "3.0.3"
__author__ = "Discord AI Agent Team"
__license__ = "MIT"

# Main exports
from .discord_bot import DiscordAIBot
from .agent_loader import load_agent_config, AgentConfig
from .session_adapter import DiscordSessionManager, DiscordSession
from .rate_limit import RateLimiter
from . import file_manager

__all__ = [
    "DiscordAIBot",
    "load_agent_config",
    "AgentConfig",
    "DiscordSessionManager",
    "DiscordSession",
    "RateLimiter",
    "file_manager",
    "__version__",
]
