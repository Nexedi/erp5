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

from Globals import DTMLFile, InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.Expression import Expression
from Products.ERP5Type import _dtmldir

from Permissions import ManagePortal
from OFS.SimpleItem import SimpleItem
from Products.ERP5Type import PropertySheet
from Acquisition import aq_base

import Products

from zLOG import LOG

_MARKER = {}

class TranslationProviderBase:
  """
  Provide Translation Tabs and management methods for PropertyTranslationDomain
  """

  security = ClassSecurityInfo()
  

  _translation_form = DTMLFile( 'editToolsTranslation', _dtmldir )

  manage_options = ( { 'label' : 'Translation'
                       , 'action' : 'manage_editTranslationForm'
                       }
                     ,
                     )

  security.declarePrivate( 'updateInitialPropertyTranslationDomainDict' )
  def updateInitialPropertyTranslationDomainDict(self, ):
    """
    Create the initial list of association between property and domain name
    """
    property_domain_dict = {}
    ptype_object = self
    # get the klass of the object based on the constructor document
    m = Products.ERP5Type._m
    ptype_name = ''.join(ptype_object.id.split(' '))
    constructor = self.factory # This is safer than: 'add%s' %(ptype_name)
    klass = None
    for method, doc in m.items():
      if method == constructor:
        klass = doc.klass
        break
    # get the property sheet list for the portal type
    # from the list of property sheet defined on the portal type
    ps_list = map(lambda p: getattr(PropertySheet, p, None),
                  ptype_object.property_sheet_list)
    ps_list = filter(lambda p: p is not None, ps_list)
    # from the property sheets defined on the class
    if klass is not None:
      from Products.ERP5Type.Base import getClassPropertyList
      ps_list = tuple(ps_list) + getClassPropertyList(klass)
    # get all properties from the property sheet list
    current_list = []
    for base in ps_list:
      if hasattr(base, '_properties'):
        # XXX must check that property is translatable
        ps_property = getattr(base, '_properties')
        if type(ps_property) in (type(()), type([])):
          current_list += ps_property
    # create TranslationInformation object for each property
    for prop in current_list:
      if prop.get('translatable', 0):
        prop_id = prop['id']
        if not property_domain_dict.has_key(prop_id):
          domain_name = prop.get('translation_domain', None)
          property_domain_dict[prop_id] = TranslationInformation(prop_id, domain_name)

    original_property_domain_dict = getattr(aq_base(self),
                                            '_property_domain_dict', _MARKER)
    original_property_domain_keys = original_property_domain_dict.keys()
    property_domain_keys = property_domain_dict.keys()
    property_domain_keys.sort()
    original_property_domain_keys.sort()

    # Only update if required in order to prevent ZODB from growing
    if original_property_domain_dict is _MARKER or\
          property_domain_keys != original_property_domain_keys:
      # Update existing dict
      property_domain_dict.update(original_property_domain_dict)
      # And store
      self._property_domain_dict = property_domain_dict

        
  security.declarePrivate( 'getPropertyTranslationDomainDict' )
  def getPropertyTranslationDomainDict(self,):
    """
    Return all the translation defined by a provider.
    """
    property_domain_dict = getattr(aq_base(self),
                                   '_property_domain_dict', _MARKER)
    # initialize if needed
    if property_domain_dict is _MARKER:
      self.updateInitialPropertyTranslationDomainDict()
      return self._property_domain_dict
    return property_domain_dict

  #
  #   ZMI methods
  #
  security.declareProtected( ManagePortal, 'manage_editTranslationForm' )
  def manage_editTranslationForm( self, REQUEST, manage_tabs_message=None ):
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

    # get list of Localizer catalog, add 'empty' one for no traduction
    catalog = self.getPortalObject().Localizer.objectIds() + ['']
    
    return self._translation_form( self
                                   , REQUEST
                                   , translations = translation_list
                                   , possible_domain_names=catalog
                                   , management_view='Translation'
                                   , manage_tabs_message=manage_tabs_message
                                   )
  

  security.declareProtected( ManagePortal, 'changeTranslations' )
  def changeTranslations( self, properties=None, REQUEST=None ):
    """
    Update our list of translations domain name
    """
    if properties is None:
      properties = REQUEST
    
    for prop_name in self._property_domain_dict.keys():
      new_domain_name = properties.get(prop_name)
      prop_object = self._property_domain_dict[prop_name]
      if new_domain_name != prop_object.getDomainName():
        prop_object.setDomainName(new_domain_name)

    from Products.ERP5Type.Base import _aq_reset
    _aq_reset() # Reset accessor cache

    if REQUEST is not None:
      return self.manage_editTranslationForm(REQUEST, manage_tabs_message=
                                       'Translations Updated.')


InitializeClass(TranslationProviderBase)


class TranslationInformation (SimpleItem):
  """
  This class represent the association between a property of a portal type and
  the domain name used to translate this property
  """

  security = ClassSecurityInfo()

  security.declarePrivate( '__init__')
  def __init__(self, property_name='', domain_name=None):
    """
    Set up an instance
    """
    self.property_name = property_name
    self.domain_name = domain_name

  security.declarePrivate('getPropertyName')
  def getPropertyName(self):
    """
    Return the property name
    """
    return self.property_name

  security.declarePrivate('getDomainName')
  def getDomainName(self):
    """
    Return the domain name
    """
    return self.domain_name

  security.declarePrivate('setDomainName')
  def setDomainName(self, domain_name='erp5_ui'):
    """
    Set the domain name value
    """
    self.domain_name = domain_name
  
    
InitializeClass(TranslationInformation)
