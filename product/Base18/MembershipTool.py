##############################################################################
#
# Base18: a Zope product which provides multilingual services for CMF Default
#         documents.
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
#
# This program as such is not intended to be used by end users. End
# users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the Zope Public License (ZPL) Version 2.0
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################
__version__ = "$Revision$"[11:-2]
__doc__ = "This product provides the basic behaviour to CMF object which need\
 translation"


"""\
Base18 portal_membership tool.
"""

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFDefault.MembershipTool import MembershipTool
import Document

default_member_content = '''Default page for %s

  This is the default document created for you when 
  you joined this community.

  To change the content just select "Edit"
  in the Tool Box on the left.
'''

class MembershipTool18( MembershipTool ):

    meta_type       = 'Base18 Membership Tool'

    security = ClassSecurityInfo()

    security.declareProtected(ManagePortal, 'createMemberarea')
    def createMemberarea(self, member_id):
        """
        create a member area
        """
        parent = self.aq_inner.aq_parent
        members =  getattr(parent, 'Members', None)

        if members is not None and not hasattr(members, member_id):
            f_title = "%s's Home" % member_id
            members.manage_addPortalFolder( id=member_id, title=f_title )
            #members.invokeFactory(type_name="Folder", id=member_id)
            f=getattr(members, member_id)
            #f.setTitle(f_title)

            # Grant ownership to Member
            acl_users = self.__getPUS()
            user = acl_users.getUser(member_id).__of__(acl_users)
            f.changeOwnership(user)
            f.manage_setLocalRoles(member_id, ['Owner'])

            # Create Member's home page.
            # default_member_content ought to be configurable per
            # instance of MembershipTool.
            #f.invokeFactory(type_name="Document", id='index_html')

    def __getPUS(self):
        # Gets something we can call getUsers() and getUserNames() on.
        acl_users = self.acl_users
        if hasattr(acl_users, 'getUsers'):
            return acl_users
        else:
            # This hack works around the absence of getUsers() in LoginManager.
            # Gets the PersistentUserSource object that stores our users
            for us in acl_users.UserSourcesGroup.objectValues():
                if us.meta_type == 'Persistent User Source':
                    return us.__of__(acl_users)
            

InitializeClass( MembershipTool18 )
