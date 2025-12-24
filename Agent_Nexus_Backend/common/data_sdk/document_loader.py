from pathlib import Path
from typing import List
from .document_model import Document


class DocumentLoader:
    def load_text(self, path: str) -> Document:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(path)
        content = file_path.read_text(encoding="utf-8")
        return Document(
            content=content,
            metadata={"source": str(file_path.resolve())},
        )

    def load_directory(self, path: str, suffix: str = ".txt") -> List[Document]:
        base = Path(path)
        if not base.exists():
            raise FileNotFoundError(path)
        documents = []
        for file in base.rglob(f"*{suffix}"):
            documents.append(self.load_text(str(file)))
        return documents
