from pydantic import BaseModel, Field
from typing import List, Literal

class StudyDocumentMetadata(BaseModel):
    user_id: str = Field(..., description="The ID of the user submitting the document.")
    document_name: str = Field(..., description="The original name of the uploaded file.")
    file_path: str = Field(..., description="The temporary or permanent path to the file on the server.")

class StudyResultSchema(BaseModel):
    key_concept: str = Field(description="The main concept addressed in the query.")
    grounded_answer: str = Field(description="The detailed answer based *only* on the retrieved documents.")
    confidence_score: float = Field(description="A score (0.0 to 1.0) indicating confidence in the answer based on context availability.")

class QuizAttempt(BaseModel):
    quiz_id: str
    user_id: str
    topic_key: str
    question: str
    user_answer: str
    correct_answer: str
    score: float
    timestamp: float

class StudyPlanInstruction(BaseModel):
    user_id: str
    instruction_type: Literal['REVIEW_TOPIC', 'NEXT_CONCEPT', 'GENERATE_QUIZ']
    target_topic: str
    confidence_level: float
    reasoning: str