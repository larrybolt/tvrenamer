from tvrenamer import options
from tvrenamer.tests import base


class OptionsTest(base.BaseTest):

    def test_list_opts(self):
        self.assertIsNotNone(options.list_opts())
