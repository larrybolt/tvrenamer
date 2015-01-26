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
