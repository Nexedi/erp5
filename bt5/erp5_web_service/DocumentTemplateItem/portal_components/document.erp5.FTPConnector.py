# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Nexedi SA and Contributors. All Rights Reserved.
#                    Aurélien Calonne <aurel@nexedi.com>
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

import posixpath

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject


class FTPConnector(XMLObject):
  # CMF Type Definition
  meta_type = 'FTP Connector'
  portal_type = 'FTP Connector'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                      )

  def getConnection(self):
    if self.getUrlProtocol() == "sftp":
      return self.getPortalObject().portal_web_services.connect(
        user_name=self.getUserId(),
        password=self.getPassword(),
        url=self.getUrlString(),
        transport=self.getUrlProtocol(),
        transport_kw={
          'private_key':self.getDescription(),
          'bind_address': self.getBindAddress(),
        },
      )
    else:
      # XXX Must manage in the future ftp and ftps protocol
      raise NotImplementedError("Protocol %s is not yet implemented" %(self.getUrlProtocol(),))

  def renameFile(self, old_path, new_path):
    """ Move a file """
    conn = self.getConnection()
    try:
      conn.renameFile(old_path, new_path)
    finally:
      conn.logout()

  def removeFile(self, filepath):
    """Delete the file"""
    conn = self.getConnection()
    try:
      conn.removeFile(filepath)
    finally:
      conn.logout()

  def listFiles(self, path=".", sort_on=None):
    """ List file of a directory """
    conn = self.getConnection()
    try:
      return conn.getDirectoryContent(path, sort_on=sort_on)
    finally:
      conn.logout()

  def getFile(self, filepath, binary=True):
    """ Try to get a file on the remote server """
    conn = self.getConnection()
    try:
      if binary:
        return conn.readBinaryFile(filepath)
      else:
        return conn.readAsciiFile(filepath)
    finally:
      conn.logout()

  def putFile(self, filename, data, remotepath='.', confirm=True):
    """ Send file to the remote server """
    conn = self.getConnection()
    # This API is misleading, and in reality filename often contains a path.
    # So let's use python posixpath API to try to reconstruct the path in a
    # robust way (ie: what if remotepath is './a' and filename is 'b/c.txt' ?),
    # and recompute the correct remotepath and filename
    remotepath, filename = posixpath.split(
      posixpath.join(remotepath, filename)
    )
    try:
      if self.isUseTemporaryFileOnWrite():
        temp_filename = '_%s.tmp' % filename
        # Simulation transaction system
        conn.writeFile(remotepath, temp_filename, data, confirm=confirm)
        self.activate(activity='SQLQueue').renameFile(
          posixpath.join(remotepath, temp_filename),
          posixpath.join(remotepath, filename)
        )
      else:
        conn.writeFile(remotepath, filename, data, confirm=confirm)
    finally:
      conn.logout()

  def createDirectory(self, path, mode=0777):
    """Create a directory `path`, with file mode `mode`.

    The directory is created immediatly, even if transaction is aborted.
    """
    conn = self.getConnection()
    try:
      conn.createDirectory(path, mode)
    finally:
      conn.logout()

  def removeDirectory(self, path):
    """Create a directory `path`, with file mode `mode`.

    The directory is removed immediatly, even if transaction is aborted.
    """
    conn = self.getConnection()
    try:
      conn.removeDirectory(path)
    finally:
      conn.logout()