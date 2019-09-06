# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2019 Nexedi SA and Contributors. All Rights Reserved.
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

class ModuleComponent(ComponentMixin, TextContentHistoryMixin):
  """
  ZODB Component for Modules, eg non-Documents from Products, and the base
  class for all other Components
  """
  meta_type = 'ERP5 Module Component'
  portal_type = 'Module Component'

  zope.interface.implements(IComponent)

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  @staticmethod
  def _getFilesystemPath():
    # TODO-arnau: useful?
    raise NotImplementedError

  @staticmethod
  def _getDynamicModuleNamespace():
    return 'erp5.component.module'

  @staticmethod
  def getIdPrefix():
    return 'module'
