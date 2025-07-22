import json
from pathlib import Path
from string import Template
from utils.claude_api import call_claude_api  # You write this Claude wrapper

PROMPT_DIR = Path("prompts/claude")

TASK_PROMPT_MAP = {
    "fact_check_memo": "validate_investment_memo",
    "correct_numbers": "piti_tax_rent_corrector",
    "simplify_output": "simplify_for_layman",
    "generate_synthesis": "strategic_synthesis",
    "tier_filter": "apply_greenlight_filters",
}

def load_prompt(prompt_name: str) -> str:
    """
    Load prompt file from .txt or .yaml with 'prompt:' key.
    """
    txt_path = PROMPT_DIR / f"{prompt_name}.txt"
    yaml_path = PROMPT_DIR / f"{prompt_name}.yaml"

    if txt_path.exists():
        return txt_path.read_text()

    elif yaml_path.exists():
        import yaml
        with open(yaml_path, "r") as f:
            parsed = yaml.safe_load(f)
            return parsed.get("prompt", "")

    else:
        raise FileNotFoundError(f"Prompt '{prompt_name}' not found.")

def format_prompt(template_str: str, data: dict) -> str:
    """
    Inject variables into the prompt using string.Template.
    """
    try:
        return Template(template_str).substitute(**data)
    except KeyError as e:
        raise ValueError(f"Missing variable for Claude prompt: {e.args[0]}")

def run_claude_task(task_type: str, data: dict) -> dict:
    """
    Core Claude agent router. Handles task-specific logic and Claude interaction.
    """
    prompt_key = TASK_PROMPT_MAP.get(task_type)
    if not prompt_key:
        raise ValueError(f"Unknown Claude task: {task_type}")

    raw_prompt = load_prompt(prompt_key)
    prompt = format_prompt(raw_prompt, data)

    response = call_claude_api(prompt)

    return response

