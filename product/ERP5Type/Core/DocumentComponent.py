# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
#                    Jean-Paul Smets <jp@nexedi.com>
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

import imp
import os

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.Base import Base
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
                           
class DocumentComponent(Base):
    # CMF Type Definition
    meta_type = 'ERP5 Document Component'
    portal_type = 'Document Component'

    isPortalContent = 1
    isRADContent = 1
    isDelivery = ConstantGetter('isDelivery', value=True)

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ('Base',
                       'XMLObject',
                       'CategoryCore',
                       'DublinCore',
                       'Version',
                       'Reference',
                       'TextDocument')

    def load(self):
      # XXX-arnau: There should be a load_source() taking a string rather than
      # creating a temporary file
      from App.config import getConfiguration
      instance_home = getConfiguration().instancehome
      path = '%s/Component' % instance_home
      if not os.path.isdir(path):
        os.mkdir(path)

      component_path = '%s/%s.py' % (path, self.getId())
      with open(component_path, 'w') as component_file:
        component_file.write(self.getTextContent())

      try:
        return imp.load_source(self.getReference(), component_path)
      finally:
        os.remove(component_path)
