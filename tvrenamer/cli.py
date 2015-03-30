"""Command-line interface to the TvRenamer APIs"""
import os
import tempfile

import lockfile

import tvrenamer
from tvrenamer import manager
from tvrenamer import service


@lockfile.locked(os.path.join(tempfile.gettempdir(), tvrenamer.PROJECT_NAME),
                 timeout=10)
def main():
    service.prepare_service()
    manager.start()
    return 0
