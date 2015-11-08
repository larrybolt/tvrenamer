import pbr.version

PROJECT_NAME = __package__
__version__ = pbr.version.VersionInfo(PROJECT_NAME).version_string()

__all__ = ['__version__', 'PROJECT_NAME']
