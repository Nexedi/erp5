##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass, DTMLFile
from Acquisition import aq_base

from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.Utils import convertToUpperCase
from Products.ERP5Type.Accessor.TypeDefinition import list_types
from Products.ERP5Form.Document.Preference import Preference
from Products.ERP5Form import _dtmldir

class PreferenceTool(BaseTool):
  """ PreferenceTool manages User Preferences / User profiles. """
  id            = 'portal_preferences'
  meta_type     = 'ERP5 Preference Tool'
  portal_type   = 'Preference Tool'
  title         = 'Preferences'
  allowed_types = ( 'ERP5 Preference',)
  security      = ClassSecurityInfo()

  security.declareProtected(
       Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainPreferenceTool', _dtmldir )
  
  security.declareProtected(
       Permissions.ManagePortal, 'manage_group_preferences' )
  manage_group_preferences = DTMLFile(
       'PreferenceTool_managePreferences', _dtmldir )
  
  manage_options = ( BaseTool.manage_options +
                     ( { 'label'      : 'User Groups Preferences'
                       , 'action'     : 'manage_group_preferences'},))
  
  security.declarePrivate('manage_afterAdd')
  def manage_afterAdd(self, item, container) :
    """ init the permissions right after creation """
    item.manage_permission(Permissions.AddPortalContent,
          ['Member', 'Author', 'Manager'])
    item.manage_permission(Permissions.View,
          ['Member', 'Auditor', 'Manager'])
    BaseTool.inheritedAttribute('manage_afterAdd')(self, item, container)
  
  def _aq_dynamic(self, name):
    """ if the name is a valid preference, then start a lookup on
      active preferences. """
    dynamic = BaseTool._aq_dynamic(self, name)
    if dynamic is not None :
      return dynamic
    aq_base_name = getattr(aq_base(self), name, None)
    if aq_base_name is not None :
      return aq_base_name
    if name in self.getValidPreferenceNames() :
      return self.getPreference(name)
  
  security.declareProtected(Permissions.View, "getPreference")
  def getPreference(self, pref_name) :
    """ get the preference on the most appopriate Preference object. """
    def _getPreference(pref_name="", user_name="") :
      found = 0
      MARKER = []
      for pref in self._getMostAppropriatePreferences() :
        attr = getattr(pref, pref_name, MARKER)
        if attr is not MARKER :
          found = 1
          # test the attr is set
          if callable(attr) :
            value = attr()
          else :
            value = attr
          if value not in (None, '', (), []) :
            return attr
      if found :
        return attr
    _getPreference = CachingMethod( _getPreference,
                                  id='PreferenceTool.CachingMethod')
    user_name = getSecurityManager().getUser().getId()
    return _getPreference(pref_name=pref_name, user_name=user_name)
  
  security.declareProtected(Permissions.ModifyPortalContent, "setPreference")
  def setPreference(self, pref_name, value) :
    """ set the preference on the active Preference object"""
    self.getActivePreference()._edit(**{pref_name:value})
    
  security.declareProtected(Permissions.View, "getValidPreferenceNames")
  def getValidPreferenceNames(self) :
    """ return the list of attributes that are preferences names and
       should be looked up on Preferences. """
    def _getValidPreferenceNames(self) :
      """ a cache for this method """
      attr_list = []
      try :
        pref_portal_type = getToolByName(self, 'portal_types')['Preference']
      except KeyError :
        # When creating an ERP5 Site, this method is called, but the 
        # type is not installed yet
        return []
      # 'Dynamic' property sheets added through ZMI
      zmi_property_sheet_list = tuple(map(lambda property_sheet:
                        getattr(__import__(property_sheet), property_sheet),
                        pref_portal_type.property_sheet_list))
      # 'Static' property sheets defined on the class
      class_property_sheet_list = Preference.property_sheets
      for property_sheet in ( zmi_property_sheet_list +
                              class_property_sheet_list ) :
        # then generate common method names 
        for prop in property_sheet._properties :
          if not prop.get('preference', 0) :
            # only properties marked as preference are used
            continue
          attribute = prop['id']
          attr_list += [ attribute,
                         'get%s' % convertToUpperCase(attribute),
                         'get%sId' % convertToUpperCase(attribute),
                         'get%sTitle' % convertToUpperCase(attribute), ]
          if prop['type'] in list_types :
            attr_list +=  ['get%sList' % convertToUpperCase(attribute), ]
        for attribute in list(getattr(property_sheet, '_categories', [])) :
          attr_list += [ attribute,
                         'get%s' % convertToUpperCase(attribute),
                         'get%sId' % convertToUpperCase(attribute),
                         'get%sTitle' % convertToUpperCase(attribute),
                         'get%sValue' % convertToUpperCase(attribute),
                         'get%sValueList' % convertToUpperCase(attribute),
                         'get%sItemList' % convertToUpperCase(attribute),
                         'get%sIdList' % convertToUpperCase(attribute),
                         'get%sTitleList' % convertToUpperCase(attribute),
                         'get%sList' % convertToUpperCase(attribute), ]
      return attr_list
    _getValidPreferenceNames = CachingMethod(
                      _getValidPreferenceNames, cache_duration = 600,
                      id = 'PreferenceTool._getPreferenceAttributes')
    return _getValidPreferenceNames(self)

  security.declarePrivate('_getMostAppropriatePreferences')
  def _getMostAppropriatePreferences(self) :
    """ return the most appropriate preferences objects,
      sorted so that the first in the list should be applied first """
    prefs = []
    for pref in self.contentValues(spec=('ERP5 Preference', )) :
      pref = pref.getObject()
      if pref.getPreferenceState() == 'enabled' :
        prefs.append(pref)
    prefs.sort(lambda b, a: cmp(a.getPriority(), b.getPriority()))
    return prefs
    
  security.declareProtected(Permissions.View, 'getActivePreference')
  def getActivePreference(self) :
    """ returns the current preference for the user. 
       Note that this preference may be read only. """
    enabled_prefs = self._getMostAppropriatePreferences()
    if len(enabled_prefs) > 0 :
      return enabled_prefs[0]

  security.declareProtected(Permissions.View, 'getDocumentTemplatesForFolder')
  def getDocumentTemplatesForFolder(self, folder) :
    """ returns all document templates that are in acceptable Preferences 
      for the folder """
    acceptable_templates = []
    for pref in self._getMostAppropriatePreferences() :
      for doc in pref.objectValues() :
        if hasattr(doc, 'getTemplateDestinationUidList') and \
           folder.getUid() in doc.getTemplateDestinationUidList() :
          acceptable_templates.append (doc)
    return acceptable_templates

  security.declareProtected(Permissions.ManagePortal,
          'manage_updateUserGroupsPreferences')
  def manage_updateUserGroupsPreferences(self, REQUEST) :
    """ action edit Users Groups Preferences from the management sceen """
    for k, v in REQUEST.items() :
      if k.startswith("preference_priority_") :
        self[k[len('preference_priority_'):]].setPriority(v)
    if REQUEST is not None:
      return self.manage_group_preferences( self, REQUEST,
        manage_tabs_message='Preference Priorities Updated')

InitializeClass(PreferenceTool)

