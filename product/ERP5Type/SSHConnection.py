##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Lucas Carvalho Teixeira <lucas@nexedi.com>
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

from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Errors import SSHConnectionError
from zLOG import LOG, WARNING
try:
  import paramiko
  from paramiko.ssh_exception import SSHException
except ImportError:
  LOG(WARNING, 0, 'The SSHConnection can not be used because Paramiko ' 
                  'is not installed!')
import os

class SSHConnection(object):
  """
    Holds an SHH connection to a remote SSH server.
  """
  security = ClassSecurityInfo()

  def __init__(self, username, host, port, key_path):
    self.username = username
    self.host = host
    self.port = port
    if os.path.exists(key_path):
      self.key_path = key_path
    else:
      raise ValueError, 'key_path does not exist: %s' % key_path

  security.declarePublic(Permissions.ManagePortal, 'connect')
  def connect(self):
    """
      Get a handle to a remote connection.
    """
    self.transport = paramiko.Transport((self.host, int(self.port)))
    rsa_key = paramiko.RSAKey.from_private_key_file(self.key_path)
    try:
      self.transport.connect(username=self.username, pkey=rsa_key)
    except SSHException, e:
      self.transport.close()
      raise SSHConnectionError(str(e))
    else:
      self.sftp = paramiko.SFTPClient.from_transport(self.transport)

  security.declarePublic(Permissions.ManagePortal, 'close')
  def close(self):
    """
      It must close the sftp and transport connection.
    """
    self.sftp.close()
    self.transport.close()

InitializeClass(SSHConnection)
