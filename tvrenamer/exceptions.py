"""Exceptions used through-out tvrenamer."""


class BaseTvRenamerException(Exception):
    """Base exception all tvrenamers exceptions inherit from."""
    pass


class NoValidFilesFoundError(BaseTvRenamerException):
    """Raised when no valid files are found. Effectively exits tvrenamer."""
    pass


class InvalidFilename(BaseTvRenamerException):
    """Raised when a file is parsed, but no episode info can be found."""
    pass


class BaseConfigError(BaseTvRenamerException):
    """Base exception for config errors."""
    pass


class ConfigValueError(BaseConfigError):
    """Raised if the config file is malformed or unreadable."""
    pass


class DataRetrievalError(BaseTvRenamerException):
    """Raised when unable to retrieve data.

    An error (such as a network problem) prevents tvrenamer
    from being able to retrieve data such as episode name
    """


class ShowNotFound(DataRetrievalError):
    """Raised when a show cannot be found."""
    pass


class SeasonNotFound(DataRetrievalError):
    """Raised when requested season cannot be found."""
    pass


class EpisodeNotFound(DataRetrievalError):
    """Raised when episode cannot be found."""
    pass
