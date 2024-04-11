##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Aurelien Calonne <aurel@nexedi.com>
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

from erp5.component.tool.WebServiceTool import WebServiceConnectionError
from Products.ERP5.ERP5Site import getSite

class MethodWrapper(object):

  def __init__(self, method, conn):
    self._method = method
    self._conn = conn

  def __call__(self, *args, **kw):
    portal = getSite()
    method_name = "DocumentConnector_%s" %(self._method)
    method = getattr(portal, method_name, None)
    kw["reference"] = self._conn.reference
    if method:
      response = method(*args, **kw)
      return method.absolute_url(), response
##       try:
##       except ValueError, msg:
##         raise WebServiceConnectionError(msg)
##       except Exception, msg:
##         raise WebServiceConnectionError(msg)
    else:
      raise WebServiceConnectionError("Method %s does not exist" %(method_name))

class DocumentConnection:
  """
    Holds a connection to the document module.
  """
  __allow_access_to_unprotected_subobjects__ = 1

  def __init__(self, url, *args, **kw):
    """
    """
    self.reference=url

  def connect(self):
    """Get a handle to a remote connection."""
    return self

  def __getattr__(self, name):
    if not name.startswith("_"):
      return MethodWrapper(name, self)
