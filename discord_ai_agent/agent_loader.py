"""
Agent Configuration Loader

Loads agent configuration from agent.yaml and system_prompt.txt files.
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Union


@dataclass
class AgentConfig:
    """Agent configuration container"""

    name: str
    system_prompt: str
    allowed_commands: Optional[List[str]]
    workspace: Path
    agent_root: Path


def load_agent_config(agent_path: Union[str, Path]) -> AgentConfig:
    """
    Load agent configuration from directory

    Args:
        agent_path: Path to agent directory

    Returns:
        AgentConfig: Loaded agent configuration

    Raises:
        ValueError: If configuration files are not found
        FileNotFoundError: If agent directory doesn't exist
    """
    agent_path = Path(agent_path).resolve()

    if not agent_path.exists():
        raise FileNotFoundError(f"Agent directory not found: {agent_path}")

    # Load agent.yaml
    config_file = agent_path / "agent.yaml"
    if not config_file.exists():
        raise ValueError(f"agent.yaml not found in {agent_path}")

    with open(config_file, "r", encoding="utf-8") as f:
        agent_yaml = yaml.safe_load(f)

    # Get agent name
    name = agent_yaml.get("name", agent_path.name)

    # Get allowed commands
    allowed_commands = agent_yaml.get("allowed_commands")

    # Load base system prompt from config.yaml (if exists)
    config_path = Path(__file__).parent.parent / "config.yaml"
    base_system_prompt = ""
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
                base_system_prompt = config_data.get("base_system_prompt", "")
        except Exception:
            # If config.yaml can't be loaded or parsed, continue without base prompt
            pass

    # Load agent-specific system prompt
    # Priority: 1. system_prompt.txt file, 2. agent.yaml system_prompt field
    prompt_file = agent_path / "system_prompt.txt"
    if prompt_file.exists():
        with open(prompt_file, "r", encoding="utf-8") as f:
            agent_system_prompt = f.read()
    elif "system_prompt" in agent_yaml:
        agent_system_prompt = agent_yaml["system_prompt"]
    else:
        raise ValueError(
            f"Neither system_prompt.txt nor system_prompt field found in {agent_path}"
        )

    # Combine base system prompt with agent-specific prompt
    # Format: base_prompt + separator + agent_prompt
    if base_system_prompt.strip():
        system_prompt = (
            f"{base_system_prompt.strip()}\n\n"
            f"{'=' * 60}\n\n"
            f"{agent_system_prompt.strip()}"
        )
    else:
        system_prompt = agent_system_prompt

    # Determine workspace directory
    # Priority:
    # 1. agent.yaml workspace field (absolute path)
    # 2. AGENT_WORKSPACE_ROOT environment variable
    # 3. Default (agent_directory/workspace)
    workspace_config = agent_yaml.get("workspace")

    if workspace_config:
        # Specified in agent.yaml
        workspace = Path(workspace_config)
        if not workspace.is_absolute():
            # Relative path from agent root
            workspace = agent_path / workspace_config
    else:
        # Use AGENT_WORKSPACE_ROOT environment variable
        workspace_root = os.getenv("AGENT_WORKSPACE_ROOT")
        if workspace_root:
            workspace = Path(workspace_root) / name / "workspace"
        else:
            workspace = agent_path / "workspace"

    workspace.mkdir(parents=True, exist_ok=True)

    return AgentConfig(
        name=name,
        system_prompt=system_prompt,
        allowed_commands=allowed_commands,
        workspace=workspace,
        agent_root=agent_path,
    )
