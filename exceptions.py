"""
Custom exceptions for the Biography Video Prompt Generator.
"""


class BiographyGeneratorError(Exception):
    """Base exception for all biography generator errors."""
    pass


class APIError(BiographyGeneratorError):
    """Exception raised when API calls fail."""
    pass


class RateLimitError(APIError):
    """Exception raised when API rate limit is exceeded."""
    pass


class ConfigurationError(BiographyGeneratorError):
    """Exception raised when configuration is invalid."""
    pass


class FileOperationError(BiographyGeneratorError):
    """Exception raised when file operations fail."""
    pass


class TextProcessingError(BiographyGeneratorError):
    """Exception raised when text processing fails."""
    pass


class ValidationError(BiographyGeneratorError):
    """Exception raised when validation fails."""
    pass
