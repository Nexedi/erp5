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

from Products.ERP5Type.Core.ModuleComponent import ModuleComponent

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions

import zope.interface
from Products.ERP5Type.interfaces.component import IComponent

class TestComponent(ModuleComponent):
  """
  ZODB Component for Live Tests only (previously defined in the bt5 and
  installed in INSTANCE_HOME/tests) as other kind of Tests should be
  deprecated at some point
  """
  meta_type = 'ERP5 Test Component'
  portal_type = 'Test Component'

  zope.interface.implements(IComponent)

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  @staticmethod
  def _getFilesystemPath():
    import os.path
    from App.config import getConfiguration
    return os.path.join(getConfiguration().instancehome, 'tests')

  @staticmethod
  def _getDynamicModuleNamespace():
    return 'erp5.component.test'

  @staticmethod
  def getIdPrefix():
    return 'test'
