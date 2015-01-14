import mock

from tvrenamer import cli
from tvrenamer.tests import base


class CliTest(base.BaseTest):

    def test_cli(self):

        with mock.patch.object(cli.api.API, 'execute', return_value={}):
            rv = cli.main()
            self.assertEqual(rv, 0)

    def test_cli_results(self):

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
        with mock.patch.object(cli.api.API, 'execute', return_value=data):
            rv = cli.main()
            self.assertEqual(rv, 0)
