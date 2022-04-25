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
from six import string_types as basestring
from types import ModuleType

from Products.ERP5Type import Permissions
from Products.ERP5Type.Utils import createExpressionContext
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable

from Products.ERP5Type.Utils import UpperCase
from Products.ERP5Type.Accessor import Related, RelatedValue
from AccessControl import ClassSecurityInfo

from zLOG import LOG, ERROR, INFO, WARNING

class AccessorHolderType(type):
  _skip_permission_tuple = (Permissions.AccessContentsInformation,
                            Permissions.ModifyPortalContent)
  def registerAccessor(cls,
                       accessor,
                       permission=None):
    accessor_name = accessor.__name__
    setattr(cls, accessor_name, accessor)
    if permission is None:
      return
    # private accessors do not need declarative security
    if accessor_name[0] != '_' and \
        permission not in AccessorHolderType._skip_permission_tuple:
      cls.security.declareProtected(permission, accessor_name)

  def __new__(meta_class, class_name, base_tuple=(object,), attribute_dict={}):
    # we dont want to add several times to the same list, so make sure
    # that duplicate attributes just point to the same list object
    constraint_list = []
    attribute_dict.update(_categories=[],
                          _constraints=constraint_list,
                          constraints=constraint_list,
                          security=ClassSecurityInfo(),
                          _properties=[])

    return super(AccessorHolderType, meta_class).__new__(meta_class,
                                                         class_name,
                                                         base_tuple,
                                                         attribute_dict)

  def _finalize(cls):
    cls.security.apply(cls)
    InitializeClass(cls)

class AccessorHolderModuleType(ModuleType):
  def registerAccessorHolder(self, accessor_holder):
    """
    Add an accessor holder to the module
    """
    # Set the module of the given accessor holder properly
    accessor_holder.__module__ = self.__name__

    # Finalize the class as no accessors is added from now on
    accessor_holder._finalize()

    self.__setattr__(accessor_holder.__name__, accessor_holder)

  def clear(self):
    """
    Clear the content of the module
    """
    for klass in self.__dict__.values():
      if isinstance(klass, AccessorHolderType):
        # Delete these attributes (computed on the portal type class
        # from its accessor holder) before deleting the class itself
        # because a reference on the class will still be kept as bases
        # of erp5.portal_type, thus this ensures that
        # erp5.portal_type.Foo will be 'unghost' thanks to
        # PortalTypeMetaClass.__getattr__
        for attribute in ('constraints', '_categories'):
          try:
            delattr(klass, attribute)
          except AttributeError:
            pass

        delattr(self, klass.__name__)

# For backward compatibility only: define provideIFoo() method where Foo has
# been migrated from filesystem to ZODB Components. Needed until bt5 shipping
# these Interfaces have been upgraded as these are called here and there (for
# example on cataloging...).
migrated_interface_list = [
  'IAccountingMovement',
  'IAmountGenerator',
  'IAmountGeneratorLine',
  'IAssetMovement',
  'IBuildableBusinessLinkProcess',
  'IBusinessLink',
  'IBusinessLinkProcess',
  'IBusinessProcess',
  'IBusinessProcessUnionProvider',
  'IConfigurable',
  'IConfiguratorItem',
  'ICoordinate',
  'IDeliverySolver',
  'IDivergenceController',
  'IDivergenceMessage',
  'IEncryptedPassword',
  'IEquivalenceTester',
  'IExpandable',
  'IImmobilisationItem',
  'ILoginAccountProvider',
  'IMovement',
  'IMovementCollection',
  'IMovementCollectionDiff',
  'IMovementCollectionUpdater',
  'IMovementGenerator',
  'IMovementGroup',
  'IMovementList',
  'IProductionMovement',
  'IRoundingTool',
  'IRule',
  'ISimulationMovement',
  'ISimulationMovementProcess',
  'ISmsReceivingGateway',
  'ISmsSendingGateway',
  'ISolver',
  'ITradeModelPath',
  'ITradeModelPathProcess',
  'ITradePhaseProcess',
  'ITradeStateProcess',
  'IWatermarkable',
  ]

def _generateBaseAccessorHolder(portal):
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
  import erp5.accessor_holder

  base_accessor_holder_id = 'BaseAccessorHolder'

  try:
    return getattr(erp5.accessor_holder, base_accessor_holder_id)
  except AttributeError:
    # The accessor holder does not already exist
    pass

  # When setting up the site, there will be no portal_categories
  category_tool = getattr(portal, 'portal_categories', None)
  if category_tool is None:
    return None

  base_category_id_list = category_tool.objectIds()

  accessor_holder = AccessorHolderType(base_accessor_holder_id)

  for base_category_id in base_category_id_list:
    applyCategoryAsRelatedValueAccessor(accessor_holder,
                                        base_category_id,
                                        category_tool)

  # Create providesIFoo() getters of ZODB/FS Interface classes
  def provides(class_id):
    accessor_name = 'provides' + class_id
    setattr(accessor_holder, accessor_name, lambda self: self.provides(class_id))
    accessor_holder.security.declarePublic(accessor_name)
  for class_id in set(portal.portal_types.getInterfaceTypeList() +
                      migrated_interface_list):
    provides(class_id)

  erp5.accessor_holder.registerAccessorHolder(accessor_holder)
  return accessor_holder

