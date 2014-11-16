__all__ = ['__version__', 'PROJECT_NAME']

import pbr.version

PROJECT_NAME = 'tvrenamer'

version_info = pbr.version.VersionInfo(PROJECT_NAME)
try:
    __version__ = version_info.version_string()
except AttributeError:
    __version__ = None
