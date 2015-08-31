from oslo_config import cfg
from stevedore import driver

cfg.CONF.import_opt('lookup_service', 'tvrenamer.options')

_SERVICE_MANAGER = None


def get_service():
    """Load the configured service."""
    global _SERVICE_MANAGER

    if _SERVICE_MANAGER is None:
        _SERVICE_MANAGER = driver.DriverManager(namespace='data.services',
                                                name=cfg.CONF.lookup_service,
                                                invoke_on_load=True)
    return _SERVICE_MANAGER.driver
