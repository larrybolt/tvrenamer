"""Manages the processing of media files."""
import logging

from tvrenamer.core import episode
from tvrenamer.core import watcher
from tvrenamer import processors

LOG = logging.getLogger(__name__)


def _start(processor_mgr):
    LOG.debug('tvrenamer starting...')

    outputs = []
    for afile in watcher.retrieve_files():
        next_ep = episode.Episode(afile)
        # process the work
        outputs.append(next_ep())

    processor_mgr.map_method('process', outputs)
    LOG.debug('tvrenamer finished')


def run():
    """Entry point to start the processing."""
    _start(processors.load())
