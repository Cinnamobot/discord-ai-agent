"""
Example: Simple Discord AI Agent Bot

This example shows how to create and run a Discord AI agent bot
programmatically using the discord-ai-agent library.
"""

import os
from discord_ai_agent import DiscordAIBot, load_agent_config
from dotenv import load_dotenv


def main():
    # Load environment variables
    load_dotenv()

    # Get Discord bot token
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("Error: DISCORD_BOT_TOKEN not set in .env file")
        return

    # Load agent configuration
    agent_config = load_agent_config("./agents/default")

    print(f"🤖 Starting {agent_config.name}")
    print(f"📁 Workspace: {agent_config.workspace}")
    print(f"{'=' * 60}\n")

    # Create and run bot
    bot = DiscordAIBot(agent_config)
    bot.run(token)


if __name__ == "__main__":
    main()
