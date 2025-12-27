from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from common.schemas.errors import AppError, ErrorCategory, ErrorCode

class StudyAgentDefinition(BaseModel):
    agent_id: str
    name: str
    version: str
    subject_expertise: List[str]
    pedagogical_style: str = "Socratic"
    system_prompt: str
    difficulty_levels: List[str] = Field(default_factory=lambda: ["beginner", "intermediate", "advanced"])
    max_tokens_per_response: int = 1500
    temperature: float = 0.3
    metadata: Dict[str, Any] = Field(default_factory=dict)

class StudyRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StudyRegistry, cls).__new__(cls)
            cls._instance._tutors: Dict[str, StudyAgentDefinition] = {}
            cls._instance._load_default_tutors()
        return cls._instance

    def _load_default_tutors(self):
        math_tutor = StudyAgentDefinition(
            agent_id="sf-math-pro-01",
            name="Archimedes AI",
            version="1.0.2",
            subject_expertise=["Calculus", "Linear Algebra", "Probability"],
            pedagogical_style="Step-by-Step Derivation",
            system_prompt=(
                "You are Archimedes AI, a specialized mathematics tutor. "
                "Your goal is to guide students through complex derivations without giving the answer immediately. "
                "Always verify the student's understanding of the previous step before moving to the next."
            ),
            metadata={"focus": "STEM", "rigor": "High"}
        )
        
        coding_tutor = StudyAgentDefinition(
            agent_id="sf-python-coach-01",
            name="Kakarot's Python Sensei",
            version="2.1.0",
            subject_expertise=["Python", "Agentic AI", "FastAPI"],
            pedagogical_style="Project-Based Learning",
            system_prompt=(
                "You are a Senior Backend Architect. You teach Python by building real-world "
                "agentic systems. Use analogies related to DBZ, One Piece, or Batman where appropriate "
                "to explain complex data structures."
            ),
            metadata={"focus": "Software Engineering", "flavor": "Anime"}
        )

        self.register_tutor(math_tutor)
        self.register_tutor(coding_tutor)

    def register_tutor(self, definition: StudyAgentDefinition):
        if definition.agent_id in self._tutors:
            raise AppError(
                message=f"Tutor {definition.agent_id} already exists in registry.",
                category=ErrorCategory.INTERNAL_ERROR,
                code=ErrorCode.SYSTEM_PANIC
            )
        self._tutors[definition.agent_id] = definition

    def get_definition(self, agent_id: str) -> StudyAgentDefinition:
        tutor = self._tutors.get(agent_id)
        if not tutor:
            raise AppError(
                message=f"Study tutor {agent_id} not found.",
                category=ErrorCategory.NOT_FOUND_ERROR,
                code=ErrorCode.RESOURCE_NOT_FOUND
            )
        return tutor

    def list_tutors_by_expertise(self, subject: str) -> List[StudyAgentDefinition]:
        return [t for t in self._tutors.values() if subject in t.subject_expertise]

    def count_agents(self) -> int:
        return len(self._tutors)

study_registry = StudyRegistry()