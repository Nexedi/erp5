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
from Products.CMFCore.TypesTool import ScriptableTypeInformation, FactoryTypeInformation, TypesTool
from Products.CMFCore.interfaces.portal_types import ContentTypeInformation as ITypeInformation

from Products.ERP5Type import _dtmldir
from Products.ERP5Type import Permissions as ERP5Permissions

class ERP5TypeInformation( FactoryTypeInformation, ScriptableTypeInformation ):
    """
    ERP5 Types are based on Scriptable Type (this will eventually require some rewriting
    of Utils... and addXXX methods)

    The most important feature of ERP5Types is programmable acquisition which
    allows to define attributes which are acquired through categories.

    Another feature is to define the way attributes are stored (localy,
    database, etc.). This allows to combine multiple attribute sources
    in a single object. This feature will be in reality implemented
    through PropertySheet classes (TALES expressions)
    """

    __implements__ = ITypeInformation

    meta_type = 'ERP5 Type Information'
    security = ClassSecurityInfo()
   
    _properties = (ScriptableTypeInformation._basic_properties + (
        {'id':'factory', 'type': 'string', 'mode':'w',
         'label':'Product factory method'},
        {'id':'init_script', 'type': 'string', 'mode':'w',
         'label':'Init Script'},
        {'id':'permission', 'type': 'string', 'mode':'w',
         'label':'Constructor permission'},
        ) + ScriptableTypeInformation._advanced_properties  + (
        {  'id':'property_sheet_list'
         , 'type': 'multiple selection'
         , 'mode':'w'
         , 'label':'Property Sheets'
         , 'select_variable':'getPropertySheetList'
         },
        {  'id':'base_category_list'
         , 'type': 'multiple selection'
         , 'mode':'w'
         , 'label':'Bae Categories'
         , 'select_variable':'getBaseCategoryList'
         },
        )) # Remove initial view name ? what is the use of meta_type ? Implicitly addable ? Allow Discusion ?

    manage_options = ScriptableTypeInformation.manage_options

    property_sheet_list = ()
    base_category_list = ()
    init_script = ''
    product = 'ERP5Type'
    
        
    #
    #   Acquisition editing interface
    #

    _actions_form = DTMLFile( 'editActions', _dtmldir )


    #
    #   Agent methods
    #
    security.declarePublic('constructInstance')
    def constructInstance( self, container, id, *args, **kw ):
        """
        Build a "bare" instance of the appropriate type in
        'container', using 'id' as its id.  Return the object.
        """
        # Check extra permissions
        if self.permission:
            if not ScriptableTypeInformation.isConstructionAllowed(self, container):
                raise Unauthorized
        
        # Get the factory method, performing a security check
        # in the process.                              
        try:
          if self.constructor_path != self.factory: self.factory = self.constructor_path
          m = self._getFactoryMethod(container)
        except ValueError:
          m = None          

        if m is not None:          
          # Standard FTI constructor
                    
          id = str(id)
  
          if getattr( m, 'isDocTemp', 0 ):
              args = ( m.aq_parent, self.REQUEST ) + args
              kw[ 'id' ] = id
          else:
              args = ( id, ) + args
  
          id = apply( m, args, kw ) or id  # allow factory to munge ID
          ob = container._getOb( id )

        else:
          # Scriptable type          
          constructor = self.restrictedTraverse( self.constructor_path )
          # make sure ownership is explicit before switching the context
          if not hasattr( aq_base(constructor), '_owner' ):
              constructor._owner = aq_get(constructor, '_owner')
  
          #   Rewrap to get into container's context.
          constructor = aq_base(constructor).__of__( container )
  
          id = str(id)
          ob = apply(constructor, (container, id) + args, kw)
          
        return self._finishConstruction(ob)                                                     

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

