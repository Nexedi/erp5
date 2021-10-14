# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2021 Nexedi SARL and Contributors. All Rights Reserved.
#          Julien Muchembled <jm@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ExternalMethod.ExternalMethod import \
  ExternalMethod as ZopeExternalMethod
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.mixin.expression import ExpressionMixin


class ExternalMethod(XMLObject, ZopeExternalMethod, ExpressionMixin()):
    """ External Method for ERP5
    """

    meta_type = 'ERP5 External Method'
    portal_type = 'External Method'
    add_permission = Permissions.AddPortalContent

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    #View content list, Force /view, Standart option in external methods
    manage_options = ( XMLObject.manage_options[0]
                     , {'icon':'', 'label':'View','action':'view'}
                     ) + ZopeExternalMethod.manage_options

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.ExternalMethod
                      )

    manage_edit = None

    def getModule(self):
      return getattr(self, '_module', None)

    def _setModule(self, module):
      self._module = module

    def getFunction(self):
      return getattr(self, '_function', None)

    def _setFunction(self, function):
      self._function = function

    __call__ = ZopeExternalMethod.__call__
