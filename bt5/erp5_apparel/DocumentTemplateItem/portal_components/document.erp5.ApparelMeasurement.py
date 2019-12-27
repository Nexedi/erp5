##############################################################################
#
# Copyright (c) 2002 Coramy SAS and Contributors. All Rights Reserved.
#                    Thierry_Faucher <Thierry_Faucher@coramy.com>
# Copyright (c) 2004, 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Courteaud_Romain <romain@nexedi.com>
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
from Products.CMFCore.WorkflowCore import WorkflowAction

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.XMLMatrix import XMLMatrix
from erp5.component.document.Image import Image

class ApparelMeasurement(XMLObject, XMLMatrix, Image):
    """
     XXX  A matrix which provides default mesure_code and mesure_name
    """
    meta_type = 'ERP5 Apparel Measurement'
    portal_type = 'Apparel Measurement'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.VariationRange
                      , PropertySheet.Arrow
                      )


    def __init__(self, id, **kw):
      Image.__init__(self, id, **kw)
      XMLObject.__init__(self, id, **kw)

    # Inheritance
    _edit = Image._edit
    security.declareProtected(Permissions.ModifyPortalContent, 'edit' )
    edit = WorkflowAction( _edit )

    security.declareProtected(Permissions.View,  'index_html')
    index_html = Image.index_html

    security.declareProtected(Permissions.AccessContentsInformation,
                              'content_type')
    content_type = Image.content_type

    def manage_afterClone(self, item):
      XMLObject.manage_afterClone(self, item)
      Image.manage_afterClone(self, item)

    def manage_afterAdd(self, item, container):
      XMLObject.manage_afterAdd(self, item, container)
      Image.manage_afterAdd(self, item, container)

    def manage_beforeDelete(self, item, container):
      Image.manage_beforeDelete(self, item, container)

    security.declareProtected(Permissions.ModifyPortalContent, '_setMeasureList')
    def _setMeasureList(self,value):
      self._categorySetMeasureList(value)
      # XXX Use interaction workflow instead
      self.updateCellRange(base_id='measure')
