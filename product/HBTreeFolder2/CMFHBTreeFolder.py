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
from App.class_init import default__class_init__ as InitializeClass
from Products.HBTreeFolder2.HBTreeFolder2 import HBTreeFolder2Base

try:
    from Products.CMFCore.PortalFolder import PortalFolderBase as PortalFolder
except ImportError:
    from Products.CMFCore.PortalFolder import PortalFolder

from Products.CMFCore.utils import getToolByName

_actions = ({'action': 'string:${object_url}',
           'id': 'view',
           'name': 'View',
           'permissions': ('View',)},
          {'action': 'string:${object_url}/folder_edit_form',
           'id': 'edit',
           'name': 'Edit',
           'permissions': ('Manage properties',)},
          {'action': 'string:${object_url}/folder_localrole_form',
           'id': 'localroles',
           'name': 'Local Roles',
           'permissions': ('Change local roles',)},
          {'action': 'string:${object_url}/folder_contents',
           'id': 'folderContents',
           'name': 'Folder contents',
           'permissions': ('List folder contents',)},
          {'action': 'string:${object_url}/folder_factories',
           'id': 'new',
           'name': 'New...',
           'permissions': ('Add portal content',),
           'visible': 0},
          {'action': 'string:${object_url}/folder_rename_form',
           'id': 'rename_items',
           'name': 'Rename items',
           'permissions': ('Add portal content',),
           'visible': 0})

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



InitializeClass(CMFHBTreeFolder)
