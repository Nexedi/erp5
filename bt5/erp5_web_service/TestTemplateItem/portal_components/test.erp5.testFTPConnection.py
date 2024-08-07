##############################################################################
#
# Copyright (c) 2018- Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import os
import unittest
import six.moves.urllib.parse

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase


class TestSFTPConnection(ERP5TypeTestCase):
  if os.environ.get("testSFTPConnection_SFTP_URL"):
    def afterSetUp(self):
      url = os.environ["testSFTPConnection_SFTP_URL"]
      parsed_url = six.moves.urllib.parse.urlparse(url)
      self.connection = self.portal.portal_web_services.newContent(
          portal_type='FTP Connector',
          reference=self.id(),
          user_id=parsed_url.username,
          password=parsed_url.password,
          url_string=url,
          url_protocol='sftp',
          use_temporary_file_on_write=False)

    def beforeTearDown(self):
      for f in self.connection.listFiles("."):
        self.connection.removeFile(f)
      self.assertEqual([], self.connection.listFiles("."))

    def test_create_read_delete_file(self):
      self.connection.putFile("filename", "file content")
      self.assertEqual(
        "file content",
        self.connection.getFile("filename")
      )
      self.connection.removeFile("filename")

      # after file is removed, an IOError is raised when trying to read it.
      self.assertRaises(
        IOError,
        self.connection.getFile, "filename"
      )

    def test_put_rename(self):
      self.connection.putFile("filename", "file content")
      self.connection.renameFile("filename", "new name")
      self.assertEqual(
        "file content",
        self.connection.getFile("new name")
      )

    def test_list_dir(self):
      self.connection.putFile("first_file", "first file content ( a bit bigger )")
      self.connection.putFile("second_file", "second file content")
      # by default, ordering is not specified
      self.assertCountEqual(
          ["first_file", "second_file"],
          self.connection.listFiles(".")
      )
      # but we can sort by modification date
      self.assertEqual(
          ["first_file", "second_file"],
          self.connection.listFiles(".", sort_on="st_mtime")
      )
      # or by file size
      self.assertEqual(
          ["second_file" , "first_file"],
          self.connection.listFiles(".", sort_on="st_size")
      )

    def test_create_remove_directory(self):
      self.connection.createDirectory("foo")
      self.assertCountEqual(["foo"], self.connection.listFiles("."))
      self.connection.removeDirectory("foo")
      self.assertCountEqual([], self.connection.listFiles("."))

  else:
    def test_no_SFTP_URL_in_environ(self):
      raise unittest.SkipTest(
        """This test needs the environment variable testSFTPConnection_SFTP_URL set to the URL of a SFTP connection.

        The URL must contain login and password, such as sftp://user:pass@[::1]:8022
        The directory from this URL must be empty and writeable.
        """
      )