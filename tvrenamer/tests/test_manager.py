from __future__ import print_function

import os
import tempfile

import mock

from tvrenamer.core import episode
from tvrenamer import manager
from tvrenamer.tests import base


class ManagerTests(base.BaseTest):

    def setUp(self):
        super(ManagerTests, self).setUp()

        dbfile = os.path.join(tempfile.mkdtemp(), 'cache.db')
        self.CONF.set_override('connection',
                               'sqlite:///' + dbfile,
                               'cache')

    def _make_data(self):
        results = []
        ep1 = mock.Mock()
        ep1.status = {
            '/tmp/Lucy.2014.576p.BDRip.AC3.x264.DuaL-EAGLE.mkv': {
                'formatted_filename': None,
                'state': 'failed',
                'messages': 'Could not find season 20'}
            }
        results.append(ep1)

        ep2 = mock.Mock()
        ep2.status = {
            '/tmp/revenge.412.hdtv-lol.mp4': {
                'formatted_filename': 'S04E12-Madness.mp4',
                'state': 'finished',
                'messages': None}
            }
        results.append(ep2)
        return results

    @mock.patch.object(manager.LOG, 'isEnabledFor')
    def test_handle_results(self, mock_log):

        self.CONF.set_override('cache_enabled', False)
        mock_log.return_value = False
        manager._handle_results([])

        mock_log.return_value = True
        with mock.patch.object(manager.table, 'write_output') as mock_output:
            manager._handle_results([])
            self.assertFalse(mock_output.called)

        with mock.patch('six.moves.builtins.print') as mock_print:
            manager._handle_results(self._make_data())
            self.assertTrue(mock_print.called)

    @mock.patch('tvrenamer.cache.save')
    def test_cache_result(self, mock_cache):

        ep = episode.Episode('/tmp/test_media.mp4')
        ep.episode_numbers = [1, 2, 3]
        ep.episode_names = ['the ep1', 'other ep2', 'final ep3']
        ep.messages = ['Invalid file found',
                       'Season not found',
                       'Unknown episode'
                       ]

        self.CONF.set_override('cache_enabled', False)
        manager._cache_result(ep)
        self.assertFalse(mock_cache.called)

        self.CONF.set_override('cache_enabled', True)
        manager._cache_result(ep)
        self.assertTrue(mock_cache.called)

        mock_cache.side_effect = RuntimeError
        manager._cache_result(ep)
        self.assertTrue(mock_cache.called)
