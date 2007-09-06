##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from AccessControl.SecurityInfo import ClassSecurityInfo
from Globals import InitializeClass
from Products.HBTreeFolder2.HBTreeFolder2 import HBTreeFolder2Base

try:
    from Products.CMFCore.PortalFolder import PortalFolderBase as PortalFolder
except ImportError:
    from Products.CMFCore.PortalFolder import PortalFolder

from Products.CMFCore.PortalFolder import factory_type_information as PortalFolder_FTI
from Products.CMFCore.utils import getToolByName

_actions = PortalFolder_FTI[0]['actions']

factory_type_information = ( { 'id'             : 'CMF HBTree Folder',
                               'meta_type'      : 'CMF HBTree Folder',
                               'description'    : """\
CMF folder designed to hold a lot of objects.""",
                               'icon'           : 'folder_icon.gif',
                               'product'        : 'CMFCore',
                               'factory'        : 'manage_addCMFHBTreeFolder',
                               'filter_content_types' : 0,
                               'immediate_view' : 'folder_edit_form',
                               'actions'        : _actions,
                               },
                           )


def manage_addCMFHBTreeFolder(dispatcher, id, title='', REQUEST=None):
    """Adds a new HBTreeFolder object with id *id*.
    """
    id = str(id)
    ob = CMFHBTreeFolder(id)
    ob.title = str(title)
    dispatcher._setObject(id, ob)
    ob = dispatcher._getOb(id)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(ob.absolute_url() + '/manage_main' )


class CMFHBTreeFolder(HBTreeFolder2Base, PortalFolder):
    """HBTree folder for CMF sites.
    """
    meta_type = 'CMF HBTree Folder'
    security = ClassSecurityInfo()

    def __init__(self, id, title=''):
        PortalFolder.__init__(self, id, title)
        HBTreeFolder2Base.__init__(self, id)

    def _checkId(self, id, allow_dup=0):
        PortalFolder._checkId(self, id, allow_dup)
        HBTreeFolder2Base._checkId(self, id, allow_dup)


    def allowedContentTypes(self):
      """
      List type info objects for types which can be added in
      this folder.
      """
      result = []
      portal_types = getToolByName(self, 'portal_types')
      myType = portal_types.getTypeInfo(self)

      if myType is not None:
        allowed_types_to_check = []
        if myType.filter_content_types:
          for portal_type in myType.allowed_content_types:
            contentType = portal_types.getTypeInfo(portal_type)
            if contentType is None:
              raise AttributeError, "Portal type '%s' does not exist " \
                                    "and should not be allowed in '%s'" % \
                                    (portal_type, self.getPortalType())
            result.append(contentType)
        else:
          for contentType in portal_types.listTypeInfo(self):
            if myType.allowType(contentType.getId()):
              result.append(contentType)
      else:
          result = portal_types.listTypeInfo()

      return filter(
          lambda typ, container=self: typ.isConstructionAllowed(container),
          result)


InitializeClass(CMFHBTreeFolder)
