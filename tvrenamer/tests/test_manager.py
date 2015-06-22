import uuid

import mock

from tvrenamer import manager
from tvrenamer.tests import base


class SampleTask(object):

    def __call__(self):
        return {str(uuid.uuid4()): {'status': 'SUCCESS'}}


class ManagerTests(base.BaseTest):

    def setUp(self):
        super(ManagerTests, self).setUp()
        self.mgr = manager.Manager()
        self.addCleanup(self.mgr.shutdown)

    def test_manager(self):
        self.assertTrue(self.mgr.empty())
        _tasks = []
        _tasks.append(SampleTask())
        _tasks.append(SampleTask())
        _tasks.append(SampleTask())

        self.mgr.add_tasks(_tasks)
        self.mgr.add_tasks(SampleTask())

        self.assertFalse(self.mgr.empty())
        self.assertEqual(len(self.mgr.tasks), 4)

        results = self.mgr.run()
        self.assertTrue(self.mgr.empty())
        self.assertEqual(len(self.mgr.tasks), 0)
        self.assertEqual(len(results), 4)


class ManagerProcessTests(base.BaseTest):

    def _make_data(self):
        results = []
        ep1 = mock.Mock()
        ep1.status = {
            '/tmp/Lucy.2014.576p.BDRip.AC3.x264.DuaL-EAGLE.mkv': {
                'formatted_filename': None,
                'result': False,
                'messages': 'Could not find season 20'}
            }
        results.append(ep1)

        ep2 = mock.Mock()
        ep2.status = {
            '/tmp/revenge.412.hdtv-lol.mp4': {
                'formatted_filename': 'S04E12-Madness.mp4',
                'result': True,
                'messages': None}
            }
        results.append(ep2)
        return results

    def test_handle_results(self):

        self.CONF.set_override('enabled', False, 'database')

        with mock.patch.object(manager.LOG, 'isEnabledFor',
                               return_value=False):
            manager._handle_results([])

        with mock.patch.object(manager.LOG, 'isEnabledFor',
                               return_value=True):
            with mock.patch.object(manager.LOG, 'info') as mock_log_info:
                manager._handle_results([])
                self.assertEqual(mock_log_info.call_count, 0)

            with mock.patch.object(manager.LOG, 'info') as mock_log_info:
                manager._handle_results(self._make_data())
                self.assertEqual(mock_log_info.call_count, 5)

    def test_get_work(self):

        locations = ['/tmp/download', '/downloads']
        orig_files = ['/tmp/download/revenge.s04e12.hdtv.x264-2hd.mp4',
                      '/tmp/download/Lucy.2014.720p.BluRay.x254-x0r.mkv']
        with mock.patch.object(manager.tools, 'retrieve_files',
                               return_value=orig_files):
            self.assertEqual(len(manager._get_work(locations, {})), 2)

        with mock.patch.object(manager.tools, 'retrieve_files',
                               return_value=orig_files):
            self.assertEqual(
                len(manager._get_work(
                    locations,
                    {'/tmp/download/revenge.s04e12.hdtv.x264-2hd.mp4': None,
                     '/tmp/download/Lucy.2014.720p.BluRay.x254-x0r.mkv': None}
                )), 0)

    def test_start(self):
        self.skipTest('function runs as infinite loop')
