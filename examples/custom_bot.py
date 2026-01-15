"""
Example: Custom Discord AI Agent Bot with Advanced Configuration

This example demonstrates advanced bot configuration including:
- Custom intents
- Multiple agents
- Custom workspace
- Event handlers
"""

import os
import discord
from discord_ai_agent import DiscordAIBot, load_agent_config
from dotenv import load_dotenv


def main():
    # Load environment variables
    load_dotenv()

    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("Error: DISCORD_BOT_TOKEN not set")
        return

    # Load agent configuration
    agent_config = load_agent_config("./agents/market-analyst")

    # Custom intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.messages = True
    intents.guilds = True
    intents.members = True  # For user mentions
    intents.presences = False  # Disable if not needed

    # Create bot with custom intents
    bot = DiscordAIBot(agent_config, intents=intents)

    # Add custom event handlers
    @bot.event
    async def on_guild_join(guild):
        print(f"✅ Bot joined guild: {guild.name} (ID: {guild.id})")

    @bot.event
    async def on_guild_remove(guild):
        print(f"❌ Bot removed from guild: {guild.name}")

    @bot.event
    async def on_error(event, *args, **kwargs):
        print(f"⚠️ Error in {event}: {args}, {kwargs}")

    print(f"🤖 Starting Advanced Bot: {agent_config.name}")
    print(f"📁 Workspace: {agent_config.workspace}")
    print(f"🔧 Custom Intents: Enabled")
    print(f"{'=' * 60}\n")

    # Run bot
    bot.run(token)


if __name__ == "__main__":
    main()
