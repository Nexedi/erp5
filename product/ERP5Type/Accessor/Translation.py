##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Aurelien Calonne <aurel@nexedi.com>
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

from zLOG import LOG, WARNING
from Products.ERP5Type.PsycoWrapper import psyco
from Acquisition import aq_base

from Products.ERP5Type.Accessor.Base import func_code, ATTRIBUTE_PREFIX, evaluateTales, Getter as BaseGetter, Method
from Products.ERP5Type.Accessor import Accessor, AcquiredProperty
from Products.ERP5Type.Accessor.TypeDefinition import type_definition


TRANSLATION_DOMAIN_CONTENT_TRANSLATION = 'content_translation'


class TranslatedPropertyGetter(BaseGetter):
  """
  Get the translated property
  """
  # This can be called from the Web
  func_code = func_code()
  func_code.co_varnames = ('self',)
  func_code.co_argcount = 1
  func_defaults = ()

  def __init__(self, id, key, property_id, property_type, language, default=None, warning=0):
    self._id = id
    self.__name__ = id
    self._property_id = property_id
    self._null = type_definition[property_type]['null']
    self._language = language
    self._default = default
    self._warning = warning

  def __call__(self, instance, *args, **kw):
    if self._warning:
      LOG("ERP5Type Deprecated Getter Id:",0, self._id)
    domain = instance.getProperty('%s_translation_domain' % self._property_id)
    if domain==TRANSLATION_DOMAIN_CONTENT_TRANSLATION:
      if len(args) > 0:
        default = args[0]
      else:
        default = instance.getProperty(self._property_id)
      if kw.get('no_original_value'):
        default = self._default

      if self._language is None:
        language = kw.get('language') or instance.getPortalObject().Localizer.get_selected_language()
      else:
        language = self._language
      try:
        return instance.getPropertyTranslation(self._property_id, language)
      except KeyError:
        return default
    else:
      value = instance.getProperty(self._property_id)
      if domain == '' or (value in ('', None)):
        return value
      localizer = instance.getPortalObject().Localizer
      if domain is not None:
        message_catalog = getattr(localizer, domain, None)
      else: message_catalog = None
      if message_catalog is not None:
        return message_catalog.gettext(unicode(value, 'utf8'), lang=self._language).encode('utf8')
      else:
        return value

  psyco.bind(__call__)


class PropertyTranslationDomainGetter(BaseGetter):
  """
  Get the translation domain
  """
  _need__name__=1

  # This can be called from the Web
  func_code = func_code()
  func_code.co_varnames = ('self', )
  func_code.co_argcount = 1
  func_defaults = ()

  def __init__(self, id, key, property_type, default=None, storage_id=None):
    self._id = id
    self.__name__ = id
    self._original_key = key.replace('_translation_domain', '')
    self._default = default
    if storage_id is None:
      storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
    self._storage_id = storage_id
    self._is_tales_type = (property_type == 'tales')

  def __call__(self, instance, *args, **kw):
    if len(args) > 0:
      default = args[0]
    else:
      default = self._default
    # No acquisition on properties
    value = getattr(aq_base(instance), self._storage_id, None)
    if value is None:
      # second try to get it from portal type
      ptype_domain = None
      ptype = instance.getPortalType()
      ptypes_tool = instance.getPortalObject()['portal_types']
      typeinfo = ptypes_tool.getTypeInfo(ptype)
      if typeinfo is None:
        ptype_domain = ''
      else:
        domain_dict = typeinfo.getPropertyTranslationDomainDict()
        domain = domain_dict.get(self._original_key)
        if domain is None:
          ptype_domain = ''
        else:
          ptype_domain = domain.getDomainName()
      if ptype_domain is '' and default is not None:
        # then get the default property defined on property sheet
        value = default
      else:
        value = ptype_domain
    if value is None:
      value = ''
    if self._is_tales_type and kw.get('evaluate', 1):
      return evaluateTales(instance, value)
    else:
      return value

  psyco.bind(__call__)


class TranslationPropertySetter(Accessor.Accessor):
  """
  Set a translation into language-property pair dict.
  """
  _need__name__=1

  # Generic Definition of Method Object
  # This is required to call the method form the Web
  # More information at http://www.zope.org/Members/htrd/howto/FunctionTemplate
  func_code = func_code()
  func_code.co_varnames = ('self', 'value')
  func_code.co_argcount = 2
  func_defaults = ()

  def __init__(self, id, key, property_id, property_type, language):
    self._id = id
    self.__name__ = id
    self._property_id = property_id
    self._language = language
    self._cast = type_definition[property_type]['cast']
    self._null = type_definition[property_type]['null']

  def __call__(self, instance, *args, **kw):
    value = args[0]
    modified_object_list = []

    domain = instance.getProperty('%s_translation_domain' % self._property_id)
    if domain==TRANSLATION_DOMAIN_CONTENT_TRANSLATION:
      if value in self._null:
        instance.deletePropertyTranslation(self._property_id, self._language)
      else:
        original_property_value = instance.getProperty(self._property_id)
        instance.setPropertyTranslation(self._property_id, self._language, original_property_value, self._cast(args[0]))
        modified_object_list.append(instance)
    else:
      pass
      #raise RuntimeError, 'The property %s.%s is not writable.' % (instance.portal_type, self._property_id)
    return modified_object_list


class AcquiredPropertyGetter(AcquiredProperty.Getter):

    def __call__(self, instance, *args, **kw):
      if len(args) > 0:
        default = args[0]
      else:
        default = None
      value = instance._getDefaultAcquiredProperty(self._key, None, self._null,
            base_category=self._acquisition_base_category,
            portal_type=self._acquisition_portal_type,
            accessor_id=self._acquisition_accessor_id,
            copy_value=self._acquisition_copy_value,
            mask_value=self._acquisition_mask_value,
            storage_id=self._storage_id,
            alt_accessor_id=self._alt_accessor_id,
            acquisition_object_id=self._acquisition_object_id,
            is_list_type=self._is_list_type,
            is_tales_type=self._is_tales_type,
            checked_permission=kw.get('checked_permission', None)
            )
      if value is not None:
        return value.getProperty(self._acquired_property, default, **kw)
      else:
        return default

class TranslatedPropertyTester(Method):
  """
    Tests if an attribute value exists
  """
  _need__name__=1

  # This is required to call the method form the Web
  func_code = func_code()
  func_code.co_varnames = ('self',)
  func_code.co_argcount = 1
  func_defaults = ()

  def __init__(self, id, key, property_id, property_type, language, warning=0):
    self._id = id
    self.__name__ = id
    self._property_id = property_id
    self._property_type = property_type
    self._null = type_definition[property_type]['null']
    self._language = language
    self._warning = warning

  def __call__(self, instance, *args, **kw):
    if self._warning:
      LOG("ERP5Type Deprecated Tester Id:",0, self._id)
    domain = instance.getProperty('%s_translation_domain' % self._property_id)

    if domain==TRANSLATION_DOMAIN_CONTENT_TRANSLATION:
      if self._language is None:
        language = kw.get('language') or instance.getPortalObject().Localizer.get_selected_language()
      else:
        language = self._language
      try:
        return instance.getPropertyTranslation(self._property_id, language) is not None
      except KeyError:
        return False
    else:
      return instance.getProperty(self._property_id) is not None
