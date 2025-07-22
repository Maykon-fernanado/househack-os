import json
from pathlib import Path
from string import Template
from utils.gemini_api import call_gemini_api  # You write this wrapper for Gemini API calls

PROMPT_DIR = Path("prompts/gemini")

# Mapping task types to prompt filenames (no extension)
TASK_PROMPT_MAP = {
    "scrape_property": "property_data_scraper",
    "extract_rents": "rent_estimation_prompt",
    "find_comps": "comparable_property_analysis",
    "summarize_deal": "deal_summary_for_memo",
    "initial_filtering": "greenlight_gate_filter",
}

def load_prompt(prompt_name: str) -> str:
    """
    Load prompt from file (supports .txt or .yaml containing 'prompt:' key).
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
        raise FileNotFoundError(f"Prompt '{prompt_name}' not found in {PROMPT_DIR}")

def format_prompt(template_str: str, data: dict) -> str:
    """
    Use string.Template to safely substitute values into the prompt.
    """
    try:
        return Template(template_str).substitute(**data)
    except KeyError as e:
        missing = e.args[0]
        raise ValueError(f"Missing variable for prompt template: {missing}")

def run_gemini_task(task_type: str, data: dict) -> dict:
    """
    Core Gemini agent function. Takes task type and data input.
    Loads the prompt, formats it, sends it to Gemini, and returns output.
    """
    prompt_key = TASK_PROMPT_MAP.get(task_type)
    if not prompt_key:
        raise ValueError(f"Unknown Gemini task type: {task_type}")

    raw_prompt = load_prompt(prompt_key)
    formatted_prompt = format_prompt(raw_prompt, data)

    # This is where Gemini is actually called (you define the wrapper)
    response = call_gemini_api(formatted_prompt)

    return response

