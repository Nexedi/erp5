# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5Type.mixin.component import ComponentMixin
from Products.ERP5Type.mixin.text_content_history import TextContentHistoryMixin
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions

import zope.interface
from Products.ERP5Type.interfaces.component import IComponent

class ExtensionComponent(ComponentMixin, TextContentHistoryMixin):
  """
  ZODB Component for Extensions previously defined in the bt5 and installed in
  INSTANCE_HOME/Extensions
  """
  meta_type = 'ERP5 Extension Component'
  portal_type = 'Extension Component'

  zope.interface.implements(IComponent)

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  @staticmethod
  def _getFilesystemPath():
    import os.path
    from App.config import getConfiguration
    return os.path.join(getConfiguration().instancehome, 'Extensions')

  @staticmethod
  def _getDynamicModuleNamespace():
    return 'erp5.component.extension'

  @staticmethod
  def getIdPrefix():
    return 'extension'
