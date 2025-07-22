import json
from pathlib import Path
from string import Template
from utils.chatgpt_api import call_chatgpt_api  # Your OpenAI wrapper

PROMPT_DIR = Path("prompts/chatgpt")

TASK_PROMPT_MAP = {
    "bull_base_bear": "bull_base_bear_thesis",
    "conditional_memo": "conditional_memo_creator",
    "memo_finalizer": "final_decision_writer",
    "greenlight_verdict": "greenlight_verdict_writer",
    "scenario_generator": "multi_branch_scenario_builder"
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
        raise ValueError(f"Missing variable for ChatGPT prompt: {e.args[0]}")

def run_chatgpt_task(task_type: str, data: dict) -> dict:
    prompt_key = TASK_PROMPT_MAP.get(task_type)
    if not prompt_key:
        raise ValueError(f"Unknown ChatGPT task: {task_type}")

    raw_prompt = load_prompt(prompt_key)
    prompt = format_prompt(raw_prompt, data)

    response = call_chatgpt_api(prompt)

    return response

