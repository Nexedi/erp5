##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""ZCatalog product"""

import ZSQLCatalog, SQLCatalog, ZopePatch
from ZClasses import createZClassForBase

createZClassForBase( ZSQLCatalog.ZCatalog , globals()
                   , 'ZCatalogBase', 'ZCatalog' )

def initialize(context):
    context.registerClass(
        ZSQLCatalog.ZCatalog,
        permission='Add ZCatalogs',
        constructors=(ZSQLCatalog.manage_addZCatalogForm,
                      ZSQLCatalog.manage_addZCatalog),
        icon='www/ZCatalog.gif',
        )

    context.registerHelp()
    context.registerHelpTitle('Zope Help')

