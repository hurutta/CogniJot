import os

from jinja2 import Environment, FileSystemLoader
from openai import OpenAI


class OpenAiCompatibleChatClient:
    def __init__(self):
        base_url = os.getenv("LLM_BASE_URL")
        api_key = os.getenv("LLM_API_KEY")
        model_name = os.getenv("LLM_MODEL_NAME")

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model_name = model_name

        self.jinja_env = Environment(
            loader=FileSystemLoader(searchpath=os.path.join(os.getcwd(), "prompt_templates"))
        )

    def render_prompt(self, template_name: str, context: dict) -> str:
        template = self.jinja_env.get_template(template_name)
        return template.render(context)

    def ask(self, user_prompt: str) -> str:
        rendered_user_prompt = self.render_prompt("error_finding.j2", {"prompt": user_prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=0,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": rendered_user_prompt}
            ]
        )
        return response.choices[0].message.content

    def format_markdown(self, user_prompt: str) -> str:
        rendered_user_prompt = self.render_prompt("markdown_formatter.j2", {"paragraph": user_prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=0,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": rendered_user_prompt}
            ]
        )
        return response.choices[0].message.content
