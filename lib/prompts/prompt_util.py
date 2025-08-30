import os
from pathlib import Path

# Loads a prompt from the prompts directory
def load_system_prompt(prompt_name: str) -> str:
    with open(f"{Path(__file__).resolve().parent}/{prompt_name}.md", "r") as f:
        return f.read()