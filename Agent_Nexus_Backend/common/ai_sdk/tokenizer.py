from dataclasses import dataclass


@dataclass(frozen=True)
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


def count_tokens(text: str) -> int:
    return max(1, len(text.split()))
