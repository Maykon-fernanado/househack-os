import json
from pathlib import Path
from string import Template

# Stub function to call an LLM API — replace with your actual LLM wrapper
def call_llm_api(prompt: str, agent_name: str) -> dict:
    print(f"Calling LLM for agent {agent_name} with prompt:")
    print(prompt)
    # Return a mocked response for now
    return {"response": f"Mocked response from {agent_name}"}

PROMPT_DIR = Path("prompts/adversarial")

# Map adversarial agent names to their prompt file names
AGENT_PROMPTS = {
    "socrates": "socrates_prompt.txt",
    "machiavelli": "machiavelli_prompt.txt",
    "bayes": "bayes_prompt.txt",
    "murphy": "murphy_prompt.txt"
}

def load_prompt(agent_name: str) -> str:
    prompt_file = PROMPT_DIR / AGENT_PROMPTS.get(agent_name.lower())
    if not prompt_file or not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file for agent '{agent_name}' not found.")
    return prompt_file.read_text()

def format_prompt(template_str: str, data: dict) -> str:
    try:
        return Template(template_str).substitute(**data)
    except KeyError as e:
        raise ValueError(f"Missing variable for prompt template: {e.args[0]}")

def run_adversarial_agent(agent_name: str, investment_memo: str) -> dict:
    """
    Run the given adversarial agent prompt on the investment memo.

    Args:
        agent_name (str): One of 'socrates', 'machiavelli', 'bayes', 'murphy'.
        investment_memo (str): The text of the investment memo to critique.

    Returns:
        dict: Response from the LLM API or mocked response.
    """
    prompt_template = load_prompt(agent_name)
    prompt = format_prompt(prompt_template, {"memo": investment_memo})
    response = call_llm_api(prompt, agent_name)
    return response

