##############################################################################
#
# Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.
#                    Nicolas Dumazet <nicolas.dumazet@nexedi.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
"""
This module should include most code related to the generation of
Accessor Holders, that is, generation of methods for ERP5

* Ideally, PropertyHolder class should be defined here
* Utils, Property Sheet Tool can be probably be cleaned up as well by
moving specialized code here.
"""
import sys

from Products.ERP5Type import Permissions
from Products.ERP5Type.Base import PropertyHolder, Base
from Products.ERP5Type.Utils import createRelatedAccessors, createExpressionContext
from Products.ERP5Type.Utils import setDefaultClassProperties, setDefaultProperties
from Products.ERP5Type.Globals import InitializeClass

from zLOG import LOG, ERROR, INFO

class AccessorHolderType(type):
  _skip_permission_tuple = (Permissions.AccessContentsInformation,
                            Permissions.ModifyPortalContent)
  def registerAccessor(cls,
                       accessor,
                       permission):
    accessor_name = accessor.__name__
    setattr(cls, accessor_name, accessor)
    # private accessors do not need declarative security
    if accessor_name[0] != '_' and \
        permission not in AccessorHolderType._skip_permission_tuple:
      cls.security.declareProtected(permission, accessor_name)

  @classmethod
  def fromPropertyHolder(meta_type,
                         property_holder,
                         portal=None,
                         accessor_holder_module_name=None,
                         initialize=True):
    """
    Create a new accessor holder class from the given Property Holder
    within the given accessor holder module
    """
    property_sheet_id = property_holder.__name__
    context = portal.portal_property_sheets
    if initialize:
      setDefaultClassProperties(property_holder)

      try:
        setDefaultProperties(property_holder,
                             object=context,
                             portal=portal)
      except:
        LOG("Tool.PropertySheetTool", ERROR,
            "Could not generate accessor holder class for %s (module=%s)" % \
            (property_sheet_id, accessor_holder_module_name),
            error=sys.exc_info())

        raise

    # Create the new accessor holder class and set its module properly
    accessor_holder_class = meta_type(property_sheet_id, (object,), dict(
      __module__ = accessor_holder_module_name,
      constraints = property_holder.constraints,
      # The following attributes have been defined only because they
      # are being used in ERP5Type.Utils when getting all the
      # property_sheets of the property_holder (then, they are added
      # to the local properties, categories and constraints lists)
      _properties = property_holder._properties,
      # Necessary for getBaseCategoryList
      _categories = property_holder._categories,
      _constraints = property_holder._constraints,
      security = property_holder.security
      ))

    # Set all the accessors (defined by a tuple) from the Property
    # Holder to the new accessor holder class (code coming from
    # createAccessor in Base.PropertyHolder)
    for id, fake_accessor in property_holder._getPropertyHolderItemList():
      if callable(fake_accessor):
        # not so fake ;)
        setattr(accessor_holder_class, id, fake_accessor)
        continue
      if not isinstance(fake_accessor, tuple):
        continue

      if fake_accessor is PropertyHolder.WORKFLOW_METHOD_MARKER:
        # Case 1 : a workflow method only
        accessor = Base._doNothing
      else:
        # Case 2 : a workflow method over an accessor
        (accessor_class, accessor_args, key) = fake_accessor
        accessor = accessor_class(id, key, *accessor_args)

      # Add the accessor to the accessor holder
      setattr(accessor_holder_class, id, accessor)

    property_holder.security.apply(accessor_holder_class)
    InitializeClass(accessor_holder_class)
    return accessor_holder_class

def _generateBaseAccessorHolder(portal,
                                accessor_holder_module):
  """
  Create once an accessor holder that contains all accessors common to
  all portal types: erp5.accessor_holder.BaseAccessorHolder

  * Related category accessors are generated here.
  In the future we would like as well:
  * the has.*Property accessors
  * the is.*Type group accessors

  It's important to remember that this accessor holder will be the last
  class added to a portal type class, and that it will always be added,
  to all living ERP5 objects.
  """
  base_accessor_holder_id = 'BaseAccessorHolder'

  accessor_holder = getattr(accessor_holder_module,
                            base_accessor_holder_id,
                            None)
  if accessor_holder is not None:
    return accessor_holder

  # When setting up the site, there will be no portal_categories
  portal_categories = getattr(portal, 'portal_categories', None)
  if portal_categories is None:
    return None

  base_category_list = portal_categories.objectIds()

  property_holder = PropertyHolder(base_accessor_holder_id)

  econtext = createExpressionContext(portal_categories, portal)
  createRelatedAccessors(portal_categories,
                         property_holder,
                         econtext,
                         base_category_list)

  accessor_holder = AccessorHolderType.fromPropertyHolder(
                      property_holder,
                      portal,
                      'erp5.accessor_holder',
                      initialize=False)
  setattr(accessor_holder_module, base_accessor_holder_id, accessor_holder)
  return accessor_holder

def _generatePreferenceToolAccessorHolder(portal, accessor_holder_list,
    accessor_holder_module):
  """
  Generate a specific Accessor Holder that will be put on the Preference Tool.
  (This used to happen in ERP5Form.PreferenceTool._aq_dynamic)

  We iterate over all properties that do exist on the system, select the
  preferences out of those, and generate the getPreferred.* accessors.
  """
  property_holder = PropertyHolder('PreferenceTool')

  from Products.ERP5Type.Accessor.TypeDefinition import list_types
  from Products.ERP5Type.Utils import convertToUpperCase
  from Products.ERP5Form.PreferenceTool import PreferenceMethod

  for accessor_holder in accessor_holder_list:
    for prop in accessor_holder._properties:
      if prop.get('preference'):
        # XXX read_permission and write_permissions defined at
        # property sheet are not respected by this.
        # only properties marked as preference are used

        # properties have already been 'converted' and _list is appended
        # to list_types properties
        attribute = prop['id']
        if attribute.endswith('_list'):
          attribute = prop['base_id']
        attr_list = [ 'get%s' % convertToUpperCase(attribute)]
        if prop['type'] == 'boolean':
          attr_list.append('is%s' % convertToUpperCase(attribute))
        if prop['type'] in list_types :
          attr_list.append('get%sList' % convertToUpperCase(attribute))
        read_permission = prop.get('read_permission')
        for attribute_name in attr_list:
          method = PreferenceMethod(attribute_name, prop.get('default'))
          setattr(property_holder, attribute_name, method)
          if read_permission:
            property_holder.declareProtected(read_permission, attribute_name)

  accessor_holder = AccessorHolderType.fromPropertyHolder(
                      property_holder,
                      portal,
                      'erp5.accessor_holder',
                      initialize=False)
  setattr(accessor_holder_module, 'PreferenceTool', accessor_holder)
  return accessor_holder
