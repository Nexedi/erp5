##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Products.CMFCategory.Category import BaseCategory as CMFBaseCategory
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import interfaces, Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Base import _aq_reset

from zLOG import LOG


class BaseCategory(CMFBaseCategory, XMLObject):
    """
      Base Categories allow to implement virtual categories
      through acquisition
    """
    meta_type='ERP5 Base Category'
    portal_type='Base Category' # maybe useful some day
    isPortalContent = 1
    isRADContent = 1
    isCategory = 1
    allowed_types = ('ERP5 Category', )

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)


    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.CategoryCore
                      , PropertySheet.BaseCategory
                      , PropertySheet.Predicate)

    # Experimental - WebDAV browsing support - ask JPS
    def experimental_listDAVObjects(self):
      from zLOG import LOG
      LOG("BaseCategory listDAVObjects" ,0, "listDAVObjects")
      return []
      result = self.objectValues(spec=('ERP5 Categorya', 'ERP5 Base Category'))
      result.append(self.getParentValue())
      #result.extend(self.portal_catalog())
      return result

    def manage_afterAdd(self, item, container):
      """
         Reset Accessors
      """
      _aq_reset()
      CMFBaseCategory.manage_afterAdd(self, item, container)
