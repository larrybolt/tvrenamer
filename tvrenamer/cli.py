"""Command-line interface to the TvRenamer APIs"""

import logging
import sys

import six

import tvrenamer
from tvrenamer import api

LOG = logging.getLogger(tvrenamer.PROJECT_NAME)


def main():
    results = api.API.execute()
    for epname, result in six.iteritems(results):
        status = 'SUCCESS' if result.get('result') else 'FAILURE'
        LOG.info('[%s]: %s --> %s', status, epname,
                 result.get('formatted_filename'))
        if result.get('messages'):
            LOG.info('\tREASON: %s', result.get('messages'))

    return 0


if __name__ == '__main__':
    sys.exit(main())
