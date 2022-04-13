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
from Products.CMFCore.Expression import Expression
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Core.StandardProperty import StandardProperty
from Products.ERP5Type.Utils import UpperCase, evaluateExpressionFromString
from Products.ERP5Type.Accessor.TypeDefinition import list_types
from Products.ERP5Type.Accessor import Base, List, Content, ContentProperty, \
     Acquired, Alias, Translation, AcquiredProperty as AcquiredPropertyAccessor

from zLOG import LOG, WARNING
import six

class AcquiredProperty(StandardProperty):
  """
  Define an Acquired Property Document for a ZODB Property Sheet (an
  Acquired Property only brings new attributes to a Standard Property)

  In addition of a Standard Property, an Acquired Property contains
  the following attributes:
   - acquisition_base_category: lines
   - acquisition_object_id: lines
   - acquisition_portal_type: lines
   - acquisition_accessor_id: string
   - alt_accessor_id: lines
   - acquisition_copy_value: boolean (default: False)
   - acquisition_mask_value: boolean (default: False)

  Specific to content type:
   - content_portal_type: string
   - content_acquired_property_id: lines
   - content_translation_acquired_property_id: lines
  """
  meta_type = 'ERP5 Acquired Property'
  portal_type = 'Acquired Property'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = StandardProperty.property_sheets + \
      (PropertySheet.AcquiredProperty,)

  # Filesystem-based name of attributes specific to 'content' type
  _content_type_attribute_tuple = ('portal_type',
                                   'acquired_property_id',
                                   'translation_acquired_property_id')

  # Add names specific to 'content' type (see StandardProperty)
  _name_mapping_filesystem_to_zodb_dict = {name: 'content_' + name
    for name in _content_type_attribute_tuple}
  _name_mapping_filesystem_to_zodb_dict.update(
    StandardProperty._name_mapping_filesystem_to_zodb_dict)

  # ZODB name of attributes whose value is a TALES Expression string
  _expression_attribute_tuple = \
      StandardProperty._expression_attribute_tuple + \
      ('acquisition_portal_type', 'content_portal_type')

  # Define getters for the property. This is necessary for bootstrap
  # as a Standard Property uses SimpleItem, defined with Acquired
  # Properties
  #
  # There is no need to define the setter as this static definition of
  # the getter is only meaningful for the Acquired Properties defined
  # within an Acquired Property.
  getAcquisitionBaseCategoryList = List.ListGetter(
    'getAcquisitionBaseCategoryList',
    'acquisition_base_category',
    'lines')

  getAcquisitionObjectIdList = List.ListGetter('getAcquisitionObjectIdList',
                                               'acquisition_object_id',
                                               'lines')

  # Define as a TALES expression string, use for Expression
  # instanciation when exporting the property to the filesystem
  # definition
  getAcquisitionPortalType = Base.Getter('getAcquisitionPortalType',
                                         'acquisition_portal_type',
                                         'string')

  getAcquisitionAccessorId = Base.Getter('getAcquisitionAccessorId',
                                         'acquisition_accessor_id',
                                         'string')

  getAltAccessorIdList = List.ListGetter('getAltAccessorIdList',
                                         'alt_accessor_id',
                                         'lines')

  getAcquisitionCopyValue = Base.Getter('getAcquisitionCopyValue',
                                        'acquisition_copy_value',
                                        'boolean',
                                        default=False)

  getAcquisitionMaskValue = Base.Getter('getAcquisitionMaskValue',
                                        'acquisition_mask_value',
                                        'boolean',
                                        default=False)

  # Define as a TALES expression string, use for Expression
  # instanciation when exporting the property to the filesystem
  # definition
  getContentPortalType = Base.Getter('getContentPortalType',
                                     'content_portal_type',
                                     'string')

  getContentAcquiredPropertyIdList = List.ListGetter(
    'getContentAcquiredPropertyIdList',
    'content_acquired_property_id',
    'lines')

  getContentTranslationAcquiredPropertyIdList = List.ListGetter(
    'getContentTranslationAcquiredPropertyIdList',
    'content_translation_acquired_property_id',
    'lines')

  @classmethod
  def _asPropertyMap(cls, property_dict):
    """
    @see Products.ERP5Type.Core.StandardProperty._asPropertyMap
    """
    property_map = super(AcquiredProperty, cls)._asPropertyMap(property_dict)

    property_map['portal_type'] = property_map.pop('content_portal_type')
    property_map['acquired_property_id'] = \
        property_map.pop('content_acquired_property_id')

    property_map['translation_acquired_property_id'] = \
        property_map.pop('content_translation_acquired_property_id')

    # Set acquisition values as read only if no value is copied
    # TODO: useful?
    if not (property_map['acquisition_base_category'] is None or \
            property_map['acquisition_copy_value']):
      property_map['mode'] = 'r'

    return property_map

  _acquisition_base_category_getter_definition_dict = {
    'get%s': Acquired.Getter,
    '_baseGet%s': Acquired.Getter,
    'getDefault%s': Acquired.DefaultGetter,
    '_baseGetDefault%s': Acquired.DefaultGetter,
  }

  _acquisition_base_category_list_type_getter_definition_dict = {
    'get%sList': Acquired.ListGetter,
    '_baseGet%sList': Acquired.ListGetter,
    'get%sSet': Acquired.SetGetter,
    '_baseGet%sSet': Acquired.SetGetter
  }

  _acquisition_base_category_content_type_getter_definition_dict = {
    'get%sValue': Acquired.Getter,
    '_baseGet%sValue': Acquired.Getter,
    'getDefault%sValue': Acquired.DefaultGetter,
    '_baseGetDefault%sValue': Acquired.DefaultGetter,
    'get%sValueList': Acquired.ListGetter,
    '_baseGet%sValueList': Acquired.ListGetter
  }

  _content_type_getter_definition_dict = {
    'get%s': Content.Getter,
    '_baseGet%s': Content.Getter,
    'getDefault%s': Content.DefaultGetter,
    '_baseGetDefault%s': Content.DefaultGetter,
    'get%sList': Content.ListGetter,
    '_baseGet%sList': Content.ListGetter,
    'get%sValue': Content.ValueGetter,
    '_baseGet%sValue': Content.ValueGetter,
    'getDefault%sValue': Content.DefaultValueGetter,
    '_baseGetDefault%sValue': Content.DefaultValueGetter,
    'get%sValueList': Content.ValueListGetter,
    '_baseGet%sValueList': Content.ValueListGetter
  }

  @classmethod
  def _applyGetterDefinitionDictOnAccessorHolder(cls,
                                                 property_dict,
                                                 accessor_holder):
    """
    Apply getters for the given acquired property on the given
    accessor holder. Basically, any Acquired Property which does not
    set acquisition_base_category or elementary_type to 'content' gets
    the StandardProperty getters.

    @see StandardProperty._applyGetterDefinitionDictOnAccessorHolder
    """
    if property_dict['acquisition_base_category'] is not None:
      is_list_type = property_dict['elementary_type'] in list_types or \
          property_dict['multivalued']

      argument_list = (property_dict['elementary_type'],
                       property_dict['property_default'],
                       property_dict['acquisition_base_category'],
                       property_dict['acquisition_portal_type'],
                       property_dict['acquisition_accessor_id'],
                       property_dict['acquisition_copy_value'],
                       property_dict['acquisition_mask_value'],
                       property_dict['storage_id'],
                       property_dict['alt_accessor_id'],
                       property_dict['acquisition_object_id'],
                       is_list_type,
                       property_dict['elementary_type'] == 'tales')

      definition_dict = cls._acquisition_base_category_getter_definition_dict.copy()

      if is_list_type:
        definition_dict.update(
          cls._acquisition_base_category_list_type_getter_definition_dict)

      if property_dict['elementary_type'] == 'content':
        definition_dict.update(
          cls._acquisition_base_category_content_type_getter_definition_dict)

    elif property_dict['elementary_type'] == 'content':
      argument_list = (property_dict['elementary_type'],
                       property_dict['content_portal_type'],
                       property_dict['storage_id'])

      definition_dict = cls._content_type_getter_definition_dict

    else:
      super(AcquiredProperty, cls)._applyGetterDefinitionDictOnAccessorHolder(
        property_dict, accessor_holder)

      return

    cls._applyDefinitionFormatDictOnAccessorHolder(
      property_dict['reference'], definition_dict, accessor_holder,
      argument_list, property_dict['read_permission'])

  _content_type_setter_definition_dict = {
    '_set%s': Content.Setter,
    '_baseSet%s': Content.Setter,
    '_setDefault%s': Content.DefaultSetter,
    '_baseSetDefault%s': Content.DefaultSetter,
    '_set%sValue': Content.Setter,
    '_baseSet%sValue': Content.Setter,
    '_setDefault%sValue': Content.DefaultSetter,
    '_baseSetDefault%sValue': Content.DefaultSetter
  }

  @classmethod
  def _applySetterDefinitionDictOnAccessorHolder(cls,
                                                 property_dict,
                                                 accessor_holder):
    """
    Apply setters for the given acquired property on the given
    accessor holder. Basically, an AcquiredProperty whose
    elementary_type is not 'content' gets the StandardProperty
    setters.

    @see StandardProperty_.applySetterDefinitionDictOnAccessorHolder
    """
    if property_dict['elementary_type'] == 'content':
      argument_list = (property_dict['elementary_type'],
                       property_dict['storage_id'])

      cls._applyDefinitionFormatDictOnAccessorHolder(
        property_dict['reference'], cls._content_type_setter_definition_dict,
        accessor_holder, argument_list, property_dict['write_permission'])

    else:
      super(AcquiredProperty, cls)._applySetterDefinitionDictOnAccessorHolder(
        property_dict, accessor_holder)

  _content_type_tester_definition_dict = {
    'has%s': Content.Tester
  }

  @classmethod
  def _applyTesterDefinitionDictOnAccessorHolder(cls,
                                                 property_dict,
                                                 accessor_holder):
    """
    Apply testers for the given acquired property on the given
    accessor holder. Basically, an AcquiredProperty whose
    elementary_type is not 'content' gets the StandardProperty
    testers.

    @see StandardProperty_.applySetterDefinitionDictOnAccessorHolder
    """
    if property_dict['elementary_type'] == 'content':
      argument_list = (property_dict['elementary_type'],
                       property_dict['storage_id'])
      reference = property_dict['reference']
      for composed_id in (reference, 'default_' + reference,):
        cls._applyDefinitionFormatDictOnAccessorHolder(
          composed_id, cls._content_type_tester_definition_dict,
          accessor_holder, argument_list, property_dict['read_permission'])

    else:
      super(AcquiredProperty, cls)._applyTesterDefinitionDictOnAccessorHolder(
        property_dict, accessor_holder)

  _translation_acquired_getter_definition_dict = {
    'get%s': Translation.AcquiredPropertyGetter,
    '_baseGet%s': Translation.AcquiredPropertyGetter,
    'getDefault%s': Translation.AcquiredPropertyGetter
  }

  @classmethod
  def _applyTranslationAcquiredGetterDefinitionDictOnAccessorHolder(cls,
     capitalised_composed_id, key, property_dict, accessor_holder):
    for name_format, klass in \
          six.iteritems(cls._translation_acquired_getter_definition_dict):
      instance = klass(
        name_format % capitalised_composed_id, key,
        property_dict['elementary_type'],
        property_dict['content_portal_type'],
        key,
        property_dict['acquisition_base_category'],
        property_dict['acquisition_portal_type'],
        property_dict['acquisition_accessor_id'],
        property_dict['acquisition_copy_value'],
        property_dict['acquisition_mask_value'],
        property_dict['storage_id'],
        property_dict['alt_accessor_id'],
        property_dict['acquisition_object_id'],
        (property_dict['elementary_type'] in list_types or \
         property_dict['multivalued']),
        (property_dict['elementary_type'] == 'tales'))

      accessor_holder.registerAccessor(instance,
                                       property_dict['read_permission'])

  @classmethod
  def _applyTranslationAcquiredOnAccessorHolder(cls,
                                                property_dict,
                                                accessor_holder,
                                                portal):
    try:
      localizer = portal._getOb('Localizer')
    except AttributeError:
      # TODO: should pbe merged with StandardProperty?
      if not getattr(portal, '_v_bootstrapping', False):
        LOG("ERP5Type.Core.StandardProperty", WARNING,
            "Localizer is missing. Accessors can not be generated")

      return

    for acquired_property_id in property_dict['content_acquired_property_id']:
      key = 'translated_' + acquired_property_id

      # Language-dependent accessors
      for language in localizer.get_languages():
        language_key = language.replace('-', '_') + '_' + key

        capitalised_composed_id = UpperCase("%s_%s" % \
                                              (property_dict['reference'],
                                               language_key))

        cls._applyTranslationAcquiredGetterDefinitionDictOnAccessorHolder(
          capitalised_composed_id, language_key, property_dict, accessor_holder)

        setter_instance = AcquiredPropertyAccessor.DefaultSetter(
          '_set' + capitalised_composed_id, language_key,
          property_dict['elementary_type'],
          property_dict['content_portal_type'],
          language_key,
          property_dict['acquisition_base_category'],
          property_dict['acquisition_portal_type'],
          property_dict['acquisition_accessor_id'],
          property_dict['acquisition_copy_value'],
          property_dict['acquisition_mask_value'],
          property_dict['storage_id'],
          property_dict['alt_accessor_id'],
          property_dict['acquisition_object_id'],
          (property_dict['elementary_type'] in list_types or \
           property_dict['multivalued']),
          (property_dict['elementary_type'] == 'tales'))

        accessor_holder.registerAccessor(setter_instance,
                                         property_dict['write_permission'])

        alias_reindex_setter = Alias.Reindex('set' + capitalised_composed_id,
                                             '_set' + capitalised_composed_id)

        accessor_holder.registerAccessor(alias_reindex_setter,
                                         property_dict['write_permission'])

        alias_reindex_setter = Alias.Reindex(
          'setDefault' + capitalised_composed_id,
          '_set' + capitalised_composed_id)

        accessor_holder.registerAccessor(alias_reindex_setter,
                                         property_dict['write_permission'])

      # Language-independent accessors
      if acquired_property_id in \
         property_dict['content_translation_acquired_property_id']:
        capitalised_composed_id = UpperCase('%s_%s' % \
                                              (property_dict['reference'],
                                               key))

        cls._applyTranslationAcquiredGetterDefinitionDictOnAccessorHolder(
          capitalised_composed_id, key, property_dict, accessor_holder)

  _acquisition_base_category_acquired_property_id_getter_definition_dict = {
    'get%s': AcquiredPropertyAccessor.Getter,
    '_baseGet%s': AcquiredPropertyAccessor.Getter,
    'getDefault%s': AcquiredPropertyAccessor.DefaultGetter,
    '_baseGetDefault%s': AcquiredPropertyAccessor.DefaultGetter,
  }

  _acquisition_base_category_acquired_property_id_tester_definition_dict = {
    'has%s': AcquiredPropertyAccessor.Tester,
  }

  _acquisition_base_category_acquired_property_id_setter_definition_dict = {
    '_set%s': AcquiredPropertyAccessor.Setter,
    '_baseSet%s': AcquiredPropertyAccessor.Setter,
    '_setDefault%s': AcquiredPropertyAccessor.DefaultSetter,
    '_baseSetDefault%s': AcquiredPropertyAccessor.DefaultSetter
  }

  @classmethod
  def _applyAcquisitionBaseCategoryAcquiredPropertyOnAccessorHolder(cls,
                                                                    aq_id,
                                                                    property_dict,
                                                                    accessor_holder):
    acquired_property_id_argument_list = (
      property_dict['elementary_type'],
      property_dict['content_portal_type'],
      aq_id,
      property_dict['acquisition_base_category'],
      property_dict['acquisition_portal_type'],
      property_dict['acquisition_accessor_id'],
      property_dict['acquisition_copy_value'],
      property_dict['acquisition_mask_value'],
      property_dict['storage_id'],
      property_dict['alt_accessor_id'],
      property_dict['acquisition_object_id'],
      property_dict['multivalued'],
      property_dict['elementary_type'] == 'tales')

    for composed_id in ("%s_%s" % (property_dict['reference'], aq_id),
                        "default_%s_%s" % (property_dict['reference'], aq_id)):

      cls._applyDefinitionFormatDictOnAccessorHolder(
        composed_id,
        cls._acquisition_base_category_acquired_property_id_getter_definition_dict,
        accessor_holder,
        acquired_property_id_argument_list,
        property_dict['read_permission'])

      cls._applyDefinitionFormatDictOnAccessorHolder(
        composed_id,
        cls._acquisition_base_category_acquired_property_id_tester_definition_dict,
        accessor_holder,
        acquired_property_id_argument_list,
        property_dict['read_permission'])

      cls._applyDefinitionFormatDictOnAccessorHolder(
        composed_id,
        cls._acquisition_base_category_acquired_property_id_setter_definition_dict,
        accessor_holder,
        acquired_property_id_argument_list,
        property_dict['write_permission'])

  _content_type_acquired_property_id_getter_definition_dict = {
    'get%s': ContentProperty.Getter
  }

  _content_type_acquired_property_id_setter_definition_dict = {
    '_set%s': ContentProperty.Setter,
    '_baseSet%s': ContentProperty.Setter
  }

  _content_type_acquired_property_id_tester_definition_dict = {
    'has%s': ContentProperty.Tester
  }

  @classmethod
  def _applyContentTypeAcquiredPropertyOnAccessorHolder(cls,
                                                        aq_id,
                                                        property_dict,
                                                        accessor_holder):
    acquired_property_id_argument_list = (property_dict['elementary_type'],
                                          aq_id,
                                          property_dict['content_portal_type'],
                                          property_dict['storage_id'])

    acquired_property_id_list_argument_list = (property_dict['elementary_type'],
                                               aq_id + '_list',
                                               property_dict['content_portal_type'],
                                               property_dict['storage_id'])

    for composed_id in ('%s_%s' % (property_dict['reference'], aq_id),
                        "default_%s_%s" % (property_dict['reference'], aq_id)):
      cls._applyDefinitionFormatDictOnAccessorHolder(
        composed_id,
        cls._content_type_acquired_property_id_getter_definition_dict,
        accessor_holder,
        acquired_property_id_argument_list,
        property_dict['read_permission'])

      cls._applyDefinitionFormatDictOnAccessorHolder(
        composed_id,
        cls._content_type_acquired_property_id_setter_definition_dict,
        accessor_holder,
        acquired_property_id_argument_list,
        property_dict['write_permission'])

      cls._applyDefinitionFormatDictOnAccessorHolder(
        composed_id,
        cls._content_type_acquired_property_id_tester_definition_dict,
        accessor_holder,
        acquired_property_id_argument_list,
        property_dict['read_permission'])

      cls._applyDefinitionFormatDictOnAccessorHolder(
        composed_id + '_list',
        cls._content_type_acquired_property_id_getter_definition_dict,
        accessor_holder,
        acquired_property_id_list_argument_list,
        property_dict['read_permission'],)

      cls._applyDefinitionFormatDictOnAccessorHolder(
        composed_id + '_list',
        cls._content_type_acquired_property_id_setter_definition_dict,
        accessor_holder,
        acquired_property_id_list_argument_list,
        property_dict['write_permission'])

      cls._applyDefinitionFormatDictOnAccessorHolder(
        composed_id + '_list',
        cls._content_type_acquired_property_id_tester_definition_dict,
        accessor_holder,
        acquired_property_id_argument_list,
        property_dict['read_permission'])

  @classmethod
  def applyDefinitionOnAccessorHolder(cls,
                                      property_dict,
                                      accessor_holder,
                                      portal,
                                      do_register=True):
    if property_dict['content_translation_acquired_property_id']:
      cls._applyTranslationAcquiredOnAccessorHolder(property_dict,
                                                    accessor_holder,
                                                    portal)

    if property_dict['elementary_type'] == 'content':
      if property_dict['acquisition_base_category']:
        apply_method = cls._applyAcquisitionBaseCategoryAcquiredPropertyOnAccessorHolder
      else:
        apply_method = cls._applyContentTypeAcquiredPropertyOnAccessorHolder

      for aq_id in property_dict['content_acquired_property_id']:
        apply_method(aq_id, property_dict, accessor_holder)

    super(AcquiredProperty, cls).applyDefinitionOnAccessorHolder(
      property_dict, accessor_holder, portal, do_register=do_register)

  @classmethod
  def _applyRangeOnAccessorHolder(cls, property_dict, accessor_holder, kind,
                                  portal):
    acquisition_accessor_id = property_dict.get('acquisition_accessor_id', None)
    if acquisition_accessor_id is not None:
      property_dict['acquisition_accessor_id'] = '%sRange%s' % \
          (acquisition_accessor_id, kind.capitalize())

    property_dict['alt_accessor_id'] = ('get' + \
                                        UpperCase(property_dict['reference']),)

    super(AcquiredProperty, cls)._applyRangeOnAccessorHolder(property_dict,
                                                             accessor_holder,
                                                             kind,
                                                             portal)
  def asDict(self, expression_context=None):
    property_dict = super(AcquiredProperty, self).asDict(expression_context)

    acquisition_portal_type_value = evaluateExpressionFromString(
      expression_context, self.getAcquisitionPortalType())

    content_portal_type_value = evaluateExpressionFromString(
      expression_context, self.getContentPortalType())

    property_dict.update(
      acquisition_portal_type=acquisition_portal_type_value,
      content_portal_type=content_portal_type_value,
      acquisition_base_category=self.getAcquisitionBaseCategoryList(),
      acquisition_object_id=self.getAcquisitionObjectIdList(),
      acquisition_accessor_id=self.getAcquisitionAccessorId(),
      alt_accessor_id=self.getAltAccessorIdList(),
      acquisition_copy_value=self.getAcquisitionCopyValue(),
      acquisition_mask_value=self.getAcquisitionMaskValue(),
      content_acquired_property_id=self.getContentAcquiredPropertyIdList(),
      content_translation_acquired_property_id=self.getContentTranslationAcquiredPropertyIdList())

    return property_dict
