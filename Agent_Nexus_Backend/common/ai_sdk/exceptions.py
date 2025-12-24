class LLMError(Exception):
    pass


class RateLimitError(LLMError):
    pass


class ProviderError(LLMError):
    pass


class ConfigurationError(LLMError):
    pass
