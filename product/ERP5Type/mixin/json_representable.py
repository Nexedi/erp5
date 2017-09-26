# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 Nexedi SA and Contributors. All Rights Reserved.
#                    Ayush Tiwari <ayush.tiwari@nexedi.com>
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

import json
import xmltodict
import zope.interface
from OFS import XMLExportImport
from StringIO import StringIO
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.interfaces.json_representable import IJSONRepresentable
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import InitializeClass

class JSONRepresentableMixin:
  """
  An implementation for IJSONRepresentable
  """

  # Declarative Security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  zope.interface.implements(IJSONRepresentable)

  security.declareProtected(Permissions.AccessContentsInformation, 'asJSON')
  def asJSON(self):
    """
    Generate a JSON representable content for ERP5 object

    Currently we use `XMLExportImport` to first convert the object to its XML
    respresentation and then use xmltodict to convert it to dict and JSON
    format finally
    """
    # Use OFS exportXML to first export to xml
    f = StringIO()
    XMLExportImport.exportXML(self._p_jar, self._p_oid, f)

    # Get the value of exported XML
    xml_value = f.getvalue()

    # Convert the XML to json representation
    return json.dumps(xmltodict.parse(xml_value))

InitializeClass(JSONRepresentableMixin)