related_accessor_definition_dict = {
  # List getter
  RelatedValue.ListGetter: (
    'get%sRelatedValueList',
    '_categoryGet%sRelatedValueList',
  ),

  # Set getter
  RelatedValue.SetGetter: (
    'get%sRelatedValueSet',
    '_categoryGet%sRelatedValueSet',
  ),

  # Default value getter
  RelatedValue.DefaultGetter: (
    'getDefault%sRelatedValue',
    'get%sRelatedValue',
    '_categoryGetDefault%sRelatedValue',
    '_categoryGet%sRelatedValue',
  ),

  # Related Relative Url
  Related.ListGetter: (
    'get%sRelatedList',
    '_categoryGet%sRelatedList',
  ),

  # Related as Set
  Related.SetGetter: (
    'get%sRelatedSet',
    '_categoryGet%sRelatedSet',
  ),

  # Default getter
  Related.DefaultGetter: (
    'getDefault%sRelated',
    'get%sRelated',
    '_categoryGetDefault%sRelated',
    '_categoryGet%sRelated',
  ),

  # Related Ids (ie. reverse relation getters)
  RelatedValue.IdListGetter: (
    'get%sRelatedIdList',
    '_categoryGet%sRelatedIdList',
  ),

  # Related Ids as Set
  RelatedValue.IdSetGetter: (
    'get%sRelatedIdSet',
    '_categoryGet%sRelatedIdSet',
  ),

  # Default Id getter
  RelatedValue.DefaultIdGetter: (
    'getDefault%sRelatedId',
    'get%sRelatedId',
    '_categoryGetDefault%sRelatedId',
    '_categoryGet%sRelatedId',
  ),

  # Related Title list
  RelatedValue.TitleListGetter: (
    'get%sRelatedTitleList',
    '_categoryGet%sRelatedTitleList',
  ),

  # Related Title Set
  RelatedValue.TitleSetGetter: (
    'get%sRelatedTitleSet',
    '_categoryGet%sRelatedTitleSet',
  ),

  # Related default title
  RelatedValue.DefaultTitleGetter: (
    'getDefault%sRelatedTitle',
    'get%sRelatedTitle',
    '_categoryGetDefault%sRelatedTitle',
    '_categoryGet%sRelatedTitle',
  ),

  # Related Property list
  RelatedValue.PropertyListGetter: (
    'get%sRelatedPropertyList',
    '_categoryGet%sRelatedPropertyList',
  ),

  # Related Property Set
  RelatedValue.PropertySetGetter: (
    'get%sRelatedPropertySet',
    '_categoryGet%sRelatedPropertySet',
  ),

  # Related default title
  RelatedValue.DefaultPropertyGetter: (
    'getDefault%sRelatedProperty',
    'get%sRelatedProperty',
    '_categoryGetDefault%sRelatedProperty',
    '_categoryGet%sRelatedProperty',
  ),
}
def applyCategoryAsRelatedValueAccessor(accessor_holder,
                                        category_id,
                                        category_tool):
  """
  Take one category_id, generate and apply all related value accessors
  implied by this category, and apply/set them to the accessor_holder
  """
  cat_object = category_tool.get(category_id, None)
  if cat_object is not None:
    read_permission = Permissions.__dict__.get(
                            cat_object.getReadPermission(),
                            Permissions.AccessContentsInformation)
  else:
    read_permission = Permissions.AccessContentsInformation

  uppercase_category_id = UpperCase(category_id)

  # two special cases
  accessor_name = uppercase_category_id[0].lower() + uppercase_category_id[1:]
  accessor = RelatedValue.ListGetter(accessor_name + 'RelatedValues', category_id)
  accessor_holder.registerAccessor(accessor, read_permission)
  accessor = RelatedValue.IdListGetter(accessor_name + 'RelatedIds', category_id)
  accessor_holder.registerAccessor(accessor, read_permission)

  for accessor_class, accessor_name_list in related_accessor_definition_dict.items():
    for accessor_name in accessor_name_list:
      accessor = accessor_class(accessor_name % uppercase_category_id, category_id)
      accessor_holder.registerAccessor(accessor, read_permission)

