import os
from typing import Dict, Any, Type, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = "gemini-2.5-flash"
OPENAI_MODEL = "gpt-4o-mini"

class LLMProvider:
    def __init__(self, model_name: str = OPENAI_MODEL):
        self.model_name = model_name
        self._chat_llm = self._initialize_chat_llm(model_name)
        self._structured_llm = self._initialize_structured_llm(model_name)

    def _initialize_chat_llm(self, model_name: str):
        return ChatOpenAI(model=model_name, temperature=0.1)

    def _initialize_structured_llm(self, model_name: str):
        return ChatOpenAI(model=model_name, temperature=0.0)

    @property
    def chat_llm(self):
        return self._chat_llm

    @property
    def structured_llm(self):
        return self._structured_llm

    async def generate_structured(self, prompt: str, schema: Type[BaseModel]) -> Dict[str, Any]:
        structured_chain = self._initialize_structured_llm(self.model_name).with_structured_output(schema)
        
        try:
            result = await structured_chain.ainvoke(prompt)
            return result.model_dump()
        except Exception as e:
            raise

_llm_provider_instance: Optional[LLMProvider] = None

def get_llm(model_name: str = OPENAI_MODEL) -> LLMProvider:
    global _llm_provider_instance
    if _llm_provider_instance is None:
        _llm_provider_instance = LLMProvider(model_name=model_name)
    return _llm_provider_instance

def get_structured_llm(*args, **kwargs) -> LLMProvider:
    return get_llm(*args, **kwargs)