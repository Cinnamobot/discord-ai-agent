"""
Multi-Bot Manager

Manages multiple Discord AI agent bots running simultaneously.
"""

import asyncio
import os
import yaml
import logging
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

import discord
from dotenv import load_dotenv

from discord_ai_agent.agent_loader import load_agent_config
from discord_ai_agent.discord_bot import DiscordAIBot

logger = logging.getLogger(__name__)


@dataclass
class BotConfig:
    """Configuration for a single bot instance"""

    name: str
    agent_path: str
    token: str
    enabled: bool = True


class MultiBotManager:
    """Manages multiple Discord AI agent bots"""

    def __init__(self, config_file: str):
        """
        Initialize multi-bot manager

        Args:
            config_file: Path to YAML configuration file
        """
        self.config_file = Path(config_file)
        self.bots: List[DiscordAIBot] = []
        self.bot_configs: List[BotConfig] = []
        self.tasks: List[asyncio.Task] = []

        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        self._load_config()

    def _load_config(self):
        """Load bot configurations from YAML file"""
        with open(self.config_file, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        # Load .env if specified
        env_file = config_data.get("env_file", ".env")
        if env_file:
            load_dotenv(env_file)

        # Parse bot configurations
        bots_config = config_data.get("bots", [])

        for bot_data in bots_config:
            name = bot_data.get("name")
            agent_path = bot_data.get("agent")
            token_key = bot_data.get("token_env", "DISCORD_BOT_TOKEN")
            enabled = bot_data.get("enabled", True)

            if not name or not agent_path:
                logger.warning(f"Skipping invalid bot configuration: {bot_data}")
                continue

            # Get token from environment or direct value
            if token_key.startswith("$"):
                # Environment variable reference
                token = os.getenv(token_key[1:])
            else:
                # Direct token or env var name
                token = os.getenv(token_key, token_key)

            if not token:
                logger.warning(f"Bot '{name}': Token not found for {token_key}")
                continue

            bot_config = BotConfig(
                name=name, agent_path=agent_path, token=token, enabled=enabled
            )

            self.bot_configs.append(bot_config)
            logger.info(f"Loaded bot config: {name} ({agent_path})")

    async def start_bot(self, bot_config: BotConfig):
        """
        Start a single bot instance

        Args:
            bot_config: Bot configuration
        """
        if not bot_config.enabled:
            logger.info(f"Bot '{bot_config.name}' is disabled, skipping...")
            return

        try:
            logger.info(f"🚀 Starting bot: {bot_config.name}")
            logger.info(f"   Agent: {bot_config.agent_path}")

            # Load agent config
            agent_config = load_agent_config(bot_config.agent_path)

            # Create bot instance
            intents = discord.Intents.default()
            intents.message_content = True
            intents.messages = True
            intents.guilds = True

            bot = DiscordAIBot(agent_config, intents=intents)
            self.bots.append(bot)

            # Start bot
            await bot.start(bot_config.token)

        except discord.LoginFailure:
            logger.error(f"❌ Bot '{bot_config.name}': Invalid token")
        except Exception as e:
            logger.error(f"❌ Bot '{bot_config.name}' failed: {e}", exc_info=True)

    async def start_all(self):
        """Start all configured bots"""
        logger.info(f"Starting {len(self.bot_configs)} bots...")

        # Create tasks for all bots
        self.tasks = [
            asyncio.create_task(self.start_bot(config)) for config in self.bot_configs
        ]

        # Wait for all bots to complete (or Ctrl+C)
        try:
            await asyncio.gather(*self.tasks)
        except KeyboardInterrupt:
            logger.info("\n⚠️ Received shutdown signal, stopping bots...")
            await self.stop_all()

    async def stop_all(self):
        """Stop all running bots"""
        logger.info("Stopping all bots...")

        # Close all bot connections
        for bot in self.bots:
            try:
                await bot.close()
                logger.info(f"✅ Stopped bot: {bot.agent_config.name}")
            except Exception as e:
                logger.error(f"Error stopping bot: {e}")

        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()

        logger.info("All bots stopped")

    def run(self):
        """Run the multi-bot manager (blocking)"""
        try:
            asyncio.run(self.start_all())
        except KeyboardInterrupt:
            logger.info("\nShutdown complete")


def main():
    """Test multi-bot manager"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m discord_ai_agent.multi_bot <config.yaml>")
        sys.exit(1)

    config_file = sys.argv[1]
    manager = MultiBotManager(config_file)
    manager.run()


if __name__ == "__main__":
    main()
