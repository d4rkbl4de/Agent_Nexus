from typing import TypeVar, Generic, Type, Optional
import uuid

from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from common.db.base import CommonBase
from common.schemas import MeetingBase, MeetingInDB

# Define SQLAlchemy model type variable
ModelType = TypeVar("ModelType", bound=CommonBase)
# Define Pydantic Create/Update schema type variables (using MeetingBase as temporary generic placeholder)
CreateSchemaType = TypeVar("CreateSchemaType", bound=MeetingBase)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=MeetingBase)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete.
        """
        self.model = model

    def get(self, db: Session, id: uuid.UUID) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

# --- StudyFlow Lobe CRUDS (Placeholders) ---

class StudyRequestCRUD(CRUDBase[CommonBase, MeetingBase, MeetingBase]):
    pass

class StudyPlanCRUD(CRUDBase[CommonBase, MeetingBase, MeetingBase]):
    pass

class AnalysisResultCRUD(CRUDBase[CommonBase, MeetingBase, MeetingBase]):
    pass

class ActionItemCRUD(CRUDBase[CommonBase, MeetingBase, MeetingBase]):
    pass

# --- InsightMate Lobe CRUDS (Placeholder) ---

class MeetingCRUD(CRUDBase[CommonBase, MeetingBase, MeetingInDB]):
    pass
