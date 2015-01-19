"""Command-line interface to the TvRenamer APIs"""

import logging
import os
import tempfile

import lockfile
import six

import tvrenamer
from tvrenamer import manager
from tvrenamer import service

LOG = logging.getLogger(tvrenamer.PROJECT_NAME)


def _show_results(results):

    # if logging is not enabled then no need to
    # go any further.
    if not LOG.isEnabledFor(logging.INFO):
        return

    for epname, result in six.iteritems(results):
        status = 'SUCCESS' if result.get('result') else 'FAILURE'
        LOG.info('[%s]: %s --> %s', status, epname,
                 result.get('formatted_filename'))
        LOG.info('\tPROGRESS: %s', result.get('progress'))
        if result.get('messages'):
            LOG.info('\tREASON: %s', result.get('messages'))


@lockfile.locked(os.path.join(tempfile.gettempdir(), tvrenamer.PROJECT_NAME),
                 timeout=10)
def main():
    service.prepare_service()
    _show_results(manager.start())
    return 0
