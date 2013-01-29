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

from Products.ERP5Form.Document.PreferenceType import PreferenceType
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5Type.dynamic.accessor_holder import AccessorHolderType

from Products.ERP5Type.Accessor.TypeDefinition import list_types
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Form.PreferenceTool import PreferenceMethod

def _generatePreferenceToolAccessorHolder(portal_type_name,
                                          accessor_holder_list):
  """
  Generate a specific Accessor Holder that will be put on the Preference Tool.
  (This used to happen in ERP5Form.PreferenceTool._aq_dynamic)

  We iterate over all properties that do exist on the system, select
  the preferences out of those, and generate the getPreferred.*
  accessors in erp5.accessor_holder.portal_type.PORTAL_TYPE.PORTAL_TYPE.
  """
  import erp5.accessor_holder.portal_type

  accessor_holder_module = getattr(erp5.accessor_holder.portal_type,
                                   portal_type_name)

  try:
    return accessor_holder_module.PreferenceTool
  except AttributeError:
    # The accessor holder does not already exist
    pass

  preference_tool_accessor_holder = AccessorHolderType('PreferenceTool')

  preferred_accessor = ("isPreferred", "hasPreferred", "getPreferred",
                        "getDefaultPreferred", "hasDefaultPreferred")

  for accessor_holder in accessor_holder_list:
    for accessor in accessor_holder.__dict__:
      if accessor.startswith(preferred_accessor) and not accessor.endswith("__roles__"):
        method = PreferenceMethod(accessor)
        preference_tool_accessor_holder.registerAccessor(method,
                                                         'Access contents information')

  accessor_holder_module.registerAccessorHolder(preference_tool_accessor_holder)

  return preference_tool_accessor_holder

class PreferenceToolType(PreferenceType):
  """
  Preference Tool also define its specific accessor holders
  """
  portal_type = 'Preference Tool Type'
  meta_type = 'ERP5 Preference Tool Type'

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def getAccessorHolderList(self):
    accessor_holder_list = super(PreferenceToolType,
                                 self).getAccessorHolderList()

    return [_generatePreferenceToolAccessorHolder(self.getPortalType(),
                                                  accessor_holder_list)]
