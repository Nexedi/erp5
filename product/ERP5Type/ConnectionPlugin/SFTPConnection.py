# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Nexedi SARL and Contributors. All Rights Reserved.
#                    Aurélien Calonne <aurel@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import os, socket
from urlparse import urlparse
from socket import error
from xmlrpclib import Binary
from cStringIO import StringIO
from paramiko import Transport, RSAKey, SFTPClient

class SFTPError(Exception):
  """
  Default exception for the connection
  """
  pass

class SFTPConnection:
  """
  Handle a SFTP (SSH over FTP) Connection
  """

  def __init__(self, url, user_name, password=None, private_key=None):
    self.url = url
    self.user_name = user_name
    if password and private_key:
      raise SFTPError("Password and private_key cannot be defined simultaneously")
    self.password = password
    self.private_key = private_key

  def connect(self):
    """ Get a handle to a remote connection """
    # Check URL
    schema = urlparse(self.url)
    if schema.scheme == 'sftp':
      self.transport = Transport((schema.hostname, int(schema.port)))
    else:
      raise SFTPError('Not a valid sftp url %s, type is %s' %(self.url, schema.scheme))
    # Add authentication to transport
    try:
      if self.password:
        self.transport.connect(username=self.user_name, password=self.password)
      elif self.private_key:
        self.transport.connect(username=self.user_name,
                               pkey=RSAKey.from_private_key(StringIO(self.private_key)))
      else:
        raise SFTPError("No password or private_key defined")
      # Connect
      self.conn = SFTPClient.from_transport(self.transport)
    except (socket.gaierror,error), msg:
      raise SFTPError(str(msg) + ' while establishing connection to %s' % (self.url,))
    # Go to specified directory
    try:
      schema.path.rstrip('/')
      if len(schema.path):
        self.conn.chdir(schema.path)
    except IOError, msg:
      raise SFTPError(str(msg) + ' while changing to dir -%r-' % (schema.path,))
    return self

  def writeFile(self, path, filename, data):
    """
    Write data in provided filepath
    """
    filepath = os.path.join(path, filename)
    serialized_data = Binary(str(data))
    try:
      self.conn.putfo(StringIO(str(serialized_data)), filepath, 0, None, True)
    except error, msg:
      raise SFTPError(str(msg) + ' while writing file %s on %s' % (filepath, path, self.url))

  def _getFile(self, filepath, binary=True):
    """Retrieve the file"""
    try:
      if binary:
        tmp_file = self.conn.file(filepath, 'rb')
      else:
        tmp_file = self.conn.file(filepath, 'r')
      tmp_file.seek(0)
      return Binary(tmp_file.read())
    except error, msg:
      raise SFTPError(str(msg) + ' while retrieving file %s from %s' % (filepath, self.url))

  def readBinaryFile(self, filepath):
    """Retrieve the file in binary mode"""
    return StringIO(str(self._getFile(filepath, binary=True)))

  def readAsciiFile(self, filepath):
    """Retrieve the file in ASCII mode"""
    binary = self._getFile(filepath, binary=False)
    if binary:
      return binary.data
    return None

  def getDirectoryContent(self, path):
    """retrieve all entries in a givan path as a list"""
    try:
      return self.conn.listdir(path)
    except (EOFError, error), msg:
      raise SFTPError(str(msg) + ' while trying to list %s on %s' % (path, self.url))

  def getDirectoryFileList(self, path):
    """Retrieve all entries in a given path with absolute paths as a list"""
    return ["%s/%s"%(path, x) for x in self.getDirectoryContent(path)]

  def removeFile(self, filepath):
    """Delete the file"""
    try:
      self.conn.unlink(filepath)
    except error, msg:
      raise SFTPError(str(msg) + 'while trying to delete %s on %s' % (filename, self.url))

  def renameFile(self, old_path, new_path):
    """Rename a file"""
    try:
      self.conn.rename(old_path, new_path)
    except error, msg:
      raise SFTPError('%s while trying to rename "%s" to "%s" on %s.' % \
                     (str(msg), old_path, new_path, self.url))

  def logout(self):
    """Logout of the SFTP Server"""
    self.conn.close()
    self.transport.close()
