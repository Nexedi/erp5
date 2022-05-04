# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Acquisition import aq_base
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import PersistentMapping
from erp5.component.interface.IConfigurable import IConfigurable

@zope.interface.implementer(IConfigurable,)
class ConfigurableMixin:
  """
  This class provides a generic implementation of IConfigurable.

  Iconfigurable provides methods to record configuration properties.
  It is used by solver decisions and solvers, but could be used for
  other purpose.
  """

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getConfigurationProperty')
  def getConfigurationProperty(self, key, default=None):
    """
    """
    return self._getConfigurationPropertyDict().get(key, default)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getConfigurationPropertyIdList')
  def getConfigurationPropertyIdList(self):
    """
    """
    return self._getConfigurationPropertyDict().keys()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getConfigurationPropertyDict')
  def getConfigurationPropertyDict(self):
    """
    """
    return dict(self._getConfigurationPropertyDict())

  security.declareProtected(Permissions.ModifyPortalContent,
                            'updateConfiguration')
  def updateConfiguration(self, **kw):
    """
    """
    self._getConfigurationPropertyDict().update(kw)

  def _getConfigurationPropertyDict(self):
    if getattr(aq_base(self), '_configuration_property_dict', None) is None:
      self._configuration_property_dict = PersistentMapping()
    return self._configuration_property_dict

InitializeClass(ConfigurableMixin)
