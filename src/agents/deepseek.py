import json
from pathlib import Path
from string import Template
from utils.deepseek_api import call_deepseek_api  # Your DeepSeek wrapper

PROMPT_DIR = Path("prompts/deepseek")

TASK_PROMPT_MAP = {
    "adversarial_thesis": "critique_thesis",
    "fragility_detector": "risk_trap_identifier",
    "reverse_engineer": "logic_reversal_mapper",
    "opponent_simulator": "bearish_actor_simulation"
}

def load_prompt(prompt_name: str) -> str:
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
    try:
        return Template(template_str).substitute(**data)
    except KeyError as e:
        raise ValueError(f"Missing variable for DeepSeek prompt: {e.args[0]}")

def run_deepseek_task(task_type: str, data: dict) -> dict:
    prompt_key = TASK_PROMPT_MAP.get(task_type)
    if not prompt_key:
        raise ValueError(f"Unknown DeepSeek task: {task_type}")

    raw_prompt = load_prompt(prompt_key)
    prompt = format_prompt(raw_prompt, data)

    response = call_deepseek_api(prompt)

    return response

