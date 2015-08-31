import os

import fixtures
import testtools
from tvdbapi_client import exceptions

from tvrenamer.services import tvdb
from tvrenamer.tests import base


def disabled():
    return not os.environ.get('TEST_API_KEY') or not os.environ.get(
        'TEST_API_USER') or not os.environ.get('TEST_API_PASSWORD')


class TvdbServiceTest(base.BaseTest):

    def setUp(self):
        super(TvdbServiceTest, self).setUp()
        self.useFixture(fixtures.EnvironmentVariable(
            'TVDB_API_KEY', os.environ.get('TEST_API_KEY')))
        self.useFixture(fixtures.EnvironmentVariable(
            'TVDB_USERNAME', os.environ.get('TEST_API_USER')))
        self.useFixture(fixtures.EnvironmentVariable(
            'TVDB_PASSWORD', os.environ.get('TEST_API_PASSWORD')))

        self.api = tvdb.TvdbService()

    @testtools.skipIf(disabled(), 'live api testing disabled')
    def test_get_series_by_name(self):
        series, err = self.api.get_series_by_name('The Big Bang Theory')
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(series['seriesName'], 'The Big Bang Theory')

        series, err = self.api.get_series_by_name('Fake - Unknown Series')
        self.assertIsNone(series)
        self.assertIsNotNone(err)
        self.assertIsInstance(err, exceptions.TVDBRequestException)

    @testtools.skipIf(disabled(), 'live api testing disabled')
    def test_get_series_by_id(self):
        series, err = self.api.get_series_by_id(80379)
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(series['seriesName'], 'The Big Bang Theory')

        series, err = self.api.get_series_by_id(0)
        self.assertIsNone(series)
        self.assertIsNotNone(err)
        self.assertIsInstance(err, exceptions.TVDBRequestException)

    @testtools.skipIf(disabled(), 'live api testing disabled')
    def test_get_series_name(self):
        series, err = self.api.get_series_by_name('The Big Bang Theory')
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(
            self.api.get_series_name(series,
                                     self.CONF.output_series_replacements),
            'The Big Bang Theory')

        self.CONF.set_override('output_series_replacements',
                               {'reign (2013)': 'reign'})
        series, err = self.api.get_series_by_name('reign (2013)')
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(
            self.api.get_series_name(series,
                                     self.CONF.output_series_replacements),
            'reign')

    @testtools.skipIf(disabled(), 'live api testing disabled')
    def test_get_episode_name(self):
        series, err = self.api.get_series_by_name('The Big Bang Theory')
        episodes, eperr = self.api.get_episode_name(series, [1], 1)
        self.assertIsNotNone(episodes)
        self.assertIsNone(eperr)
        self.assertEqual(episodes, ['Pilot'])

    @testtools.skipIf(disabled(), 'live api testing disabled')
    def test_get_episode_name_season_nf(self):
        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [1], 2)
        self.assertIsNone(episodes)
        self.assertIsNotNone(eperr)
        self.assertIsInstance(eperr, exceptions.TVDBRequestException)

    @testtools.skipIf(disabled(), 'live api testing disabled')
    def test_get_episode_name_attr_nf(self):
        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [1], 5)
        self.assertIsNone(episodes)
        self.assertIsNotNone(eperr)
        self.assertIsInstance(eperr, exceptions.TVDBRequestException)

    @testtools.skipIf(disabled(), 'live api testing disabled')
    def test_get_episode_name_episode_nf(self):
        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [25], 1)
        self.assertIsNone(episodes)
        self.assertIsNone(eperr)

        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [15], 0)
        self.assertIsNotNone(episodes)
        self.assertIsNone(eperr)
        self.assertEqual(episodes, ['Serenity'])
