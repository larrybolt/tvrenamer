import mock

from tvrenamer import manager
from tvrenamer.processors import base as proc_base
from tvrenamer.tests import base


class ManagerTests(base.BaseTest):

    def setUp(self):
        super(ManagerTests, self).setUp()

    def test_run(self):
        self.CONF.set_override('cron', False)
        with mock.patch.object(manager, '_start') as mock_start:
            manager.run()
            self.assertTrue(mock_start.called)

        self.CONF.set_override('cron', True)
        with mock.patch.object(manager._service, 'launch') as mock_start:
            manager.run()
            self.assertTrue(mock_start.called)

    @mock.patch('tvrenamer.core.watcher.retrieve_files')
    @mock.patch.object(manager.episode, 'Episode')
    def test_start(self, mock_ep, mock_watcher):
        proc_mgr = mock.Mock(spec=proc_base.EnabledExtensionManager)
        mock_watcher.return_value = ['/tmp/videos/video1.mp4']
        manager._start(proc_mgr)
        self.assertTrue(proc_mgr.map_method.called)
