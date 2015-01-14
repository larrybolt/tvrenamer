import tvdb_api

from tvrenamer.services import tvdb
from tvrenamer.tests import base


class TvdbServiceTest(base.BaseTest):

    def setUp(self):
        super(TvdbServiceTest, self).setUp()
        self.api = tvdb.TvdbService()

    def test_get_series_by_name(self):
        series, err = self.api.get_series_by_name('The Big Bang Theory')
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(series['seriesname'], 'The Big Bang Theory')

        series, err = self.api.get_series_by_name('Fake - Unknown Series')
        self.assertIsNone(series)
        self.assertIsNotNone(err)
        self.assertIsInstance(err, tvdb_api.tvdb_shownotfound)

    def test_get_series_by_id(self):
        series, err = self.api.get_series_by_id(80379)
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(series['seriesname'], 'The Big Bang Theory')

        series, err = self.api.get_series_by_id(0)
        self.assertIsNone(series)
        self.assertIsNotNone(err)
        self.assertIsInstance(err, tvdb_api.tvdb_error)

    def test_get_series_name(self):
        series, err = self.api.get_series_by_name('The Big Bang Theory')
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(self.api.get_series_name(series),
                         'The Big Bang Theory')

        self.assertIsNone(self.api.get_series_name(None))

        self.CONF.set_override('output_series_replacements',
                               {'reign (2013)': 'reign'})
        series, err = self.api.get_series_by_name('reign (2013)')
        self.assertIsNotNone(series)
        self.assertIsNone(err)
        self.assertEqual(self.api.get_series_name(series), 'reign')

    def test_get_episode_name(self):
        series, err = self.api.get_series_by_name('The Big Bang Theory')
        episodes, eperr = self.api.get_episode_name(series, [1], 1)
        self.assertIsNotNone(episodes)
        self.assertIsNone(eperr)
        self.assertEqual(episodes, ['Pilot'])

        episodes, eperr = self.api.get_episode_name(None, [1], 1)
        self.assertIsNone(episodes)
        self.assertIsNone(eperr)

        episodes, eperr = self.api.get_episode_name(series, [1])
        self.assertIsNotNone(episodes)
        self.assertIsNone(eperr)
        self.assertEqual(episodes, ['Pilot'])

    def test_get_episode_name_season_nf(self):
        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [1], 2)
        self.assertIsNone(episodes)
        self.assertIsNotNone(eperr)
        self.assertIsInstance(eperr, tvdb_api.tvdb_seasonnotfound)

        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [1], '1')
        self.assertIsNone(episodes)
        self.assertIsNotNone(eperr)
        self.assertIsInstance(eperr, tvdb_api.tvdb_seasonnotfound)

    def test_get_episode_name_attr_nf(self):
        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [1], 'xx')
        self.assertIsNone(episodes)
        self.assertIsNone(eperr)

    def test_get_episode_name_episode_nf(self):
        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [25], 1)
        self.assertIsNone(episodes)
        self.assertIsNotNone(eperr)
        self.assertIsInstance(eperr, tvdb_api.tvdb_episodenotfound)

        series, err = self.api.get_series_by_name('Firefly')
        episodes, eperr = self.api.get_episode_name(series, [15], 1)
        self.assertIsNotNone(episodes)
        self.assertIsNone(eperr)
        self.assertEqual(episodes, ['Serenity'])
