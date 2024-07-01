# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Lucas Carvalho <lucas@nexedi.com>
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


_marker=object()

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable


class VirtualFolderMixin:
  """
    Virtual Folder Mixin is a class which allows to customize the _setObject
    and _getOb methods for a given portal type.
  """

  security = ClassSecurityInfo()

  security.declarePrivate('PUT_factory')
  def PUT_factory(self, name, typ, body):
    """ Factory for PUT requests to objects which do not yet exist.

    Used by NullResource.PUT.

    Returns -- Bare and empty object of the appropriate type (or None, if
    we don't know what to do)
    """
    method = getattr(self, 'Base_putFactory', None)
    if method is not None:
      return method(name, typ, body)

    return Folder.PUT_factory(self, name, typ, body)  # pylint:disable=not-callable

  security.declarePrivate('_setObject')
  def _setObject(self, id, ob, **kw): # pylint: disable=redefined-builtin
    """
      XXX
    """
    tv = getTransactionalVariable()
    key = 'VirtualFolderMixin', self.getPhysicalPath(), id
    tv[key] = ob.__of__(self).getRelativeUrl()

    method = getattr(self, 'Base_setObject', None)
    if method is not None:
      return method(id, ob, **kw)

    return Folder._setObject(self, id, ob, **kw)

  security.declarePrivate('_getOb')
  def _getOb(self, id, default=_marker, **kw): # pylint: disable=redefined-builtin
    """
      XXX
    """
    tv = getTransactionalVariable()
    key = 'VirtualFolderMixin', self.getPhysicalPath(), id
    document_url = tv.get(key, None)
    if document_url is not None:
      return self.getPortalObject().unrestrictedTraverse(document_url)

    try:
      return Folder._getOb(self, id, default=default, **kw)
    except KeyError:
      if default is _marker:
        raise
      return default

InitializeClass(VirtualFolderMixin)
