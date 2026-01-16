"""
Agent Registry System

Manages multiple agents by auto-discovering them from the agents directory.
Provides on-demand loading of agent configurations.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from .agent_loader import AgentConfig, load_agent_config

logger = logging.getLogger(__name__)


@dataclass
class AgentInfo:
    """Agent metadata for listing"""

    name: str
    path: Path
    description: Optional[str] = None


class AgentRegistry:
    """
    Registry for managing multiple agents.

    Automatically discovers agents in the agents directory and loads them on-demand.
    """

    def __init__(self, agents_dir: str = "./agents"):
        """
        Initialize the agent registry.

        Args:
            agents_dir: Path to the directory containing agent subdirectories
        """
        self.agents_dir = Path(agents_dir).resolve()
        self._agent_cache: Dict[str, AgentConfig] = {}
        self._agent_info: Dict[str, AgentInfo] = {}

        # Discover agents on initialization
        self.discover_agents()

    def discover_agents(self) -> List[AgentInfo]:
        """
        Discover all agents in the agents directory.

        Returns:
            List of AgentInfo objects for discovered agents

        Raises:
            FileNotFoundError: If agents directory doesn't exist
        """
        if not self.agents_dir.exists():
            raise FileNotFoundError(f"Agents directory not found: {self.agents_dir}")

        self._agent_info.clear()
        discovered = []

        # Scan each subdirectory in agents/
        for entry in self.agents_dir.iterdir():
            if not entry.is_dir():
                continue

            # Check if it's a valid agent directory (has agent.yaml)
            agent_yaml = entry / "agent.yaml"
            if not agent_yaml.exists():
                logger.debug(f"Skipping {entry.name}: no agent.yaml found")
                continue

            agent_name = entry.name

            # Try to load basic info (description) from agent.yaml
            description = None
            try:
                import yaml

                with open(agent_yaml, "r", encoding="utf-8") as f:
                    yaml_data = yaml.safe_load(f)
                    description = yaml_data.get("description")
            except Exception as e:
                logger.warning(f"Failed to read description from {agent_yaml}: {e}")

            info = AgentInfo(name=agent_name, path=entry, description=description)
            self._agent_info[agent_name] = info
            discovered.append(info)

            logger.info(f"Discovered agent: {agent_name}")

        logger.info(f"Discovered {len(discovered)} agent(s)")
        return discovered

    def get_agent(self, name: str) -> AgentConfig:
        """
        Get agent configuration by name.

        Loads the agent on-demand and caches it for subsequent calls.

        Args:
            name: Agent name (directory name)

        Returns:
            AgentConfig: Loaded agent configuration

        Raises:
            ValueError: If agent is not found or invalid
        """
        # Check if agent exists in discovered agents
        if name not in self._agent_info:
            available = ", ".join(self._agent_info.keys())
            raise ValueError(f"Agent '{name}' not found. Available agents: {available}")

        # Return cached config if available
        if name in self._agent_cache:
            logger.debug(f"Using cached config for agent: {name}")
            return self._agent_cache[name]

        # Load agent config
        agent_info = self._agent_info[name]
        logger.info(f"Loading agent config: {name}")

        try:
            config = load_agent_config(agent_info.path)
            self._agent_cache[name] = config
            return config
        except Exception as e:
            logger.error(f"Failed to load agent '{name}': {e}")
            raise ValueError(f"Failed to load agent '{name}': {e}") from e

    def list_agents(self) -> List[AgentInfo]:
        """
        List all discovered agents.

        Returns:
            List of AgentInfo objects
        """
        return list(self._agent_info.values())

    def reload_agents(self) -> List[AgentInfo]:
        """
        Reload agent list from disk and clear cache.

        Useful for detecting newly added agents without restarting the bot.

        Returns:
            List of AgentInfo objects for discovered agents
        """
        logger.info("Reloading agents from disk")
        self._agent_cache.clear()
        return self.discover_agents()

    def has_agent(self, name: str) -> bool:
        """
        Check if an agent exists.

        Args:
            name: Agent name

        Returns:
            True if agent exists, False otherwise
        """
        return name in self._agent_info

    def get_default_agent_name(self) -> str:
        """
        Get the default agent name.

        Returns:
            "default" if it exists, otherwise the first available agent name

        Raises:
            ValueError: If no agents are available
        """
        if not self._agent_info:
            raise ValueError("No agents available")

        if "default" in self._agent_info:
            return "default"

        # Return first agent alphabetically
        return sorted(self._agent_info.keys())[0]
