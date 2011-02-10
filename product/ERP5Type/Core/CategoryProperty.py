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
from Products.ERP5Type.XMLObject import XMLObject

from Products.ERP5Type.Accessor.Base import Getter as BaseGetter
from Products.ERP5Type.Accessor import Category, Value, Alias
from Products.ERP5Type.Utils import UpperCase

from Products.ERP5Type.Core.StandardProperty import StandardProperty

class CategoryProperty(XMLObject):
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

  getReference = BaseGetter('getReference', 'reference', 'string',
                            storage_id='default_reference')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'exportToFilesystemDefinition')
  def exportToFilesystemDefinition(self):
    """
    Return the filesystem definition of the property
    """
    return self.getReference()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'importFromFilesystemDefinition')
  @classmethod
  def importFromFilesystemDefinition(cls, context, category_name):
    """
    Set the Reference from a filesystem definition of a property
    """
    return context.newContent(portal_type=cls.portal_type,
                              reference=category_name)

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
      # public 'reindexers'
      'set%sValue': Alias.Reindex,
      'set%sValueList': Alias.Reindex,
      'set%sValueSet': Alias.Reindex,
      'setDefault%sValue': Alias.Reindex,
      'set%sUid': Alias.Reindex,
      'set%sUidList': Alias.Reindex,
      'set%sUidSet': Alias.Reindex,
      'setDefault%sUid': Alias.Reindex,
      # setters
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
  def applyPropertyOnAccessorHolder(cls,
                                    accessor_holder,
                                    category_id,
                                    category_tool):
    # Create free text accessors.
    # XXX These are only for backward compatibility.
    storage_id = None
    if category_id == 'group':
      storage_id = 'group'
    elif category_id == 'site':
      storage_id = 'location'

    StandardProperty.applyPropertyOnAccessorHolder(
                      accessor_holder=accessor_holder,
                      reference='%s_free_text' % category_id,
                      elementary_type='text',
                      is_multivalues=False,
                      property_default='',
                      storage_id=storage_id,
                      read_permission=Permissions.AccessContentsInformation,
                      write_permission=Permissions.ModifyPortalContent)

    # Get read and write permission
    if category_tool is not None:
      cat_object = category_tool.get(category_id, None)
    else:
      cat_object = None
    if cat_object is not None:
      read_permission = Permissions.__dict__.get(
                              cat_object.getReadPermission(),
                              Permissions.AccessContentsInformation)
      write_permission = Permissions.__dict__.get(
                              cat_object.getWritePermission(),
                              Permissions.ModifyPortalContent)
    else:
      read_permission = Permissions.AccessContentsInformation
      write_permission = Permissions.ModifyPortalContent

    # Actually create accessors
    uppercase_reference = UpperCase(id)

    # three special cases
    accessor = Category.Tester('has' + uppercase_reference, id)
    accessor_holder.registerAccessor(accessor, read_permission)

    accessor_name = uppercase_reference[0].lower() + uppercase_reference[1:]
    accessor = Value.ListGetter(accessor_name + 'Values', id)
    accessor_holder.registerAccessor(accessor_holder, read_permission)
    accessor = Value.IdListGetter(accessor_name + 'Ids', id)
    accessor_holder.registerAccessor(accessor_holder, read_permission)

    # then getters
    for id_format, accessor_class in cls.getter_definition_dict.iteritems():
      accessor_name = id_format % uppercase_reference

      public_accessor = accessor_class(accessor_name, id)
      accessor_holder.registerAccessor(public_accessor, read_permission)

      # create the private getter on the fly instead of having a definition dict
      # that's twice the size for the same info
      accessor_name = '_category' + accessor_name[0].upper() + accessor_name[1:]
      private_accessor = accessor_class(accessor_name, id)
      accessor_holder.registerAccessor(private_accessor, read_permission)

    # and setters
    for id_format, accessor_class in cls.setter_definition_dict.iteritems():
      accessor_name = id_format % uppercase_reference

      accessor = accessor_class(accessor_name, id)
      accessor_holder.registerAccessor(accessor, write_permission)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'applyOnAccessorHolder')
  def applyOnAccessorHolder(self, accessor_holder, expression_context, portal):
    reference = self.getReference()
    if reference is not None:
      accessor_holder._categories.append(reference)
      category_tool = getattr(portal, 'portal_categories', None)
      self.applyPropertyOnAccessorHolder(accessor_holder,
                                         reference,
                                         category_tool)
