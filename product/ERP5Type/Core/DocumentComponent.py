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
from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage

import zope.interface
import re
from Products.ERP5Type.interfaces.component import IComponent

class DocumentComponent(ModuleComponent):
  """
  ZODB Component for Documents in bt5 only for now (which used to be installed
  in INSTANCE_HOME/Document) but this will also be used later on for Documents
  in Products
  """
  meta_type = 'ERP5 Document Component'
  portal_type = 'Document Component'

  zope.interface.implements(IComponent)

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  @staticmethod
  def _getFilesystemPath():
    import os.path
    from App.config import getConfiguration
    return os.path.join(getConfiguration().instancehome, 'Document')

  @staticmethod
  def _getDynamicModuleNamespace():
    return 'erp5.component.document'

  @staticmethod
  def getIdPrefix():
    return 'document'

  _message_reference_class_not_defined = "Class ${reference} must be defined"
  def checkConsistency(self, *args, **kw):
    """
    Per convention, a Document Component must have at least a class whose name
    is the same as the Reference so that it can be assigned to Portal Types.

    XXX: Very basic check for now.
    """
    error_list = super(DocumentComponent, self).checkConsistency(*args ,**kw)
    reference = self.getReference()
    text_content = self.getTextContent()
    if (reference and text_content and # Already checked in the parent class
        re.search('[^\s]*class\s+%s\s*[(:]' % reference, text_content) is None):
      error_list.append(ConsistencyMessage(
        self,
        self.getRelativeUrl(),
        message=self._message_reference_class_not_defined,
        mapping={'reference': reference}))

    return error_list
