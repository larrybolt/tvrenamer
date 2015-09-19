import os
import tempfile

import mock

from tvrenamer.processors import cache
from tvrenamer.tests import base


class CacheProcessorTests(base.BaseTest):

    def setUp(self):
        super(CacheProcessorTests, self).setUp()

        dbfile = os.path.join(tempfile.mkdtemp(), 'cache.db')
        self.CONF.set_override('connection',
                               'sqlite:///' + dbfile,
                               'cache')

        self.processor = cache.CacheResults()

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

    @mock.patch('tvrenamer.cache.save')
    def test_cache_result(self, mock_cache):

        self.CONF.set_override('cache_enabled', False)
        self.assertFalse(self.processor.enabled)
        self.processor.process([])
        self.assertFalse(mock_cache.called)

        self.CONF.set_override('cache_enabled', True)
        self.assertTrue(self.processor.enabled)
        self.processor.process(self._make_data())
        self.assertTrue(mock_cache.called)

        mock_cache.side_effect = RuntimeError
        self.processor.process(self._make_data())
        self.assertTrue(mock_cache.called)
