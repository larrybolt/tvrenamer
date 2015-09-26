import os
import tempfile

from tvrenamer import cache
from tvrenamer.core import episode
from tvrenamer.tests import base


class SAApiTestCase(base.BaseTest):

    def setUp(self):
        super(SAApiTestCase, self).setUp()

        dbfile = os.path.join(tempfile.mkdtemp(), 'cache.json')
        self.CONF.set_override('dbfile', dbfile, 'cache')
        self.dbconn = cache.dbapi(self.CONF)

    def tearDown(self):
        cache._DBAPI = None
        super(SAApiTestCase, self).tearDown()

    def test_clear(self):
        dbapi = cache.dbapi(self.CONF)
        dbapi.clear()
        self.assertTrue(True)

    def test_save(self):

        media = self.create_tempfiles(
            [('revenge.s04e12.hdtv.x264-2hd', 'dummy data')],
            '.mp4')[0]
        ep = episode.Episode(media)

        _saved_ep_id = self.dbconn.save(ep)
        self.assertIsInstance(_saved_ep_id, int)

        ep.formatted_filename = 'S04E12.mp4'
        _saved_ep_id = self.dbconn.save(ep)
        self.assertIsInstance(_saved_ep_id, int)