def getPropertySheetValueList(site, property_sheet_name_set):
  try:
    property_sheet_tool = site.portal_property_sheets

  except AttributeError:
    if not getattr(site, '_v_bootstrapping', False):
      LOG("ERP5Type.dynamic", WARNING,
              "Property Sheet Tool was not found. Please update erp5_core "
              "Business Template")

    return []

  property_sheet_value_list = []

  for property_sheet_name in property_sheet_name_set:
    try:
      property_sheet = property_sheet_tool._getOb(property_sheet_name)
    except (AttributeError, KeyError):
      # XXX: OFS.Folder explicitly raises AttributeError, BTreeFolder2
      # implicitly raises KeyError...
      LOG("ERP5Type.dynamic", WARNING,
          "Ignoring missing Property Sheet " + property_sheet_name)

      continue
    else:
      property_sheet_value_list.append(property_sheet)

  return property_sheet_value_list

def getAccessorHolderList(site, portal_type_name, property_sheet_value_list):
  import erp5.accessor_holder

  accessor_holder_list = []
  expression_context = None

  for property_sheet in property_sheet_value_list:
    # LOG("ERP5Type.dynamic", INFO,
    #     "Getting accessor holder for " + property_sheet_name)

    property_sheet_name = property_sheet.getId()

    if property_sheet.isTempObject():
      accessor_holder_module = getattr(erp5.accessor_holder.portal_type,
                                       portal_type_name)
    else:
      accessor_holder_module = erp5.accessor_holder.property_sheet

    try:
      accessor_holder_list.append(getattr(accessor_holder_module,
                                          property_sheet_name))
    except AttributeError:
      # lazily create the context, only if needed.
      if expression_context is None:
        expression_context = createExpressionContext(site)

      # Generate the accessor holder as it has not been done yet
      accessor_holder_class = property_sheet.createAccessorHolder(
        expression_context, site)

      accessor_holder_module.registerAccessorHolder(accessor_holder_class)
      accessor_holder_list.append(accessor_holder_class)

      # LOG("ERP5Type.dynamic", INFO,
      #     "Created accessor holder for %s" % property_sheet_name)

  return accessor_holder_list

from Products.ERP5Type.Base import getClassPropertyList

def createAllAccessorHolderList(site,
                                portal_type_name,
                                portal_type,
                                type_class):
  """
  Create the accessor holder list with the given ZODB Property Sheets
  """
  from erp5 import accessor_holder as accessor_holder_module

  property_sheet_name_set = set()
  accessor_holder_list = []

  # Get the accessor holders of the Portal Type
  if portal_type is not None:
    accessor_holder_list.extend(portal_type.getAccessorHolderList())

    portal_type_property_sheet_name_set = {
      accessor_holder.__name__ for accessor_holder in accessor_holder_list}

  else:
    portal_type_property_sheet_name_set = set()

  # XXX: Only kept for backward-compatibility as Preference and System
  # Preference have Preference Type as portal type, which define
  # getTypePropertySheetList properly and, likewise, Preference Tool
  # has Preference Tool Type as its portal type
  if portal_type_name in ("Preference Tool",
                          "Preference",
                          "System Preference"):
    if portal_type is None or \
       not portal_type.getPortalType().startswith(portal_type_name):
      # The Property Sheet Tool may be None if the code is updated but
      # the BT has not been upgraded yet with portal_property_sheets
      try:
        zodb_property_sheet_name_set = set(site.portal_property_sheets.objectIds())

      except AttributeError:
        if not getattr(site, '_v_bootstrapping', False):
          LOG("ERP5Type.dynamic", WARNING,
              "Property Sheet Tool was not found. Please update erp5_core "
              "Business Template")

      else:
        for property_sheet in zodb_property_sheet_name_set:
          if property_sheet.endswith('Preference'):
            property_sheet_name_set.add(property_sheet)

      # XXX a hook to add per-portal type accessor holders maybe?
      if portal_type_name == "Preference Tool":
        from Products.ERP5Form.Document.PreferenceToolType import \
            _generatePreferenceToolAccessorHolder

        accessor_holder_class = _generatePreferenceToolAccessorHolder(
          portal_type_name, accessor_holder_list)

        accessor_holder_list.insert(0, accessor_holder_class)

  # Get the Property Sheets defined on the document and its bases
  # recursively
  for property_sheet in getClassPropertyList(type_class):
    # If the Property Sheet is a string, then this is a ZODB
    # Property Sheet
    #
    # NOTE: The Property Sheets of a document should be given as a
    #       string from now on
    if not isinstance(property_sheet, basestring):
      property_sheet = property_sheet.__name__

    property_sheet_name_set.add(property_sheet)

  property_sheet_name_set = property_sheet_name_set - \
      portal_type_property_sheet_name_set

  document_accessor_holder_list = \
      getAccessorHolderList(site, portal_type_name,
                            getPropertySheetValueList(site,
                                                      property_sheet_name_set))

  accessor_holder_list.extend(document_accessor_holder_list)

  # useless if Base Category is not yet here or if we're
  # currently generating accessors for Base Categories
  accessor_holder_class = _generateBaseAccessorHolder(site)

  if accessor_holder_class is not None:
    accessor_holder_list.append(accessor_holder_class)

  return accessor_holder_list
