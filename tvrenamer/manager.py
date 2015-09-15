"""Manages the execution of tasks using parallel processes."""
import logging

from oslo_config import cfg
import six

from tvrenamer import cache
from tvrenamer.common import _service
from tvrenamer.common import table
from tvrenamer.core import episode
from tvrenamer.core import watcher

LOG = logging.getLogger(__name__)


def _handle_results(results):

    fields = []
    for res in results:

        _cache_result(res)

        # if logging is not enabled then no need to
        # go any further.
        if LOG.isEnabledFor(logging.INFO):
            for epname, data in six.iteritems(res.status):
                fields.append(
                    [data.get('state'),
                     epname,
                     data.get('formatted_filename'),
                     data.get('messages')])

    if LOG.isEnabledFor(logging.INFO) and fields:
        table.write_output(fields)


def _cache_result(res):

    if cfg.CONF.cache_enabled:
        try:
            cache.save(res)
        except Exception:
            LOG.exception('failed to cache result: %s', res.status)


class _RenamerService(_service.Service):

    def __init__(self):
        super(_RenamerService, self).__init__()
        self.watcher = watcher.FileWatcher()
        self.files = []

    def _on_done(self, gt, *args, **kwargs):
        finished_ep = gt.wait()
        _cache_result(finished_ep)

    def _files_found(self, gt, *args, **kwargs):
        self.files = gt.wait()

    def _process_files(self):
        for file in self.files:
            th = self.tg.add_thread(episode.Episode(file))
            th.link(self._on_done)

        self.tg.wait()

    def start(self):
        super(_RenamerService, self).start()
        LOG.info('RenamerService starting...')

        while True:
            th = self.tg.add_thread(self.watcher.run)
            th.link(self._files_found)
            self.tg.wait()
            self._process_files()

    def stop(self):
        LOG.info('RenamerService shutting down.')
        super(_RenamerService, self).stop()


def start():
    """Entry point to start the processing."""

    results = []
    for file in watcher.retrieve_files():
        ep = episode.Episode(file)
        # process the work
        results.append(ep())
    _handle_results(results)


def start_daemon():
    _service.launch(cfg.CONF, _RenamerService()).wait()
