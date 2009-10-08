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

import HBTreeFolder2

def initialize(context):

    context.registerClass(
        HBTreeFolder2.HBTreeFolder2,
        constructors=(HBTreeFolder2.manage_addHBTreeFolder2Form,
                      HBTreeFolder2.manage_addHBTreeFolder2),
        icon='btreefolder2.gif',
        )

    #context.registerHelp()
    #context.registerHelpTitle('Zope Help')

    try:
        from Products.CMFCore import utils
    except ImportError:
        # CMF not installed
        pass
    else:
        # CMF installed; make available a special folder type.
        import CMFHBTreeFolder
        ADD_FOLDERS_PERMISSION = 'Add portal folders'

        utils.ContentInit(
            'CMF HBTree Folder',
            content_types=(CMFHBTreeFolder.CMFHBTreeFolder,),
            permission=ADD_FOLDERS_PERMISSION,
            extra_constructors=(CMFHBTreeFolder.manage_addCMFHBTreeFolder,),
            fti=CMFHBTreeFolder.factory_type_information
            ).initialize(context)

