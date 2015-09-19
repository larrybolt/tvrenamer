import logging

from oslo_config import cfg

from tvrenamer import cache
from tvrenamer.processors import base

LOG = logging.getLogger(__name__)


class CacheResults(base.ResultProcessorBase):
    """Result processor that cache output from execution."""

    @property
    def priority(self):
        """Processor priority used for sorting to determine execution order."""
        return 100

    @property
    def enabled(self):
        """Determines if a processor plugin is enabled for processing data."""
        return cfg.CONF.cache_enabled

    def process(self, data):
        """Process the results from episode processing.

        :param list data: result instances
        """
        for res in data:
            try:
                cache.save(res)
            except Exception:
                LOG.exception('failed to cache result: %s', res.status)
