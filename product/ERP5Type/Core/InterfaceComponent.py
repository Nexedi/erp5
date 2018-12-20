# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2018 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5Type.Core.DocumentComponent import DocumentComponent
from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage

class InterfaceComponent(DocumentComponent):
  """
  ZODB Component for interfaces
  """
  meta_type = 'ERP5 Interface Component'
  portal_type = 'Interface Component'

  @staticmethod
  def _getDynamicModuleNamespace():
    return 'erp5.component.interface'

  @staticmethod
  def getIdPrefix():
    return 'interface'

  _message_reference_wrong_naming = "Interface Reference must start with 'I'"
  def checkConsistency(self, *args, **kw):
    """
    Per convention, an Interface class must start with 'I'
    """
    error_list = super(InterfaceComponent, self).checkConsistency(*args, **kw)
    reference = self.getReference()
    if (reference and # Already checked in the parent class
        not reference.startswith('I')):
      error_list.append(ConsistencyMessage(
        self,
        self.getRelativeUrl(),
        message=self._message_reference_wrong_naming,
        mapping={}))

    return error_list
