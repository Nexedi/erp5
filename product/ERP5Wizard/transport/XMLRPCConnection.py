##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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

import xmlrpclib
from urlparse import urlparse

class XMLRPCConnection:
  """
    Holds an XML-RPC connection to a remote XML-RPC server.
  """

  def __init__(self, url, user_name = None, password = None):
    self.url = url
    self._user_name = user_name
    self._password = password

  def connect(self):
    """Get a handle to a remote connection."""
    url = self.url
    if self._user_name is not None and self._password is not None:
      # add HTTP Basic Authentication
      schema = urlparse(url)
      url = '%s://%s:%s@%s%s' %(schema[0], self._user_name, self._password,
                                schema[1], schema[2])
    return xmlrpclib.ServerProxy(url, allow_none=1)


