__all__ = ['__version__', 'PROJECT_NAME']

import pbr.version

PROJECT_NAME = __package__

version_info = pbr.version.VersionInfo(PROJECT_NAME)
__version__ = version_info.version_string()
