from tvrenamer.core import patterns
from tvrenamer.tests import base


class PatternsTest(base.BaseTest):

    def test_get_expressions(self):
        exprs = patterns.get_expressions()
        self.assertEqual(len(exprs), 21)

        acopy = patterns.get_expressions()
        self.assertEqual(len(acopy), 21)

        self.assertEqual(exprs, acopy)
