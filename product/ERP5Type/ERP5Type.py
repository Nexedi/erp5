##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002-2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

import Products.CMFCore.TypesTool
from Products.CMFCore.TypesTool import TypeInformation, ScriptableTypeInformation, FactoryTypeInformation, TypesTool
from Products.CMFCore.interfaces.portal_types import ContentTypeInformation as ITypeInformation

from Products.ERP5Type import _dtmldir
from Products.ERP5Type import Permissions as ERP5Permissions

from zLOG import LOG

class ERP5TypeInformation( FactoryTypeInformation ):
    """
    ERP5 Types are based on FactoryTypeInformation

    The most important feature of ERP5Types is programmable acquisition which
    allows defining attributes which are acquired through categories.

    Another feature is to define the way attributes are stored (localy,
    database, etc.). This allows combining multiple attribute sources
    in a single object. This feature will be in reality implemented
    through PropertySheet classes (TALES expressions)
    """

    __implements__ = ITypeInformation

    meta_type = 'ERP5 Type Information'
    security = ClassSecurityInfo()

    _properties = (TypeInformation._basic_properties + (
        {'id':'factory', 'type': 'string', 'mode':'w',
         'label':'Product factory method'},
        {'id':'init_script', 'type': 'string', 'mode':'w',
         'label':'Init Script'},
        {'id':'redirect_script'
         , 'type': 'string'
         , 'mode':'w'
         , 'label':'Redirect Script'
         },
        {'id':'filter_content_types', 'type': 'boolean', 'mode':'w',
         'label':'Filter content types?'},
        {'id':'allowed_content_types'
         , 'type': 'multiple selection'
         , 'mode':'w'
         , 'label':'Allowed content types'
         , 'select_variable':'listContentTypes'
         },
        {'id':'property_sheet_list'
         , 'type': 'multiple selection'
         , 'mode':'w'
         , 'label':'Property Sheets'
         , 'select_variable':'getPropertySheetList'
         },
        {'id':'base_category_list'
         , 'type': 'multiple selection'
         , 'mode':'w'
         , 'label':'Base Categories'
         , 'select_variable':'getBaseCategoryList'
         },
        ))

    property_sheet_list = ()
    base_category_list = ()
    init_script = ''
    redirect_script = ''
    product = 'ERP5Type'
    immediate_view = 'view'

    #
    #   Acquisition editing interface
    #

    _actions_form = DTMLFile( 'editToolsActions', _dtmldir )


    #
    #   Agent methods
    #
    security.declarePublic('constructInstance')
    def constructInstance( self, container, id, *args, **kw ):
        """
        Build a "bare" instance of the appropriate type in
        'container', using 'id' as its id.  Return the object.
        """
        ob = FactoryTypeInformation.constructInstance(self, container, id, *args, **kw)
        if self.init_script:
          # Acquire the init script in the context of this object
          init_script = getattr(ob, self.init_script)
          init_script(*args, **kw)

        return ob

    security.declareProtected(ERP5Permissions.AccessContentsInformation, 'getPropertySheetList')
    def getPropertySheetList( self ):
        """
            Return list of content types.
        """
        from Products.ERP5Type import PropertySheet
        result = PropertySheet.__dict__.keys()
        result = filter(lambda k: not k.startswith('__'),  result)
        result.sort()
        return result

    security.declareProtected(ERP5Permissions.AccessContentsInformation, 'getBaseCategoryList')
    def getBaseCategoryList( self ):
        result = self.portal_categories.getBaseCategoryList()
        result.sort()
        return result

    security.declareProtected(ERP5Permissions.AccessContentsInformation, 'getConstraintList')
    def getConstraintList( self ):
        from Products.ERP5Type import Constraint
        result = Constraint.__dict__.keys()
        result = filter(lambda k: k != 'Constraint' and not k.startswith('__'),  result)
        result.sort()
        return result
        
    security.declareProtected(ERP5Permissions.AccessContentsInformation, 'getRedirectScript')
    def getRedirectScript( self ):
         """
         return the redirect script
         """
         if self.redirect_script == '':
           return None
         return self.redirect_script

    def manage_editProperties(self, REQUEST):
      """
        Method overload 
        
        Reset _aq_dynamic if property_sheet definition has changed)
        
        XXX This is only good in single thread mode.
            In ZEO environment, we should call portal_activities
            in order to implement a broadcast update
            on production hosts
      """
      previous_property_sheet_list = self.property_sheet_list
      base_category_list = self.base_category_list
      result = FactoryTypeInformation.manage_editProperties(self, REQUEST)
      if previous_property_sheet_list != self.property_sheet_list or \
                   base_category_list != self.base_category_list:
        from Products.ERP5Type.Base import _aq_reset
        _aq_reset() # XXX We should also call it whenever we change workflow defitino
      return result                 

InitializeClass( ERP5TypeInformation )

typeClasses = [
    {'class':FactoryTypeInformation,
     'name':FactoryTypeInformation.meta_type,
     'action':'manage_addFactoryTIForm',
     'permission':'Manage portal'},
    {'class':ScriptableTypeInformation,
     'name':ScriptableTypeInformation.meta_type,
     'action':'manage_addScriptableTIForm',
     'permission':'Manage portal'},
    {'class':ERP5TypeInformation,
     'name':ERP5TypeInformation.meta_type,
     'action':'manage_addERP5TIForm',
     'permission':'Manage portal'},
    ]

class ERP5TypesTool(TypesTool):
    """
      Only used to patch standard TypesTool
    """
    meta_type = 'ERP5 Type Information'

    security = ClassSecurityInfo()

    security.declareProtected(ERP5Permissions.ManagePortal, 'manage_addERP5TIForm')
    def manage_addERP5TIForm(self, REQUEST):
        ' '
        return self._addTIForm(
            self, REQUEST,
            add_meta_type=ERP5TypeInformation.meta_type,
            types=self.listDefaultTypeInformation())


# Dynamic patch
Products.CMFCore.TypesTool.typeClasses = typeClasses
Products.CMFCore.TypesTool.TypesTool.manage_addERP5TIForm = ERP5TypesTool.manage_addERP5TIForm

