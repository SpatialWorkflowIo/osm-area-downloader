"""Project specific exceptions."""


class DownloadError(Exception):
    """Raised when network download or conversion fails."""


class InputError(Exception):
    """Raised when CLI input cannot be parsed or validated."""

