"""
Discord Slash Commands

Implements slash commands for agent selection and channel configuration.
"""

import logging
from typing import List, TYPE_CHECKING

import discord
from discord import app_commands

if TYPE_CHECKING:
    from .discord_bot import DiscordAIBot

logger = logging.getLogger(__name__)


async def setup_commands(bot: "DiscordAIBot"):
    """
    Register all slash commands with the bot

    Args:
        bot: DiscordAIBot instance
    """

    @bot.tree.command(
        name="create-thread", description="エージェントを選択して新しいスレッドを作成"
    )
    @app_commands.describe(
        agent="使用するエージェント",
        message="最初のメッセージ (オプション)",
    )
    async def create_thread(
        interaction: discord.Interaction,
        agent: str,
        message: str = "",
    ):
        """Create a new thread with selected agent"""
        try:
            # Validate agent exists
            if not bot.agent_registry.has_agent(agent):
                available = ", ".join(
                    [a.name for a in bot.agent_registry.list_agents()]
                )
                await interaction.response.send_message(
                    f"❌ エージェント `{agent}` が見つかりません\n"
                    f"利用可能なエージェント: {available}",
                    ephemeral=True,
                )
                return

            # Defer response (thread creation may take time)
            await interaction.response.defer(ephemeral=False)

            # Create a message in the channel for thread creation
            # This is needed because Discord threads must be created from a message
            user_mention = interaction.user.mention
            message_content = f"{user_mention} {message}".strip()

            # Create the message
            channel_msg = await interaction.channel.send(message_content)

            # Create thread with specified agent
            await bot.create_thread_and_start(channel_msg, agent_name=agent)

            # Send followup confirmation
            await interaction.followup.send(
                f"✅ エージェント `{agent}` でスレッドを作成しました!",
                ephemeral=True,
            )

            logger.info(
                f"User {interaction.user.id} created thread with agent '{agent}'"
            )

        except Exception as e:
            logger.error(f"Error in create-thread command: {e}", exc_info=True)
            try:
                await interaction.followup.send(
                    f"❌ スレッドの作成中にエラーが発生しました: {str(e)}",
                    ephemeral=True,
                )
            except:
                # If followup fails, try to respond directly
                await interaction.response.send_message(
                    f"❌ スレッドの作成中にエラーが発生しました: {str(e)}",
                    ephemeral=True,
                )

    @create_thread.autocomplete("agent")
    async def agent_autocomplete(
        interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        """Autocomplete for agent names"""
        try:
            agents = bot.agent_registry.list_agents()
            # Filter agents based on current input
            filtered = [
                agent for agent in agents if current.lower() in agent.name.lower()
            ]
            # Sort alphabetically
            filtered.sort(key=lambda a: a.name)
            # Return choices (max 25 due to Discord limit)
            return [
                app_commands.Choice(
                    name=f"{agent.name}"
                    + (f" - {agent.description}" if agent.description else ""),
                    value=agent.name,
                )
                for agent in filtered[:25]
            ]
        except Exception as e:
            logger.error(f"Error in agent autocomplete: {e}")
            return []

    @bot.tree.command(
        name="settings", description="チャンネルのデフォルトエージェントを設定"
    )
    @app_commands.describe(
        agent="デフォルトで使用するエージェント (空白でクリア)",
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def settings(
        interaction: discord.Interaction,
        agent: str = None,
    ):
        """Configure channel default agent"""
        try:
            if agent is None:
                # Show current settings
                settings = bot.session_store.get_channel_settings(
                    interaction.channel_id
                )
                if settings and settings.default_agent:
                    current = settings.default_agent
                    await interaction.response.send_message(
                        f"📋 このチャンネルのデフォルトエージェント: `{current}`\n\n"
                        f"変更するには `/settings agent:<エージェント名>` を実行してください。",
                        ephemeral=True,
                    )
                else:
                    default_agent = bot.agent_registry.get_default_agent_name()
                    await interaction.response.send_message(
                        f"📋 このチャンネルのデフォルトエージェント: 未設定\n"
                        f"現在は全体のデフォルト (`{default_agent}`) が使用されます。\n\n"
                        f"設定するには `/settings agent:<エージェント名>` を実行してください。",
                        ephemeral=True,
                    )
                return

            # Clear settings if empty string
            if agent == "":
                bot.session_store.set_channel_default_agent(
                    channel_id=interaction.channel_id,
                    guild_id=interaction.guild_id,
                    agent_name=None,
                )
                default_agent = bot.agent_registry.get_default_agent_name()
                await interaction.response.send_message(
                    f"✅ デフォルトエージェントをクリアしました\n"
                    f"全体のデフォルト (`{default_agent}`) が使用されます。",
                    ephemeral=True,
                )
                logger.info(
                    f"User {interaction.user.id} cleared default agent for channel {interaction.channel_id}"
                )
                return

            # Validate agent exists
            if not bot.agent_registry.has_agent(agent):
                available = ", ".join(
                    [a.name for a in bot.agent_registry.list_agents()]
                )
                await interaction.response.send_message(
                    f"❌ エージェント `{agent}` が見つかりません\n"
                    f"利用可能なエージェント: {available}",
                    ephemeral=True,
                )
                return

            # Update settings
            bot.session_store.set_channel_default_agent(
                channel_id=interaction.channel_id,
                guild_id=interaction.guild_id,
                agent_name=agent,
            )

            await interaction.response.send_message(
                f"✅ このチャンネルのデフォルトエージェントを `{agent}` に設定しました\n"
                f"メンション時にこのエージェントが使用されます。",
                ephemeral=True,
            )

            logger.info(
                f"User {interaction.user.id} set default agent for channel {interaction.channel_id} to '{agent}'"
            )

        except discord.errors.Forbidden:
            await interaction.response.send_message(
                "❌ この操作を実行する権限がありません (チャンネル管理権限が必要です)",
                ephemeral=True,
            )
        except Exception as e:
            logger.error(f"Error in settings command: {e}", exc_info=True)
            try:
                await interaction.response.send_message(
                    f"❌ 設定中にエラーが発生しました: {str(e)}",
                    ephemeral=True,
                )
            except:
                pass

    @settings.autocomplete("agent")
    async def settings_agent_autocomplete(
        interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        """Autocomplete for settings agent parameter"""
        try:
            agents = bot.agent_registry.list_agents()
            choices = []

            # Add clear option if user is typing something that matches
            if (
                current.lower() in "clear"
                or current.lower() in "クリア"
                or current == ""
            ):
                choices.append(
                    app_commands.Choice(
                        name="(クリア - デフォルト設定を解除)", value=""
                    )
                )

            # Filter and add agent choices
            filtered = [
                agent for agent in agents if current.lower() in agent.name.lower()
            ]
            filtered.sort(key=lambda a: a.name)

            for agent in filtered:
                if len(choices) >= 25:  # Discord limit
                    break
                choice_name = agent.name
                if agent.description:
                    choice_name += f" - {agent.description}"
                choices.append(app_commands.Choice(name=choice_name, value=agent.name))

            return choices
        except Exception as e:
            logger.error(f"Error in settings autocomplete: {e}")
            return []

    logger.info("Slash commands registered")
