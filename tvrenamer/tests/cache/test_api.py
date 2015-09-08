import os
import tempfile

from tvrenamer import cache
from tvrenamer.cache import models as db_model
from tvrenamer.tests import base


class SAApiTestCase(base.BaseTest):

    def setUp(self):
        super(SAApiTestCase, self).setUp()

        dbfile = os.path.join(tempfile.mkdtemp(), 'cache.db')
        self.CONF.set_override('connection',
                               'sqlite:///' + dbfile,
                               'cache')
        self.dbconn = cache.dbapi(self.CONF)

    def tearDown(self):
        cache._DBAPI = None
        super(SAApiTestCase, self).tearDown()

    def test_upgrade(self):
        try:
            self.dbconn.upgrade()
            self.assertTrue(True)
        except Exception:
            self.assertTrue(False)

    def test_clear(self):
        dbapi = cache.dbapi(self.CONF)
        dbapi.clear()
        self.assertTrue(True)

    def test_shrink_db(self):
        self.dbconn.shrink_db()
        self.assertTrue(True)

    def test_save(self):

        self.dbconn._engine_facade.session.expire_on_commit = False

        mf = db_model.MediaFile(original='/tmp/download/sample.avi')
        self.assertIsInstance(mf, db_model.MediaFile)

        _saved_mf = self.dbconn.save(mf)
        self.assertIsInstance(_saved_mf, db_model.MediaFile)
