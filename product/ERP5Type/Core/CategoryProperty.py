##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type import SOURCE_DESTINATION_REFERENCE_LEGACY
from Products.ERP5Type.XMLObject import XMLObject

from Products.ERP5Type.Accessor.Base import Getter as BaseGetter
from Products.ERP5Type.Accessor import Category, Value, Alias
from Products.ERP5Type.Utils import UpperCase
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.ERP5Type.Core.StandardProperty import StandardProperty
from zLOG import LOG, WARNING
import six

class CategoryProperty(IdAsReferenceMixin('_category'), XMLObject):
  """
  Define a Category Property Document for a ZODB Property Sheets
  """
  meta_type = 'ERP5 Category Property'
  portal_type = 'Category Property'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = (PropertySheet.SimpleItem,
                     PropertySheet.Reference)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'importFromFilesystemDefinition')
  @classmethod
  def importFromFilesystemDefinition(cls, context, category_name):
    """
    Set the Reference from a filesystem definition of a property
    """
    return context.newContent(portal_type=cls.portal_type,
                              id=category_name + cls.getIdAsReferenceAffix())

  getter_definition_dict = {
      # normal accessors
      'get%sList': Category.ListGetter,
      'get%sSet': Category.SetGetter,
      'get%sItemList': Category.ItemListGetter,
      'getDefault%s': Category.DefaultGetter,
      'get%s': Category.DefaultGetter,
      # value accessors
      'get%sValueList': Value.ListGetter,
      'get%sValueSet': Value.SetGetter,
      'get%sTitleList': Value.TitleListGetter,
      'get%sTitleSet': Value.TitleSetGetter,
      'get%sTranslatedTitleList': Value.TranslatedTitleListGetter,
      'get%sTranslatedTitleSet': Value.TranslatedTitleSetGetter,
      'get%sReferenceList': Value.ReferenceListGetter,
      'get%sReferenceSet': Value.ReferenceSetGetter,
      'get%sShortTitleList': Value.ShortTitleListGetter,
      'get%sShortTitleSet': Value.ShortTitleSetGetter,
      'get%sIdList': Value.IdListGetter,
      'get%sIdSet': Value.IdSetGetter,
      'get%sLogicalPathList': Value.LogicalPathListGetter,
      'get%sLogicalPathSet': Value.LogicalPathSetGetter,
      'get%sUidList': Value.UidListGetter,
      'get%sUidSet': Value.UidSetGetter,
      'get%sPropertyList': Value.PropertyListGetter,
      'get%sPropertySet': Value.PropertySetGetter,
      'getDefault%sValue': Value.DefaultGetter,
      'get%sValue': Value.DefaultGetter,
      'getDefault%sTitle': Value.DefaultTitleGetter,
      'get%sTitle': Value.DefaultTitleGetter,
      'getDefault%sTranslatedTitle': Value.DefaultTranslatedTitleGetter,
      'get%sTranslatedTitle': Value.DefaultTranslatedTitleGetter,
      'getDefault%sReference': Value.DefaultReferenceGetter,
      'get%sReference': Value.DefaultReferenceGetter,
      'getDefault%sShortTitle': Value.DefaultShortTitleGetter,
      'get%sShortTitle': Value.DefaultShortTitleGetter,
      'getDefault%sUid': Value.DefaultUidGetter,
      'get%sUid': Value.DefaultUidGetter,
      'getDefault%sId': Value.DefaultIdGetter,
      'get%sId': Value.DefaultIdGetter,
      'getDefault%sTitleOrId': Value.DefaultTitleOrIdGetter,
      'get%sTitleOrId': Value.DefaultTitleOrIdGetter,
      'getDefault%sProperty': Value.DefaultPropertyGetter,
      'get%sProperty': Value.DefaultPropertyGetter,
      'getDefault%sLogicalPath': Value.DefaultLogicalPathGetter,
      'get%sLogicalPath': Value.DefaultLogicalPathGetter,
      'get%sTranslatedLogicalPath': Value.DefaultTranslatedLogicalPathGetter,
  }
  setter_definition_dict = {
      # setters
      '_set%s': Category.Setter,
      '_categorySet%s': Category.Setter,
      '_set%sList': Category.ListSetter,
      '_categorySet%sList': Category.ListSetter,
      '_setDefault%s': Category.DefaultSetter,
      '_categorySetDefault%s': Category.DefaultSetter,
      '_set%sSet': Category.SetSetter,
      '_categorySet%sSet': Category.SetSetter,
      '_set%sValue': Value.Setter,
      '_categorySet%sValue': Value.Setter,
      '_set%sValueList': Value.ListSetter,
      '_categorySet%sValueList': Value.ListSetter,
      '_set%sValueSet': Value.SetSetter,
      '_categorySet%sValueSet': Value.SetSetter,
      '_setDefault%sValue': Value.DefaultSetter,
      '_categorySetDefault%sValue': Value.DefaultSetter,
      # uid setters
      '_set%sUid': Value.UidSetter,
      '_categorySet%sUid': Value.UidSetter,
      '_set%sUidList': Value.UidListSetter,
      '_categorySet%sUidList': Value.UidListSetter,
      '_set%sUidSet': Value.UidSetSetter,
      '_categorySet%sUidSet': Value.UidSetSetter,
      '_setDefault%sUid': Value.UidDefaultSetter,
      '_categorySetDefault%sUid': Value.UidDefaultSetter,
  }

  @classmethod
  def applyDefinitionOnAccessorHolder(cls,
                                      accessor_holder,
                                      category_id,
                                      portal):
    try:
      cat_object = portal.portal_categories._getOb(category_id)
    except KeyError:
      if portal.hasObject('portal_categories'):
        LOG("ERP5Type.Core.CategoryProperty", WARNING,
            "Base Category %r is missing. Accessors can not be generated." % \
              category_id)

      return
    except TypeError:
      # category_id is None
      raise ValueError("Invalid category reference")

    # Create free text accessors.
    # XXX These are only for backward compatibility.
    storage_id = None
    if category_id == 'group':
      storage_id = 'group'
    elif category_id == 'site':
      storage_id = 'location'

    property_dict = {'reference': '%s_free_text' % category_id,
                     'elementary_type': 'text',
                     'property_default': '',
                     'multivalued': False,
                     'storage_id': storage_id,
                     'range': False,
                     'translatable': False,
                     'description': 'free text to specify %s' % category_id,
                     'read_permission': Permissions.AccessContentsInformation,
                     'write_permission': Permissions.ModifyPortalContent}

    StandardProperty.applyDefinitionOnAccessorHolder(property_dict,
                                                     accessor_holder,
                                                     portal,
                                                     do_register=False)

    # Get read and write permission
    read_permission = Permissions.__dict__.get(cat_object.getReadPermission(),
                                               Permissions.AccessContentsInformation)
    write_permission = Permissions.__dict__.get(cat_object.getWritePermission(),
                                                Permissions.ModifyPortalContent)

    # Actually create accessors
    uppercase_category_id = UpperCase(category_id)

    # three special cases
    accessor = Category.Tester('has' + uppercase_category_id, category_id)
    accessor_holder.registerAccessor(accessor, read_permission)

    accessor_name = uppercase_category_id[0].lower() + uppercase_category_id[1:]
    accessor = Value.ListGetter(accessor_name + 'Values', category_id)
    accessor_holder.registerAccessor(accessor, read_permission)
    accessor = Value.IdListGetter(accessor_name + 'Ids', category_id)
    accessor_holder.registerAccessor(accessor, read_permission)

    # then getters
    for id_format, accessor_class in six.iteritems(cls.getter_definition_dict):
      accessor_name = id_format % uppercase_category_id
      # XXX getSourceReference/getDestinationReference are already generated by
      # 'source_reference' and 'destination_reference' standard properties. To
      # prevent name conflict, we don't generate them as a category accessor.
      if not (SOURCE_DESTINATION_REFERENCE_LEGACY and accessor_name in (
              'getSourceReference', 'getDestinationReference')):
        public_accessor = accessor_class(accessor_name, category_id)
        accessor_holder.registerAccessor(public_accessor, read_permission)

      # create the private getter on the fly instead of having a definition dict
      # that's twice the size for the same info
      accessor_name = '_category' + accessor_name[0].upper() + accessor_name[1:]
      private_accessor = accessor_class(accessor_name, category_id)
      accessor_holder.registerAccessor(private_accessor, read_permission)

    # and setters
    for id_format, accessor_class in six.iteritems(cls.setter_definition_dict):
      accessor_name = id_format % uppercase_category_id
      # XXX setSourceReference/setDestinationReference are already generated by
      # 'source_reference' and 'destination_reference' standard properties. To
      # prevent name conflict, we don't generate them as a category accessor.
      if SOURCE_DESTINATION_REFERENCE_LEGACY and accessor_name in (
                  'setSourceReference', 'setDestinationReference'):
        continue

      accessor = accessor_class(accessor_name, category_id)
      accessor_holder.registerAccessor(accessor, write_permission)

      # TODO: merge with StandardProperty
      if accessor_name.startswith('_set'):
        accessor = Alias.Reindex(accessor_name[1:], accessor_name)
        accessor_holder.registerAccessor(accessor, write_permission)

    # Only add the category ID if it is not already in _categories,
    # which may happen when getting the categories with acquisition
    if category_id not in accessor_holder._categories:
      accessor_holder._categories.append(category_id)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'applyOnAccessorHolder')
  def applyOnAccessorHolder(self, accessor_holder, expression_context, portal):
    self.applyDefinitionOnAccessorHolder(accessor_holder,
                                         self.getReference(),
                                         portal)
