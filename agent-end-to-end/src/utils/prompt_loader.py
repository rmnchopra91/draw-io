import os
import yaml

def load_prompt(agent_type: str, version: str) -> str | None:
    """
    Load a YAML prompt for a given agent type and version.

    Directory layout example:
      src/prompts/simple/v1.yaml

    Expected YAML structure:
      prompt: |
        You are a helpful assistant...
    or
      - role: system
        content: You are a helpful assistant.
      - role: user
        content: Hello!
    """

    # Navigate from utils → ../prompts/<agent_type>/<version>.yaml
    base_dir = os.path.dirname(os.path.dirname(__file__))
    prompt_path = os.path.join(base_dir, "prompts", agent_type, f"{version}.yaml")

    print(f"base_dir : ", base_dir)
    print(f"prompt_path : ", prompt_path)

    if not os.path.exists(prompt_path):
        return None

    with open(prompt_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Case 1: Dictionary with "prompt" key
    if isinstance(data, dict) and "prompt" in data:
        return data["prompt"].strip()

    # Case 2: List of role/content messages
    if isinstance(data, list):
        return "\n".join(
            item.get("content", "").strip() for item in data if isinstance(item, dict)
        )

    # Fallback
    return str(data).strip() if data else None
