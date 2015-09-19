import mock

from tvrenamer import cli
from tvrenamer.tests import base


class CliTest(base.BaseTest):

    def test_cli(self):
        with mock.patch.object(cli.service, 'prepare_service'):
            with mock.patch.object(cli.manager, 'run', return_value={}):
                rv = cli.main()
                self.assertEqual(rv, 0)
