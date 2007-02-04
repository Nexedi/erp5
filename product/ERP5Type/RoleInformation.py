##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Information about customizable roles.

$Id$
"""

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Acquisition import aq_inner, aq_parent
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression

from Permissions import View

ERP5TYPE_SECURITY_CATEGORY_GENERATION_SCRIPT = \
                'ERP5Type_getSecurityCategoryFromAssignment'

class RoleInformation( SimpleItem ):

    """ Represent a role definition.

    Roles definitions defines local roles on ERP5Type documents. They are
    applied by the updateLocalRolesOnSecurityGroups method.
    """
    _isRoleInformation = 1
    __allow_access_to_unprotected_subobjects__ = 1

    security = ClassSecurityInfo()

    def __init__( self
                , id
                , title=''
                , description=''
                , category=()
                , condition=''
                , priority=10
                , base_category=()
                , base_category_script=''
                ):
        """ Set up an instance.
        """
        if condition and isinstance(condition, str):
            condition = Expression( condition )

        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.condition = condition
        self.priority = priority
        self.base_category = base_category
        self.base_category_script = base_category_script

    security.declareProtected( View, 'Title' )
    def Title(self):

        """ Return the Role title.
        """
        return self.title or self.getId()

    security.declareProtected( View, 'Description' )
    def Description( self ):

        """ Return a description of the role.
        """
        return self.description

    security.declarePrivate( 'testCondition' )
    def testCondition( self, ec ):

        """ Evaluate condition using context, 'ec', and return 0 or 1.
        """
        if self.condition:
            return self.condition(ec)
        else:
            return 1

    security.declareProtected( View, 'getRole' )
    def getRole( self, ec ):

        """ Compute the role using context, 'ec'; return a mapping of
            info about the role.
        """
        info = {}
        info['id'] = self.id
        info['name'] = self.Title()
        info['description'] = self.Description()
        info['category'] = self.getCategory()
        info['base_category'] = self.getBaseCategory()
        info['base_category_script'] = self.getBaseCategoryScript()
        return info

    security.declareProtected( View, 'getCondition' )
    def getCondition(self):

        """ Return the text of the TALES expression for our condition.
        """
        return getattr( self, 'condition', None ) and self.condition.text or ''

    security.declareProtected( View, 'getCategory' )
    def getCategory( self ):

        """ Return the category
            as a tuple (to prevent script from modifying it)

            Strip any return or ending space
        """
        return tuple(map(lambda x: x.strip(),
                         filter(lambda x: x, self.category))) or ()

    security.declareProtected( View, 'getBaseCategory' )
    def getBaseCategory( self ):

        """ Return the base_category
            as a tuple (to prevent script from modifying it)
        """
        return tuple(getattr(self, 'base_category', ()))

    security.declareProtected( View, 'getBaseCategoryScript' )
    def getBaseCategoryScript( self ):

        """ Return the base_category_script id
        """
        base_category_script = getattr(self, 'base_category_script', '')
        if base_category_script:
          return base_category_script
        return ERP5TYPE_SECURITY_CATEGORY_GENERATION_SCRIPT

    security.declarePrivate( 'clone' )
    def clone( self ):

        """ Return a newly-created RI just like us.
        """
        return self.__class__( id=self.id
                             , title=self.title
                             , description=self.description
                             , category =self.category
                             , condition=self.getCondition()
                             , priority =self.priority
                             , base_category=self.base_category
                             , base_category_script=getattr(self,
                                                   'base_category_script', '')
                             )

InitializeClass( RoleInformation )

class ori:
    #Provided for backwards compatability
    # Provides information that may be needed when constructing the list of
    # available actions.
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__( self, tool, folder, object=None ):
        self.portal = portal = aq_parent(aq_inner(tool))
        membership = getToolByName(tool, 'portal_membership')
        #self.isAnonymous = membership.isAnonymousUser()
        #self.user_id = membership.getAuthenticatedMember().getId()
        self.portal_url = portal.absolute_url()
        if folder is not None:
            self.folder_url = folder.absolute_url()
            self.folder = folder
        else:
            self.folder_url = self.portal_url
            self.folder = portal
        self.content = object
        if object is not None:
            self.content_url = object.absolute_url()
        else:
            self.content_url = None

    def __getitem__(self, name):
        # Mapping interface for easy string formatting.
        if name[:1] == '_':
            raise KeyError, name
        if hasattr(self, name):
            return getattr(self, name)
        raise KeyError, name
