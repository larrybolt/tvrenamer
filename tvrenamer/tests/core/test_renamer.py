import errno
import os

import mock
from testtools import matchers

from tvrenamer.core import renamer
from tvrenamer.tests import base


class RenamerTest(base.BaseTest):

#   def test_rename_file(self):
#       tempfile = self.create_tempfiles([('test_file', 'test data')])[0]
#       new_file = os.path.join(os.path.dirname(tempfile), 'other_file.conf')
#       renamer._rename_file(tempfile, new_file)
#       self.assertThat(new_file, matchers.FileExists())
#       self.assertThat(tempfile, matchers.Not(matchers.FileExists()))
#
#       with mock.patch.object(os, 'utime',
#                              side_effect=OSError(errno.EPERM,
#                                                  'perm err',
#                                                  'other_file2.conf')):
#           tempfile = self.create_tempfiles([('test_file2', 'test data')])[0]
#           new_file = os.path.join(os.path.dirname(tempfile),
#                                   'other_file2.conf')
#           renamer._rename_file(tempfile, new_file)
#           self.assertThat(new_file, matchers.FileExists())
#           self.assertThat(tempfile, matchers.Not(matchers.FileExists()))
#
#       with mock.patch.object(os, 'utime',
#                              side_effect=OSError(errno.ENOENT,
#                                                  'missing file',
#                                                  'other_file3.conf')):
#           tempfile = self.create_tempfiles([('test_file3', 'test data')])[0]
#           new_file = os.path.join(os.path.dirname(tempfile),
#                                   'other_file3.conf')
#           self.assertRaises(OSError, renamer._rename_file,
#                             tempfile, new_file)

#   def test_check_overwrite_existing(self):
#
#       with mock.patch.object(os.path, 'isfile', return_value=False):
#           self.assertTrue(
#               renamer._check_overwrite_existing('/tmp/test_file.txt',
#                                                 'Test_file.txt'))
#
#       with mock.patch.object(os.path, 'isfile', return_value=True):
#           self.assertRaises(OSError,
#               renamer._check_overwrite_existing,
#               '/tmp/test_file.txt', 'Test_file.txt')
#
#       with mock.patch.object(os.path, 'isfile', return_value=True):
#           self.CONF.set_override('overwrite_file_enabled', True)
#           self.assertTrue(
#               renamer._check_overwrite_existing('/tmp/test_file.txt',
#                                                 'Test_file.txt'))

    def test_execute(self):

        with mock.patch.object(os.path, 'isfile', return_value=True):
            self.assertRaises(OSError, 
                renamer.execute,
                '/tmp/test_file.txt', 'Test_file.txt')

        tempfile = self.create_tempfiles([('test_file', 'test data')])[0]
        new_file = os.path.join(os.path.dirname(tempfile), 'other_file.conf')
        renamer.execute(tempfile, new_file)
        self.assertThat(new_file, matchers.FileExists())
        self.assertThat(tempfile, matchers.Not(matchers.FileExists()))

        tempfiles = self.create_tempfiles([('test_file', 'test data'),
                                           ('other_file', 'test data')])
        self.CONF.set_override('overwrite_file_enabled', True)
        renamer.execute(tempfiles[0], tempfiles[1])
        self.assertThat(tempfiles[1], matchers.FileExists())
        self.assertThat(tempfiles[0], matchers.Not(matchers.FileExists()))

        tempfile = self.create_tempfiles([('my_file', 'test data')])[0]
        new_file = os.path.join(os.path.dirname(tempfile), 'alt_file.conf')
        self.CONF.set_override('dryrun', True)
        renamer.execute(tempfile, new_file)
        self.assertThat(tempfile, matchers.FileExists())
        self.assertThat(new_file, matchers.Not(matchers.FileExists()))

#   def test_execute_rename(self):
#       self.CONF.set_override('overwrite_file_enabled', True)
#       tempfile = self.create_tempfiles([('my_file', 'test data')])[0]
#       new_file = os.path.join(os.path.dirname(tempfile),
#                               'myother_file.conf')
#       renamer.execute_rename(tempfile, new_file)
#       self.assertThat(new_file, matchers.FileExists())
#       self.assertThat(tempfile, matchers.Not(matchers.FileExists()))
#
#       self.CONF.set_override('dryrun', True)
#       tempfile = self.create_tempfiles([('my_file1', 'test data')])[0]
#       new_file = os.path.join(os.path.dirname(tempfile),
#                               'myother_file1.conf')
#       renamer.execute_rename(tempfile, new_file)
#       self.assertThat(tempfile, matchers.FileExists())
#       self.assertThat(new_file, matchers.Not(matchers.FileExists()))

#   def test_execute_relocate(self):
#       tempfile = self.create_tempfiles([('mv_file', 'test data')])[0]
#       new_file = os.path.join(os.path.dirname(tempfile),
#                               'mvother_file.conf')
#       renamer.execute_relocate(tempfile, new_file)
#       self.assertThat(new_file, matchers.FileExists())
#       self.assertThat(tempfile, matchers.Not(matchers.FileExists()))
#
#       # test making directory portion
#       tempfile = self.create_tempfiles([('mv_file1', 'test data')])[0]
#       new_file = os.path.join(os.path.dirname(tempfile),
#                               'test',
#                               'mvother_file1.conf')
#       renamer.execute_relocate(tempfile, new_file)
#       self.assertThat(new_file, matchers.FileExists())
#       self.assertThat(tempfile, matchers.Not(matchers.FileExists()))
#
#       with mock.patch.object(os, 'makedirs',
#                              side_effect=OSError(errno.EPERM,
#                                                  'perm err',
#                                                  'test1')):
#
#           tempfile = self.create_tempfiles([('mv_file3', 'test data')])[0]
#           new_file = os.path.join(os.path.dirname(tempfile),
#                                  'test2',
#                                  'mvother_file3.conf')
#           self.assertRaises(OSError, renamer.execute_relocate,
#                            tempfile, new_file)

#   def test_execute_relocate_dryrun(self):
#       self.CONF.set_override('dryrun', True)
#
#       tempfile = self.create_tempfiles([('mv_file', 'test data')])[0]
#       new_file = os.path.join(os.path.dirname(tempfile),
#                               'mvother_file.conf')
#       renamer.execute_relocate(tempfile, new_file)
#       self.assertThat(tempfile, matchers.FileExists())
#       self.assertThat(new_file, matchers.Not(matchers.FileExists()))
#
#       # test making directory portion
#       tempfile = self.create_tempfiles([('mv_file1', 'test data')])[0]
#       new_file = os.path.join(os.path.dirname(tempfile),
#                               'test',
#                               'mvother_file1.conf')
#       os.makedirs(os.path.dirname(new_file))
#       renamer.execute_relocate(tempfile, new_file)
#       self.assertThat(tempfile, matchers.FileExists())
#       self.assertThat(new_file, matchers.Not(matchers.FileExists()))
#
#       with mock.patch.object(os, 'makedirs',
#                              side_effect=OSError(errno.EPERM,
#                                                  'perm err',
#                                                  'test1')):
#
#           tempfile = self.create_tempfiles([('mv_file3', 'test data')])[0]
#           new_file = os.path.join(os.path.dirname(tempfile),
#                                  'test2',
#                                  'mvother_file3.conf')
#           self.assertRaises(OSError, renamer.execute_relocate,
#                            tempfile, new_file)
