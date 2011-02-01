##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#               2006 Nexedi
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.Expression import Expression
from Products.ERP5Type import _dtmldir
from Products.ERP5Type.Cache import CachingMethod

from Permissions import AccessContentsInformation, ManagePortal, ModifyPortalContent
from OFS.SimpleItem import SimpleItem
from Products.ERP5Type import PropertySheet
from Acquisition import aq_base, Implicit

import Products

from Products.ERP5Type.Accessor import Translation

from zLOG import LOG

_MARKER = {}

class PropertyDomainDict(Implicit):
  """
  Combined with TranslationProviderBase.property_domain_dict,
  this class makes TranslationInformation objects inside
  TranslationProviderBase._property_domain_dict accessible with
  (un)restrictedTraverse. This hack allows forms to use Base_edit
  for such objects.
  """
  def _aq_dynamic(self, attr):
    type_info = self.aq_parent
    try:
      return type_info._property_domain_dict[attr].__of__(type_info)
    except KeyError:
      return None


class TranslationProviderBase(object):
  """
  Provide Translation Tabs and management methods for PropertyTranslationDomain
  """

  security = ClassSecurityInfo()

  security.declarePrivate('updateInitialPropertyTranslationDomainDict')
  def updateInitialPropertyTranslationDomainDict(self):
    """
    Updates the list of association between property and domain name.
    This method must be called anytime new translatable properties are added.
    """
    property_domain_dict = {}

    for prop in self._getPropertyHolder()._properties:
      prop_id = prop['id']
      if prop.get('translatable') and prop_id not in property_domain_dict:
        domain_name = prop.get('translation_domain')
        property_domain_dict[prop_id] = TranslationInformation(prop_id,
                                                               domain_name)

    original_property_domain_dict = getattr(aq_base(self),
                                            '_property_domain_dict', _MARKER)
    # Only update if required in order to prevent ZODB from growing
    if original_property_domain_dict is _MARKER or\
       sorted(property_domain_dict) != sorted(original_property_domain_dict):
      # Update existing dict
      property_domain_dict.update(original_property_domain_dict)
      # And store
      self._property_domain_dict = property_domain_dict

  security.declareProtected(AccessContentsInformation,
                            'getPropertyTranslationDomainDict')
  def getPropertyTranslationDomainDict(self):
    """
    Return all translations defined by a provider.
    """
    # From time to time we'll update property translation domain dict.
    def _updatePropertyTranslationDomainDict():
      self.updateInitialPropertyTranslationDomainDict()
    CachingMethod(_updatePropertyTranslationDomainDict,
      id='%s._updateInitialPropertyTranslationDomainDict' % self.getId(),
      cache_factory='erp5_ui_long')()

    if getattr(self, '_property_domain_dict', None) is None:
      return {}
    else:
      return dict((k, v.__of__(self))
                  for k, v in self._property_domain_dict.iteritems())

  security.declarePublic('getContentTranslationDomainPropertyNameList')
  def getContentTranslationDomainPropertyNameList(self):
    result = []
    for property_name, translation_information in self.getPropertyTranslationDomainDict().items():
      if translation_information.getDomainName()==Translation.TRANSLATION_DOMAIN_CONTENT_TRANSLATION:
        result.append(property_name)
    return result

  #
  #   ZMI methods
  #
  security.declareProtected(ManagePortal, 'manage_editTranslationForm')
  def manage_editTranslationForm(self, REQUEST, manage_tabs_message=None):
    """ Show the 'Translation' management tab.
    """
    translation_list = []
    self.updateInitialPropertyTranslationDomainDict() # Force update in case of change of PS list
    prop_domain_name_dict = self.getPropertyTranslationDomainDict()
    keys = prop_domain_name_dict.keys()
    keys.sort()
    for k in keys:
      prop = prop_domain_name_dict[k]
      t = {}
      t['property_name'] = prop.getPropertyName()
      t['domain_name'] = prop.getDomainName()
      translation_list.append(t)

    # get a list of message catalogs and add empty one for no traduction and
    # add another for content translation.
    translation_domain_list = self.portal_property_sheets.getTranslationDomainNameList()
    return self._translation_form( self
                                   , REQUEST
                                   , translations = translation_list
                                   , possible_domain_names=translation_domain_list
                                   , management_view='Translation'
                                   , manage_tabs_message=manage_tabs_message
                                   )


  security.declareProtected(ManagePortal, 'changeTranslations')
  def changeTranslations(self, properties=None, REQUEST=None):
    """
    Update our list of translations domain name
    """
    if properties is None:
      properties = REQUEST

    # PropertySheet might be changed.
    self.updateInitialPropertyTranslationDomainDict()

    property_domain_dict = self.getPropertyTranslationDomainDict()
    for prop_name in property_domain_dict.keys():
      new_domain_name = properties.get(prop_name)
      prop_object = property_domain_dict[prop_name]
      if new_domain_name != prop_object.getDomainName():
        prop_object.edit(domain_name=new_domain_name)

    # Reset accessor cache
    types_tool = self.getPortalObject().portal_types
    types_tool.resetDynamicDocumentsOnceAtTransactionBoundary()

    if REQUEST is not None:
      return self.manage_editTranslationForm(REQUEST, manage_tabs_message=
                                       'Translations Updated.')

  security.declareProtected(ModifyPortalContent, 'property_domain_dict')
  @property
  def property_domain_dict(self):
    return PropertyDomainDict().__of__(self)


class TranslationInformation(SimpleItem):
  """
  This class represent the association between a property of a portal type and
  the domain name used to translate this property
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(AccessContentsInformation)

  def __init__(self, property_name='', domain_name=None):
    """
    Set up an instance
    """
    self.property_name = property_name
    self.domain_name = domain_name

  security.declareProtected(AccessContentsInformation, 'getPropertyName')
  def getPropertyName(self):
    """
    Return the property name
    """
    return self.property_name

  security.declareProtected(AccessContentsInformation, 'getDomainName')
  def getDomainName(self):
    """
    Return the domain name
    """
    return self.domain_name

  security.declareProtected(ModifyPortalContent, 'edit')
  def edit(self, edit_order=(), **kw):
    self._p_changed = 1
    self.__dict__.update((k, v or None) for k, v in kw.iteritems())

InitializeClass(TranslationInformation)
