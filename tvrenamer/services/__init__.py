from oslo_config import cfg
from stevedore import driver

_SERVICE_MANAGER = None


def get_service():
    """Load the configured service."""
    global _SERVICE_MANAGER

    if _SERVICE_MANAGER is None:
        _SERVICE_MANAGER = driver.DriverManager(
            namespace='tvrenamer.data.services',
            name=cfg.CONF.lookup_service,
            invoke_on_load=True)
    return _SERVICE_MANAGER.driver


def load_service_opts(conf):
    """Load configuration options for services."""
    conf.import_group('tvdb', 'tvdbapi_client.options')
