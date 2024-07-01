# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Nicolas Delaby <nicolas@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions
from warnings import warn


class TextConvertableMixin:
  """
  This class provides a generic implementation of ITextConvertable.
  """

  # Declarative security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'asText')
  def asText(self, **kw):
    """
    Converts the current document to plain text
    """
    kw['format'] = 'txt'
    _, data = self.convert(**kw)
    return data

  security.declareProtected(Permissions.AccessContentsInformation,
                            'asRawText')
  def asRawText(self, **kw):
    """
    Converts the current document to plain text without substitution
    """
    kw['format'] = 'txt'
    kw['substitute'] = False
    return self.asText(**kw)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'asTextContent')
  def asTextContent(self, **kw):
    """
    Converts the current document to plain text
    Backward (legacy) compatibility
    """
    warn("asTextContent() function is deprecated. Use asText() instead.", \
          DeprecationWarning, stacklevel=2)
    return self.asText(**kw)

InitializeClass(TextConvertableMixin)
