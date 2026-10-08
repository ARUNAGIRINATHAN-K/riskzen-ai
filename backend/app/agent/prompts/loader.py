"""Prompt Template Loader for AI Agent."""
import os
from pathlib import Path
from typing import Any, Dict

PROMPTS_DIR = Path(__file__).parent


def load_prompt_template(template_name: str, variables: Dict[str, Any]) -> str:
    """Load a markdown prompt template and substitute format variables."""
    file_path = PROMPTS_DIR / f"{template_name}.md"
    if not file_path.exists():
        raise FileNotFoundError(f"Prompt template '{template_name}.md' not found at {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Safe variable replacement
    for key, val in variables.items():
        placeholder = f"{{{key}}}"
        template = template.replace(placeholder, str(val))

    return template
