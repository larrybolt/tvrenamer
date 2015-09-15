"""Command-line interface to the TvRenamer APIs"""
import os
import tempfile

import lockfile
from oslo_config import cfg

from tvrenamer import manager
from tvrenamer import service


@lockfile.locked(os.path.join(tempfile.gettempdir(), __package__), timeout=10)
def main():
    service.prepare_service()
    if cfg.CONF.cron:
        manager.start_daemon()
    else:
        manager.start()
    return 0
