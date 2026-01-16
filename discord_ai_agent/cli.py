"""
Discord AI Agent - Command Line Interface

Provides CLI commands for running single or multiple Discord AI agent bots.
"""

import sys
import os
import argparse
import asyncio
from pathlib import Path
from typing import Optional, List
import logging

from dotenv import load_dotenv

# Setup logger
logger = logging.getLogger(__name__)


def setup_environment():
    """Setup environment for CLI execution"""
    # Disable output buffering for real-time display
    os.environ["PYTHONUNBUFFERED"] = "1"

    # Windows UTF-8 encoding setup
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


def run_single_bot(agents_dir: str = "./agents", token: Optional[str] = None):
    """
    Run a single Discord AI agent bot with multi-agent support

    Args:
        agents_dir: Path to agents directory containing all agents (default: ./agents)
        token: Discord bot token (optional, can use .env)
    """
    from discord_ai_agent.discord_bot import main as bot_main

    # Load .env file
    load_dotenv()

    # Override token if provided
    if token:
        os.environ["DISCORD_BOT_TOKEN"] = token

    # Set agents directory
    sys.argv = ["discord-ai-agent", agents_dir]

    print(f"🚀 Starting Discord AI Agent Bot")
    print(f"📁 Agents Directory: {agents_dir}")
    print(f"{'=' * 60}\n")

    bot_main()


def run_multiple_bots(config_file: str):
    """
    Run multiple Discord AI agent bots from configuration file

    Args:
        config_file: Path to bots configuration YAML file
    """
    from discord_ai_agent.multi_bot import MultiBotManager

    print(f"🚀 Starting Multiple Discord AI Agent Bots")
    print(f"📁 Config: {config_file}")
    print(f"{'=' * 60}\n")

    manager = MultiBotManager(config_file)
    manager.run()


def main():
    """Main CLI entry point"""
    setup_environment()

    parser = argparse.ArgumentParser(
        description="Discord AI Agent Bot - AI-powered Discord bots with Claude Agent SDK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run single bot with all agents in directory
  discord-ai-agent
  discord-ai-agent ./agents
  discord-ai-agent --agents ./my-agents
  
  # Run single bot with token
  discord-ai-agent --agents ./agents --token YOUR_TOKEN
  
  # Run multiple bots from config file
  discord-ai-agent --config bots.yaml
  
  # Show version
  discord-ai-agent --version

For more information, visit: https://github.com/yourusername/discord-ai-agent
        """,
    )

    parser.add_argument(
        "agents_dir", nargs="?", help="Path to agents directory (default: ./agents)"
    )

    parser.add_argument(
        "-a", "--agents", dest="agents_dir_arg", help="Path to agents directory"
    )

    parser.add_argument(
        "-c",
        "--config",
        dest="config_file",
        help="Path to multi-bot configuration YAML file",
    )

    parser.add_argument(
        "-t", "--token", dest="token", help="Discord bot token (overrides .env)"
    )

    parser.add_argument(
        "-v", "--version", action="version", version=f"discord-ai-agent {get_version()}"
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    # Determine mode
    if args.config_file:
        # Multi-bot mode
        run_multiple_bots(args.config_file)
    else:
        # Single bot mode with multi-agent support
        agents_dir = args.agents_dir_arg or args.agents_dir or "./agents"
        run_single_bot(agents_dir, args.token)


def get_version() -> str:
    """Get package version"""
    try:
        from discord_ai_agent import __version__

        return __version__
    except ImportError:
        return "unknown"


if __name__ == "__main__":
    main()
