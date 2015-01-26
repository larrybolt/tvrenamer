import mock

from tvrenamer import cli
from tvrenamer.tests import base


class CliTest(base.BaseTest):

    def test_cli(self):
        with mock.patch.object(cli.service, 'prepare_service'):
            with mock.patch.object(cli.manager, 'start', return_value={}):
                rv = cli.main()
                self.assertEqual(rv, 0)

    def test_cli_results(self):

        with mock.patch.object(cli.LOG, 'isEnabledFor', return_value=False):
            cli._show_results({})

        with mock.patch.object(cli.LOG, 'isEnabledFor', return_value=True):
            with mock.patch.object(cli.LOG, 'info') as mock_log_info:
                cli._show_results({})
                self.assertEqual(mock_log_info.call_count, 0)

            with mock.patch.object(cli.LOG, 'info') as mock_log_info:
                data = {
                    '/tmp/Lucy.2014.576p.BDRip.AC3.x264.DuaL-EAGLE.mkv': {
                        'formatted_filename': None,
                        'result': False,
                        'messages': 'Could not find season 20',
                        },
                    '/tmp/revenge.412.hdtv-lol.mp4': {
                        'formatted_filename': 'S04E12-Madness.mp4',
                        'result': True,
                        'messages': None,
                        },
                    }
                cli._show_results(data)
                self.assertEqual(mock_log_info.call_count, 5)
