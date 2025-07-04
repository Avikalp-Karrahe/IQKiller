import yaml
from typing import Dict, Any

class PromptLoader:
    def __init__(self, prompt_file: str = "prompts/v1.yaml"):
        with open(prompt_file, 'r') as f:
            self.prompts = yaml.safe_load(f)
    
    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """Get and format a prompt with variables"""
        template = self.prompts.get(prompt_name, "")
        return template.format(**kwargs)

# Global instance
prompt_loader = PromptLoader() 