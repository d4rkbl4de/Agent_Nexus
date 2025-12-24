from abc import ABC, abstractmethod
from langgraph.graph import StateGraph

class BaseAgentLobe(ABC):
    def __init__(self, name: str):
        self.name = name
        self.builder = StateGraph(self.get_state_schema())

    @abstractmethod
    def get_state_schema(self):
        pass

    @abstractmethod
    def build_graph(self):
        pass