import os
from typing import Any, Dict, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
from common.config.logging import logger
from common.ai_sdk.exceptions import ConfigurationException

class PromptManager:
    def __init__(self, template_dir: Optional[str] = None):
        if not template_dir:
            template_dir = os.path.join(os.path.dirname(__file__), "templates")
        
        if not os.path.exists(template_dir):
            try:
                os.makedirs(template_dir, exist_ok=True)
            except Exception as e:
                logger.warning(f"PROMPT_DIR_CREATE_FAILED | Path: {template_dir} | Error: {str(e)}")

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def render(self, template_name: str, **kwargs: Any) -> str:
        try:
            if not template_name.endswith(".j2"):
                template_name = f"{template_name}.j2"
            
            template = self.env.get_template(template_name)
            rendered = template.render(**kwargs)
            
            return rendered.strip()
        except TemplateNotFound:
            logger.error(f"PROMPT_TEMPLATE_NOT_FOUND | Template: {template_name}")
            raise ConfigurationException(f"Prompt template '{template_name}' not found.")
        except Exception as e:
            logger.error(f"PROMPT_RENDER_ERROR | Template: {template_name} | Error: {str(e)}")
            raise ConfigurationException(f"Failed to render prompt '{template_name}': {str(e)}")

    def render_system_and_user(self, domain: str, task: str, context: Dict[str, Any]) -> Dict[str, str]:
        system_path = f"{domain}/{task}/system"
        user_path = f"{domain}/{task}/user"
        
        return {
            "system": self.render(system_path, **context),
            "user": self.render(user_path, **context)
        }

    def list_templates(self) -> list:
        return self.env.list_templates()