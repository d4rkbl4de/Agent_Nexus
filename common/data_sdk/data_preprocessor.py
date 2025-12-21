import re


class DataPreprocessor:
    def normalize(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def clean(self, text: str) -> str:
        text = re.sub(r"[^\x00-\x7F]+", " ", text)
        return self.normalize(text)

    def process(self, text: str) -> str:
        return self.clean(text)
