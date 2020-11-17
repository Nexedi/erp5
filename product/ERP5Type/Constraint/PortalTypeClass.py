from __future__ import absolute_import
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

from .Constraint import Constraint
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

  _message_id_list = [ 'message_type_not_registered',
                       'message_inconsistent_meta_type',
                       'message_inconsistent_class' ]

  message_type_not_registered = "Type Information ${type_name} not "\
                                "registered with the TypeTool"
  message_inconsistent_meta_type = "Meta type is inconsistant with portal"\
      " type definition. Portal type meta type is ${portal_type_meta_type}"\
      " class meta type is ${class_meta_type}"
  message_inconsistent_class = "__class__ is inconsistant with portal type"\
      " definition. Portal Type class is ${portal_type_class},"\
      " document class is ${document_class}"

  def _checkConsistency(self, obj, fixit=0):
    """Check the object's consistency.
    """
    error_list = []
    types_tool = getToolByName(obj, 'portal_types')
    type_info = types_tool._getOb(obj.getPortalType(), None)
    if type_info is None :
      error_list.append(self._generateError(obj,
          self._getMessage('message_type_not_registered'),
          mapping=dict(type_name=obj.getPortalType())))
    elif type_info.content_meta_type != obj.meta_type :
      error_list.append(self._generateError(obj,
          self._getMessage('message_inconsistent_meta_type'),
          mapping=dict(portal_type_meta_type=type_info.content_meta_type,
                       class_meta_type=obj.meta_type)))
    else :
      portal_type_class = self._getClassForPortalType(obj, type_info)
      obj_class = str(obj.__class__)
      if portal_type_class != obj_class :
        error_list.append(self._generateError(obj,
          self._getMessage('message_inconsistent_class'),
          mapping=dict(portal_type_class=portal_type_class,
                       document_class=obj_class)))
      # TODO fixit argument can be implemented here.
    return error_list


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

