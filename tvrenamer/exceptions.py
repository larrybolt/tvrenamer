"""Exceptions used through-out tvrenamer
"""


class BaseTvRenamerException(Exception):
    """Base exception all tvrenamers exceptions inherit from
    """
    pass


class InvalidPath(BaseTvRenamerException):
    """Raised when an argument is a non-existent file or directory path
    """
    pass


class NoValidFilesFoundError(BaseTvRenamerException):
    """Raised when no valid files are found. Effectively exits tvnamer
    """
    pass


class InvalidFilename(BaseTvRenamerException):
    """Raised when a file is parsed, but no episode info can be found
    """
    pass


class UserAbort(BaseTvRenamerException):
    """Base exception for config errors
    """
    pass


class BaseConfigError(BaseTvRenamerException):
    """Base exception for config errors
    """
    pass


class ConfigValueError(BaseConfigError):
    """Raised if the config file is malformed or unreadable
    """
    pass


class DataRetrievalError(BaseTvRenamerException):
    """Raised when an error (such as a network problem) prevents tvnamer
    from being able to retrieve data such as episode name
    """


class ShowNotFound(DataRetrievalError):
    """Raised when a show cannot be found
    """
    pass


class SeasonNotFound(DataRetrievalError):
    """Raised when requested season cannot be found
    """
    pass


class EpisodeNotFound(DataRetrievalError):
    """Raised when episode cannot be found
    """
    pass


class EpisodeNameNotFound(DataRetrievalError):
    """Raised when the name of the episode cannot be found
    """
    pass
