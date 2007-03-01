##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jerome Perrin <jerome@nexedi.com>
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

from Constraint import Constraint
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Cache import CachingMethod

class PortalTypeClass(Constraint):
  """
    This constraint checks that a document is based on the same class as
    it's portal type.
    This is usefull to check that all objects of a given portal type are
    consistant and that dynamic methods for the portal type can be
    attached on the class.

    Configuration example:
    { 'id'            : 'portal_type_class',
      'description'   : 'The __class__ must be the same as the portal'\
                        ' type definition',
      'type'          : 'PortalTypeClass',
      'condition'     : 'python: object.getPortalType() == 'Foo',
    },
  """

  def checkConsistency(self, obj, fixit=0):
    """
      This is the check method, we return a list of string,
      each string corresponds to an error.
    """
    if not self._checkConstraintCondition(obj):
      return []
    errors = []
    types_tool = getToolByName(obj, 'portal_types')
    type_info = types_tool._getOb(obj.getPortalType(), None)
    if type_info is None :
      errors.append(self._generateError(obj,
          "Type information for '%s' not registred with the TypeTool"))
    elif type_info.content_meta_type != obj.meta_type :
      errors.append(self._generateError(obj,
          "Meta type is inconsistant with portal type definition."\
          " Portal type meta type is '%s' class meta type is '%s' " % (
           type_info.content_meta_type, obj.meta_type )))
    else :
      portal_type_class = self._getClassForPortalType(obj, type_info)
      obj_class = str(obj.__class__)
      if portal_type_class != obj_class :
        errors.append(self._generateError(obj,
          "__class__ is inconsistant with portal type definition."\
          " Portal_type class is %s, document class is %s" % (
            portal_type_class, obj_class)))
      # TODO fixit argument can be implemented here.
    return errors


  def _getClassForPortalType(self, obj, type_info):
    """Computes the class for a portal type.
    XXX Is there any better way than creating an object ???
    """
    def _getClassForPortalTypeCache(portal_type_name):
      folder = obj.getParentValue()
      new_obj = type_info.constructInstance(
                    folder, None)
      class_name = str(new_obj.__class__)
      folder.manage_delObjects([new_obj.getId()])
      return class_name
    _getClassForPortalTypeCache = CachingMethod(
        _getClassForPortalTypeCache,
        "PortalTypeClass._getClassForPortalTypeCache",
        cache_factory = 'erp5_content_medium'
        )
    return _getClassForPortalTypeCache(obj.getPortalType())

