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
import operator
from six.moves.urllib.parse import urlparse
from socket import gaierror, error, socket, getaddrinfo, AF_UNSPEC, SOCK_STREAM
from six.moves.xmlrpc_client import Binary
from six.moves import cStringIO as StringIO
from paramiko import Transport, RSAKey, SFTPClient
from paramiko.util import retry_on_signal

class SFTPError(Exception):
  """
  Default exception for the connection
  """
  pass

class SFTPConnection:
  """
  Handle a SFTP (SSH over FTP) Connection
  """

  def __init__(self, url, user_name, password=None, private_key=None,
      bind_address=None):
    self.url = url
    self.user_name = user_name
    if password and private_key:
      raise SFTPError("Password and private_key cannot be defined simultaneously")
    self.password = password
    self.private_key = private_key
    self.bind_address = bind_address

  def connect(self):
    """ Get a handle to a remote connection """
    # Check URL
    schema = urlparse(self.url)
    if schema.scheme == 'sftp':
      hostname = schema.hostname
      port = int(schema.port)
      # Socket creation code inspired from paramiko.Transport.__init__
      # with added bind support.
      for family, socktype, _, _, _ in getaddrinfo(
            hostname, port, AF_UNSPEC, SOCK_STREAM,
          ):
        if socktype == SOCK_STREAM:
          sock = socket(family, SOCK_STREAM)
          if self.bind_address:
            # XXX: Expects bind address to be of same family as hostname.
            # May not be easy if name resolution is involved.
            # Try to reconciliate them ?
            sock.bind((self.bind_address, 0))
          retry_on_signal(lambda: sock.connect((hostname, port))) # pylint: disable=cell-var-from-loop
          break
      else:
        raise SFTPError('No suitable socket family found')
      self.transport = Transport(sock)
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
    except (gaierror, error) as msg:
      raise SFTPError(str(msg) + ' while establishing connection to %s' % (self.url,))
    # Go to specified directory
    try:
      schema.path.rstrip('/')
      if len(schema.path):
        self.conn.chdir(schema.path)
    except IOError as msg:
      raise SFTPError(str(msg) + ' while changing to dir -%r-' % (schema.path,))
    return self

  def writeFile(self, path, filename, data, confirm=True):
    """
    Write data in provided filepath
    """
    filepath = os.path.join(path, filename)
    serialized_data = Binary(str(data))
    try:
      self.conn.putfo(StringIO(str(serialized_data)), filepath, confirm=confirm)
    except error as msg:
      raise SFTPError(str(msg) + ' while writing file %s on %s' % (filepath, path))

  def _getFile(self, filepath):
    """Retrieve the file"""
    try:
      # always open with binary mode, otherwise paramiko will raise
      # UnicodeDecodeError for non-utf8 data. also SFTP has no ASCII
      # mode like FTP that normalises CRLF/CR/LF.
      tmp_file = self.conn.file(filepath, 'rb')
      tmp_file.seek(0)
      return tmp_file.read()
    except error as msg:
      raise SFTPError(str(msg) + ' while retrieving file %s from %s' % (filepath, self.url))

  def readBinaryFile(self, filepath):
    """Retrieve the file in binary mode"""
    return self._getFile(filepath)

  def readAsciiFile(self, filepath):
    """Retrieve the file in ASCII mode"""
    # normalise CRLF/CR/LF like FTP's ASCII mode transfer.
    return os.linesep.join(self._getFile(filepath).splitlines())

  def getDirectoryContent(self, path, sort_on=None):
    """retrieve all entries in a givan path as a list.

    `sort_on` parameter allows to retrieve the directory content in a sorted
    order, it understands all parameters from
    paramiko.sftp_attr.SFTPAttributes, the most useful being `st_mtime` to sort
    by modification date.
    """
    try:
      if sort_on:
        return [x.filename for x in sorted(self.conn.listdir_attr(path), key=operator.attrgetter(sort_on))]
      return self.conn.listdir(path)
    except (EOFError, error) as msg:
      raise SFTPError(str(msg) + ' while trying to list %s on %s' % (path, self.url))

  def getDirectoryFileList(self, path):
    """Retrieve all entries in a given path with absolute paths as a list"""
    return ["%s/%s"%(path, x) for x in self.getDirectoryContent(path)]

  def removeFile(self, filepath):
    """Delete the file"""
    try:
      self.conn.unlink(filepath)
    except error as msg:
      raise SFTPError(str(msg) + 'while trying to delete %s on %s' % (filepath, self.url))

  def renameFile(self, old_path, new_path):
    """Rename a file"""
    try:
      self.conn.rename(old_path, new_path)
    except error as msg:
      raise SFTPError('%s while trying to rename "%s" to "%s" on %s.' % \
                     (str(msg), old_path, new_path, self.url))

  def createDirectory(self, path, mode=0o777):
    """Create a directory `path` with mode `mode`.
    """
    return self.conn.mkdir(path, mode)

  def removeDirectory(self, path):
    """Remove directory `path`.
    """
    return self.conn.rmdir(path)

  def logout(self):
    """Logout of the SFTP Server"""
    self.conn.close()
    self.transport.close()
