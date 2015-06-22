import re

import titlecase as tc

from tvrenamer.tests import base

tc.ALL_CAPS = re.compile(r'^[A-Z\s%s]+$' % tc.PUNCT)


class TitlecaseTest(base.BaseTest):

    def test_from_all_lower(self):
        self.assertEqual(tc.titlecase('a very simple title'),
                         'A Very Simple Title')
        self.assertEqual(tc.titlecase('o\'shea is not a good band'),
                         'O\'Shea Is Not a Good Band')
        self.assertEqual(tc.titlecase('o\'do not wanton with those eyes'),
                         'O\'Do Not Wanton With Those Eyes')

    def test_from_all_upper(self):
        self.assertEqual(tc.titlecase('A VERY SIMPLE TITLE'),
                         'A Very Simple Title')
        self.assertEqual(tc.titlecase('W.KI.N.YR.'), 'W.KI.N.YR.')

    def test_from_notation(self):
        self.assertEqual(tc.titlecase('funtime.example.com'),
                         'funtime.example.com')

        self.assertEqual(tc.titlecase('Funtime.Example.Com'),
                         'Funtime.Example.Com')

    def test_from_location(self):
        self.assertEqual(tc.titlecase('S09E01 - sample episode'),
                         'S09E01 - Sample Episode')
        self.assertEqual(
            tc.titlecase('sample series/season 9/S09E01 - sample episode'),
            'Sample Series/Season 9/S09E01 - Sample Episode')

    def test_from_mac(self):
        self.assertEqual(tc.titlecase('macyhg'), 'Macyhg')

    def test_from_asis(self):
        self.assertEqual(tc.titlecase('A Very Simple Title'),
                         'A Very Simple Title')
