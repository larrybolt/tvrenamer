import os
import tempfile

from tvrenamer import cache
from tvrenamer.cache import models as db_model
from tvrenamer.core import episode
from tvrenamer.tests import base


class CacheTests(base.BaseTest):

    def setUp(self):
        super(CacheTests, self).setUp()

        dbfile = os.path.join(tempfile.mkdtemp(), 'cache.db')
        self.CONF.set_override('connection',
                               'sqlite:///' + dbfile,
                               'cache')
        self.dbconn = cache.dbapi(self.CONF)

    def tearDown(self):
        cache._DBAPI = None
        super(CacheTests, self).tearDown()

    def test_save(self):
        ep = episode.Episode('/tmp/test_media.mp4')
        ep.episode_numbers = [1, 2, 3]
        ep.episode_names = ['the ep1', 'other ep2', 'final ep3']
        ep.messages = ['Invalid file found',
                       'Season not found',
                       'Unknown episode'
                       ]
        mf = cache.save(ep)
        self.assertIsNotNone(mf)
        self.assertIsInstance(mf, db_model.MediaFile)

#       self.assertEqual(mf.original, '/tmp/test_media.mp4')
#       self.assertEqual(mf.name, 'test_media.mp4')
#       self.assertEqual(mf.location,  '/tmp')
#       self.assertEqual(mf.episode_numbers, '1,2,3')
#       self.assertEqual(mf.episode_names, 'the ep1,other ep2,final ep3')
#       self.assertEqual(
#           mf.messages,
#           'Invalid file found,Season not found,Unknown episode')
#       self.assertIsNone(mf.clean_name)
