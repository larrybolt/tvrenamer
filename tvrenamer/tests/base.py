from oslo_config import fixture as fixture_config
from oslotest import base as test_base

import tvrenamer


class BaseTest(test_base.BaseTestCase):

    def setUp(self):
        super(BaseTest, self).setUp()

        self.CONF = self.useFixture(fixture_config.Config()).conf
        self.CONF([], project=tvrenamer.PROJECT_NAME)
