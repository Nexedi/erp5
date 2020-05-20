##############################################################################
#
# Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.
#                    Arnaud Fontaine <arnaud.fontaine@nexedi.com>
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

from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions

class PreferenceType(ERP5TypeInformation):
  """
  Preference, System Preference and Preference Tool portal types are
  Preference Type, necessary to define custom behavior for these
  portal types, such as Property Sheets
  """
  portal_type = 'Preference Type'
  meta_type = 'ERP5 Preference Type'

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def getTypePropertySheetList(self):
    """
    Preference and System Preference get all the Property Sheets
    ending by 'Preference' applied automatically
    """
    property_sheet_tool = getattr(self.getPortalObject(),
                                  'portal_property_sheets',
                                  None)

    if property_sheet_tool is None:
      return

    existing_property_sheet_name_set = set(property_sheet_tool.objectIds())
    property_sheet_name_list = []

    for property_sheet_name in existing_property_sheet_name_set:
      if property_sheet_name.endswith('Preference'):
        property_sheet_name_list.append(property_sheet_name)

    return property_sheet_name_list
