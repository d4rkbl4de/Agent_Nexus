import re
from typing import Dict


class PromptTemplate:
    _pattern = re.compile(r"{(\w+)}")

    def __init__(self, template: str):
        self.template = template

    def render(self, variables: Dict[str, str]) -> str:
        def replacer(match: re.Match) -> str:
            key = match.group(1)
            if key not in variables:
                raise ValueError(key)
            return str(variables[key])

        return self._pattern.sub(replacer, self.template)


SYSTEM_BASE_PROMPT = PromptTemplate(
    "You are an autonomous AI agent operating inside Agent Nexus."
)

PLANNING_PROMPT = PromptTemplate(
    "Decompose the following goal into executable steps.\n\nGoal:\n{goal}\n\nReturn a numbered plan."
)
