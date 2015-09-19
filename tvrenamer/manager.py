"""Manages the execution of tasks using parallel processes."""
import logging

from oslo_config import cfg

from tvrenamer.common import _service
from tvrenamer.core import episode
from tvrenamer.core import watcher
from tvrenamer import processors

LOG = logging.getLogger(__name__)


class _RenamerService(_service.Service):

    def __init__(self, processor_mgr):
        super(_RenamerService, self).__init__()
        self.processor_mgr = processor_mgr
        self.watcher = watcher.FileWatcher()
        self.files = []

    def _on_done(self, gt, *args, **kwargs):
        finished_ep = gt.wait()
        self.processor_mgr.map_method('process', [finished_ep])

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


def _start(processor_mgr):
    outputs = []
    for file in watcher.retrieve_files():
        ep = episode.Episode(file)
        # process the work
        outputs.append(ep())

    processor_mgr.map_method('process', outputs)


def run():
    """Entry point to start the processing."""
    if cfg.CONF.cron:
        _service.launch(cfg.CONF, _RenamerService(processors.load())).wait()
    else:
        _start(processors.load())
