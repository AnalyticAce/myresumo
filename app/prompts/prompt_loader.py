"""Load system prompts from markdown files."""
import os
from pathlib import Path
from typing import Dict


class PromptLoader:
    """Load system prompts from markdown files."""
    
    def __init__(self, prompts_dir: str = None):
        if prompts_dir is None:
            prompts_dir = os.path.join(os.path.dirname(__file__))
        self.prompts_dir = Path(prompts_dir)
    
    def load_prompt(self, prompt_name: str) -> str:
        """Load a specific prompt file.
        
        Args:
            prompt_name: Name of prompt file (without .md extension)
            
        Returns:
            str: Prompt content
            
        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        filepath = self.prompts_dir / f"{prompt_name}.md"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Prompt file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def load_all_prompts(self) -> Dict[str, str]:
        """Load all available prompts.
        
        Returns:
            dict: Mapping of prompt names to content
        """
        return {
            'analyzer': self.load_prompt('cv_analyzer'),
            'optimizer': self.load_prompt('cv_optimizer'),
            'cover_letter': self.load_prompt('cover_letter')
        }
