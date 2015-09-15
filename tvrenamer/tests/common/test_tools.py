from tvrenamer.common import tools
from tvrenamer.tests import base


class ToolsTest(base.BaseTest):

    def test_make_opt_list(self):
        group_name = 'test'
        options = ['x', 'y', 'z', 'v']
        results = tools.make_opt_list(options, group_name)
        self.assertEqual(results, [('test', ['x', 'y', 'z', 'v'])])
