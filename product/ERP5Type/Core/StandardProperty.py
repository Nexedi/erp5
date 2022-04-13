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
from Products.ERP5Type.XMLObject import XMLObject

from zLOG import LOG, WARNING, INFO
from Products.ERP5Type.Accessor import Base, List, Alias, Translation
from Products.ERP5Type.Accessor.TypeDefinition import type_definition, list_types
from Products.ERP5Type.Utils import UpperCase, createExpressionContext, \
     evaluateExpressionFromString
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
import six

class StandardProperty(IdAsReferenceMixin('_property'), XMLObject):
  """
  Define a Standard Property Document for a ZODB Property Sheet

  A Standard Property contains the following attributes:
   - reference: string
   - description: string
   - elementary_type: string
   - storage_id: string
   - multivalued: boolean (default: False)
   - property_default: TALES Expression as a string
   - range: boolean (default: False)
   - preference: boolean (default: False)
   - read_permission: string (default: Permissions.AccessContentsInformation)
   - write_permission: string (default: Permissions.ModifyPortalContent)
   - translatable: boolean (default: False)
   - translation_domain: string
  """
  meta_type = 'ERP5 Standard Property'
  portal_type = 'Standard Property'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = (PropertySheet.SimpleItem,
                     PropertySheet.StandardProperty,
                     PropertySheet.Reference,
                     PropertySheet.TranslatableProperty)

  # Names mapping between filesystem to ZODB property, only meaningful
  # when importing a property from its filesystem definition
  _name_mapping_filesystem_to_zodb_dict = {'type': 'elementary_type',
                                           'default': 'property_default'}

  # ZODB name of attributes whose value is a TALES Expression string
  _expression_attribute_tuple = ('property_default',)

  # Define getters for the property. This is necessary for bootstrap
  # as a Standard Property is defined by Standard Properties which
  # also depends on Property Sheets defined by Standard Properties.
  #
  # There is no need to define the setter as this static definition of
  # the getter is only meaningful for the Standard Properties defined
  # within an Standard Property.
  getDescription = Base.Getter('getDescription', 'description', 'string',
                               default='')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getElementaryType')
  def getElementaryType(self):
    """
    Define this getter manually as it is not possible to rely on
    CategoryTool during the bootstrap
    """
    for category in self.__dict__.get('categories', ()):
      if category.startswith('elementary_type/'):
        return category.split('elementary_type/')[1]

    return getattr(self, 'elementary_type', None)

  # The following getters have been defined to address bootstrap
  # issues
  getStorageId = Base.Getter('getStorageId', 'storage_id', 'string')

  getMultivalued = Base.Getter('getMultivalued', 'multivalued', 'boolean',
                               default=False)

  # Define as a TALES expression string, use for Expression
  # instanciation when exporting the property to the filesystem
  # definition
  getPropertyDefault = Base.Getter('getPropertyDefault', 'property_default',
                                   'string')

  getRange = Base.Getter('getRange', 'range', 'boolean', default=False)

  getPreference = Base.Getter('getPreference', 'preference', 'boolean',
                              default=False)

  getReadPermission = Base.Getter(
    'getReadPermission', 'read_permission', 'string',
    default=Permissions.AccessContentsInformation)

  getWritePermission = Base.Getter('getWritePermission',
                                   'write_permission',
                                   'string',
                                   default=Permissions.ModifyPortalContent)

  getTranslatable = Base.Getter('getTranslatable', 'translatable', 'boolean',
                                default=False)

  getTranslationDomain = Base.Getter('getTranslationDomain',
                                     'translation_domain',
                                     'string')

  getSelectVariable = Base.Getter('getSelectVariable',
                                  'select_variable',
                                  'string')

  @classmethod
  def _asPropertyMap(cls, property_dict):
    """
    Return the Zope definition of this ZODB property, as used by the
    PropertyManager (for the ZMI for example).

    ERP5 _properties and Zope _properties are somehow different. The
    id is converted to the Zope standard - we keep the original id as
    base_id.

    @param property_dict: ZODB property dict
    @type property_dict: dict
    @return: PropertyManager definition
    @rtype: dict
    """
    property_dict['type'] = property_dict.pop('elementary_type')
    property_dict['default'] = property_dict.pop('property_default')

    property_dict['id'] = property_dict.pop('reference')

    # In case, this property is a list, then display it as a list
    if property_dict['type'] in list_types or property_dict['multivalued']:
      property_dict['base_id'] = property_dict['id']
      property_dict['id'] = property_dict['id'] + '_list'

    # Maintain consistency while displaying properties form.
    # Addition of select_variable property is required for 'selection'
    # and 'multiple selection' property type as while rendering properties
    # dtml file, it asks for 'select_variable' property
    if property_dict['type'] in ['selection', 'multiple selection']:
      property_dict['select_variable'] = property_dict.pop('select_variable')

    return property_dict

  @staticmethod
  def _applyDefinitionFormatDictOnAccessorHolder(reference,
                                                 definition_dict,
                                                 accessor_holder,
                                                 argument_list,
                                                 permission):
    """
    Apply a definition dict, a format string defining the accessor
    name as the key (formatted with the given reference) and the
    accessor class to be used as the value, on the given accessor
    holder class.

    The accessor class given in the definition dict is instanciated
    with the given argument list and the the accessor is protected
    using the given permission (which may be either read if it is a
    getter or tester, or write if it is a setter), it is then
    registered on the accessor holder.

    For most cases, the reference is used in the accessor name but
    there are exceptions, such as translation accessors.

    @param reference: Reference to be used to format accessor name
    @type reference: str
    @param definition_dict: Definition of accessors being created
    @type definition_dict: dict
    @param accessor_holder: Accessor holder to applied the accessors on
    @type accessor_holder: Products.ERP5Type.dynamic.accessor_holder.AccessorHolderType
    @param argument_list: Arguments to be given to the accessor class constructor
    @type argument_list: list
    @param permission: Permission to be applied on the accessor
    @type permission: str
    """
    uppercase_reference = UpperCase(reference)
    for format, klass in six.iteritems(definition_dict):
      name = format % uppercase_reference

      instance = klass(name, reference, *argument_list)
      accessor_holder.registerAccessor(instance, permission)

      # Public setters actually just calls the private one and then
      # perform a re-indexing
      if name.startswith('_set'):
        instance = Alias.Reindex(name[1:], name)
        accessor_holder.registerAccessor(instance, permission)

  @classmethod
  def _applyRangeOnAccessorHolder(cls,
                                  property_dict,
                                  accessor_holder,
                                  kind,
                                  portal):
    """
    Apply range accessors.

    @param property_dict: Property to generate getter for
    @type property_dict: dict
    @param accessor_holder: Accessor holder to applied the accessors on
    @type accessor_holder: Products.ERP5Type.dynamic.accessor_holder.AccessorHolderType
    @param kind: 'min' or 'max'
    @type kind: string
    @param portal: Portal object
    @type portal: Products.ERP5.ERP5Site.ERP5Site
    """
    property_dict['reference'] = '%s_range_%s' % (property_dict['reference'],
                                                  kind)

    # Override storage_id to not store the value on the same attribute
    # as the "normal" accessor
    property_dict['storage_id'] = None

    # Set range to False to avoid infinite recursion upon
    # applyDefinitionOnAccessorHolder call
    property_dict['range'] = False

    cls.applyDefinitionOnAccessorHolder(property_dict,
                                        accessor_holder,
                                        portal,
                                        do_register=False)

  _translation_language_getter_definition_dict = {
    'get%s': Translation.TranslatedPropertyGetter,
    '_baseGet%s': Translation.TranslatedPropertyGetter
  }

  _translation_language_getter_definition_dict = {
    'get%s': Translation.TranslatedPropertyGetter,
    '_baseGet%s': Translation.TranslatedPropertyGetter
  }

  _translation_language_tester_definition_dict = {
    'has%s': Translation.TranslatedPropertyTester
  }

  _translation_language_setter_definition_dict = {
    '_set%s': Translation.TranslationPropertySetter
  }

  @classmethod
  def _applyTranslationLanguageOnAccessorHolder(cls,
                                                property_dict,
                                                accessor_holder,
                                                portal):
    """
    Apply translation language accessors.

    @param property_dict: Property to generate getter for
    @type property_dict: dict
    @param accessor_holder: Accessor holder to applied the accessors on
    @type accessor_holder: Products.ERP5Type.dynamic.accessor_holder.AccessorHolderType
    @param portal: Portal object
    @type portal: Products.ERP5.ERP5Site.ERP5Site
    """
    try:
      localizer = portal._getOb('Localizer')
    except AttributeError:
      if not getattr(portal, '_v_bootstrapping', False):
        LOG("ERP5Type.Core.StandardProperty", WARNING,
            "Localizer is missing. Accessors can not be generated")

      return

    # Apply language-specific accessors
    for language in localizer.get_languages():
      translation_language_id = '%s_translated_%s' % \
          (language.replace('-', '_'),
           property_dict['reference'])

      # Prepare accessor arguments for getters
      getter_argument_list = (property_dict['reference'],
                              property_dict['elementary_type'],
                              language,
                              property_dict['property_default'])

      cls._applyDefinitionFormatDictOnAccessorHolder(
        translation_language_id,
        cls._translation_language_getter_definition_dict,
        accessor_holder,
        getter_argument_list,
        property_dict['read_permission'])

      # Prepare accessor arguments for testers and setters
      tester_setter_argument_list = (property_dict['reference'],
                                     property_dict['elementary_type'],
                                     language)

      cls._applyDefinitionFormatDictOnAccessorHolder(
        translation_language_id,
        cls._translation_language_tester_definition_dict,
        accessor_holder,
        tester_setter_argument_list,
        property_dict['read_permission'])

      cls._applyDefinitionFormatDictOnAccessorHolder(
        translation_language_id,
        cls._translation_language_setter_definition_dict,
        accessor_holder,
        tester_setter_argument_list,
        property_dict['write_permission'])

  _primitive_getter_definition_dict = {
    'get%s': Base.Getter,
    '_baseGet%s': Base.Getter
  }

  _list_getter_definition_dict = {
    'get%s': List.Getter,
    '_baseGet%s': List.Getter,
    'getDefault%s': List.DefaultGetter,
    '_baseGetDefault%s': List.DefaultGetter,
    'get%sList': List.ListGetter,
    '_baseGet%sList': List.ListGetter,
    'get%sSet': List.SetGetter,
    '_baseGet%sSet': List.SetGetter
  }

  @classmethod
  def _applyGetterDefinitionDictOnAccessorHolder(cls,
                                                 property_dict,
                                                 accessor_holder):
    """
    Apply getters for the given property on the given accessor holder.
    This method is overriden in AcquiredProperty for example to add
    accessors specific to Acquired Properties.

    @param property_dict: Property to generate getter for
    @type property_dict: dict
    @param accessor_holder: Accessor holder to applied the accessors on
    @type accessor_holder: Products.ERP5Type.dynamic.accessor_holder.AccessorHolderType

    @see _applyDefinitionFormatDictOnAccessorHolder
    """
    argument_list = (property_dict['elementary_type'],
                     property_dict['property_default'],
                     property_dict['storage_id'])

    if property_dict['elementary_type'] in list_types or \
       property_dict['multivalued']:
      definition_dict = cls._list_getter_definition_dict
    else:
      definition_dict = cls._primitive_getter_definition_dict

    cls._applyDefinitionFormatDictOnAccessorHolder(
      property_dict['reference'], definition_dict, accessor_holder,
      argument_list, property_dict['read_permission'])

  _list_setter_definition_dict = {
    '_set%s': List.Setter,
    '_baseSet%s': List.Setter,
    '_setDefault%s': List.DefaultSetter,
    '_baseSetDefault%s': List.DefaultSetter,
    '_set%sList': List.ListSetter,
    '_baseSet%sList': List.ListSetter,
    '_set%sSet': List.SetSetter,
    '_baseSet%sSet': List.SetSetter
  }

  _primitive_setter_definition_dict = {
    '_set%s': Base.Setter,
    '_baseSet%s': Base.Setter
  }

  @classmethod
  def _applySetterDefinitionDictOnAccessorHolder(cls,
                                                 property_dict,
                                                 accessor_holder):
    """
    Apply setters for the given property on the given accessor holder.

    @param property_dict: Property to generate getter for
    @type property_dict: dict
    @param accessor_holder: Accessor holder to applied the accessors on
    @type accessor_holder: Products.ERP5Type.dynamic.accessor_holder.AccessorHolderType

    @see _applyGetterDefinitionDictOnAccessorHolder
    """
    argument_list = (property_dict['elementary_type'],
                     property_dict['storage_id'])

    if property_dict['elementary_type'] in list_types or \
       property_dict['multivalued']:
      definition_dict = cls._list_setter_definition_dict
    else:
      definition_dict = cls._primitive_setter_definition_dict

    cls._applyDefinitionFormatDictOnAccessorHolder(
      property_dict['reference'], definition_dict, accessor_holder,
      argument_list, property_dict['write_permission'])

  _tester_definition_dict = {
    'has%s': Base.Tester,
    '_baseHas%s': Base.Tester,
    'has%sList': List.Tester,
    '_baseHas%sList': List.Tester,
    'hasDefault%s': List.Tester,
    '_baseHasDefault%s': List.Tester
  }

  _boolean_definition_dict = {
    'is%s': Base.Getter,
    '_baseIs%s': Base.Getter
  }

  @classmethod
  def _applyTesterDefinitionDictOnAccessorHolder(cls,
                                                 property_dict,
                                                 accessor_holder):
    """
    Apply testers and boolean accessors for the given property on the
    given accessor holder.

    @param property_dict: Property to generate getter for
    @type property_dict: dict
    @param accessor_holder: Accessor holder to applied the accessors on
    @type accessor_holder: Products.ERP5Type.dynamic.accessor_holder.AccessorHolderType

    @see _applyGetterDefinitionDictOnAccessorHolder
    """
    tester_argument_list = (property_dict['elementary_type'],
                            property_dict['storage_id'])

    cls._applyDefinitionFormatDictOnAccessorHolder(
      property_dict['reference'], cls._tester_definition_dict, accessor_holder,
      tester_argument_list, property_dict['read_permission'])

    boolean_argument_list = (property_dict['elementary_type'],
                             property_dict['property_default'],
                             property_dict['storage_id'])

    cls._applyDefinitionFormatDictOnAccessorHolder(
      property_dict['reference'], cls._boolean_definition_dict, accessor_holder,
      boolean_argument_list, property_dict['read_permission'])

  _translated_getter_definition_dict = {
    'get%s': Translation.TranslatedPropertyGetter,
    '_baseGet%s': Translation.TranslatedPropertyGetter
  }

  security.declareProtected(Permissions.ModifyPortalContent,
                            'applyDefinitionOnAccessorHolder')
  @classmethod
  def applyDefinitionOnAccessorHolder(cls,
                                      property_dict,
                                      accessor_holder,
                                      portal,
                                      do_register=True):
    """
    Apply getters, setters and testers for a list property or a
    primitive property.

    This class method may be called to apply a property dictionnary on
    an accessor holder. While applyOnAccessorHolder is commonly used
    to apply a property on an *existing* ZODB Property Sheet, this
    method can be used to apply accessors from a Property not defined
    in a ZODB Property Sheet.

    The property dictionnary must define all the attributes listed in
    the class docstring.

    The TALES Expression in the given property dict are considered to
    have been already evaluated, as performed through
    applyOnAccessorHolder by asDict method.

    @param property_dict: Property to generate getter for
    @type property_dict: dict
    @param accessor_holder: Accessor holder to applied the accessors on
    @type accessor_holder: Products.ERP5Type.dynamic.accessor_holder.AccessorHolderType
    @param portal: Portal object
    @type portal: Products.ERP5.ERP5Site.ERP5Site
    @param do_register: Register the property in the Zope property map
    @type do_register: bool
    """
    # Some attributes are required to generate accessors, if they have
    # not been set properly, then don't generate them at all for this
    # Property
    if property_dict['reference'] is None or \
       property_dict['elementary_type'] is None or \
       property_dict['elementary_type'] not in type_definition:
      raise ValueError("Invalid type or reference")

    # Create range accessors if relevant
    if property_dict['range']:
      for kind in ('min', 'max'):
        cls._applyRangeOnAccessorHolder(property_dict.copy(),
                                        accessor_holder, kind, portal)

    # Create translation accessors if relevant
    if property_dict['translatable']:
      translated_property_dict = property_dict.copy()

      if translated_property_dict['property_default'] is None:
        translated_property_dict['property_default'] = ''

      # Make accessors such as getTranslatedProperty
      translated_reference = 'translated_' + property_dict['reference']

      argument_list = (translated_property_dict['reference'],
                       translated_property_dict['elementary_type'],
                       None,
                       translated_property_dict['property_default'])

      cls._applyDefinitionFormatDictOnAccessorHolder(
        translated_reference, cls._translated_getter_definition_dict,
        accessor_holder, argument_list,
        translated_property_dict['read_permission'])

      cls._applyTranslationLanguageOnAccessorHolder(translated_property_dict,
                                                    accessor_holder, portal)

      # make accessor to translation_domain
      # first create default one as a normal property
      translation_domain_reference = translated_property_dict['reference'] + \
                                     '_translation_domain'

      translation_domain_property_dict = {
        'reference': translation_domain_reference,
        'elementary_type': 'string',
        'property_default': '',
        'multivalued': False,
        'storage_id': None,
        'range': False,
        'translatable': False,
        'read_permission': translated_property_dict['read_permission'],
        'write_permission': translated_property_dict['write_permission']}

      # This will always be a StandardProperty, so avoid calling
      # super() here
      StandardProperty.applyDefinitionOnAccessorHolder(
        translation_domain_property_dict, accessor_holder, portal,
        do_register=False)

      # Then override getPropertyTranslationDomain accessor
      accessor = Translation.PropertyTranslationDomainGetter(
        'get' + UpperCase(translation_domain_reference),
        translation_domain_reference, 'string',
        property_dict['translation_domain'])

      accessor_holder.registerAccessor(
        accessor, translated_property_dict['read_permission'])

    # After applying specific getters, setters and testers, apply
    # common getters, setters and testers
    cls._applyGetterDefinitionDictOnAccessorHolder(property_dict,
                                                   accessor_holder)

    cls._applySetterDefinitionDictOnAccessorHolder(property_dict,
                                                   accessor_holder)

    cls._applyTesterDefinitionDictOnAccessorHolder(property_dict,
                                                   accessor_holder)

    # By default, register the property as a Zope property map, by
    # adding it to _properties, which will be later used by
    # PropertyManager
    if do_register:
      property_map = cls._asPropertyMap(property_dict)
      if property_map:
        accessor_holder._properties.append(property_map)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'asDict')
  def asDict(self, expression_context=None):
    """
    Convert the current property to a dict, which is then applied on
    the accessor holder.

    @param expression_context: Expression context for TALES Expression
    @type expression_context: Products.PageTemplates.Expressions.ZopeContext
    @return: The current property as a dict
    @rtype: dict
    """
    # If no expression context has been given, create one, meaningful
    # when being called from the browser for example
    if expression_context is None:
      expression_context = createExpressionContext(self.getPortalObject())

    property_default = evaluateExpressionFromString(expression_context,
                                                    self.getPropertyDefault())

    return {'reference': self.getReference(),
            'description': self.getDescription(),
            'elementary_type': self.getElementaryType(),
            'storage_id': self.getStorageId(),
            'multivalued': self.getMultivalued(),
            'property_default': property_default,
            'range': self.getRange(),
            'preference': self.getPreference(),
            'read_permission': self.getReadPermission(),
            'write_permission': self.getWritePermission(),
            'translatable': self.getTranslatable(),
            'translation_domain': self.getTranslationDomain(),
            'select_variable': self.getSelectVariable()}

  security.declareProtected(Permissions.ModifyPortalContent,
                            'applyOnAccessorHolder')
  def applyOnAccessorHolder(self,
                            accessor_holder,
                            expression_context,
                            portal):
    """
    Apply the ZODB Property to the given accessor holder

    @param accessor_holder: Accessor holder to applied the accessors on
    @type accessor_holder: Products.ERP5Type.dynamic.accessor_holder.AccessorHolderType
    @param expression_context: Expression context for TALES Expression
    @type expression_context: Products.PageTemplates.Expressions.ZopeContext
    @param portal: Portal object
    @type portal: Products.ERP5.ERP5Site.ERP5Site

    @see applyDefinitionOnAccessorHolder
    """
    self.applyDefinitionOnAccessorHolder(self.asDict(expression_context),
                                         accessor_holder,
                                         portal)

  @classmethod
  def _convertFromFilesystemPropertyDict(cls, filesystem_property_dict):
    """
    Convert a property dict coming from a Property Sheet on the
    filesystem to a ZODB property dict.

    This method is just kept for backward-compatibility with
    filesystem Property Sheets used before ZODB Property Sheets.

    @param filesystem_property_dict: Filesystem property definition
    @type filesystem_property_dict: dict
    @return: ZODB property definition
    @rtype: dict
    """
    # Prepare a dictionnary of the ZODB property
    zodb_property_dict = {}

    for fs_property_name, value in six.iteritems(filesystem_property_dict):
      # Convert filesystem property name to ZODB if necessary
      zodb_property_name = \
          fs_property_name in cls._name_mapping_filesystem_to_zodb_dict and \
          cls._name_mapping_filesystem_to_zodb_dict[fs_property_name] or \
          fs_property_name

      # Convert existing TALES expression class or primitive type to a
      # TALES expression string
      if zodb_property_name in cls._expression_attribute_tuple:
        value = isinstance(value, Expression) and \
            value.text or 'python: ' + repr(value)

      # set correctly the id by following naming conventions
      if zodb_property_name == 'id':
        value += cls.getIdAsReferenceAffix()

      zodb_property_dict[zodb_property_name] = value

    return zodb_property_dict

  security.declareProtected(Permissions.ModifyPortalContent,
                            'importFromFilesystemDefinition')
  @classmethod
  def importFromFilesystemDefinition(cls, context, filesystem_property_dict):
    """
    Create a new property on the given context from the given
    filesystem definition dict.

    This method is just kept for backward-compatibility with
    filesystem Property Sheets used before ZODB Property Sheets.

    @param context: Context to create the property in
    @type context: Products.ERP5Type.Core.PropertySheet
    @param filesystem_property_dict: Filesystem definition
    @param filesystem_property_dict: dict
    @return: The new Standard Property
    @rtype: StandardProperty
    """
    return context.newContent(
      portal_type=cls.portal_type,
      **cls._convertFromFilesystemPropertyDict(filesystem_property_dict))
