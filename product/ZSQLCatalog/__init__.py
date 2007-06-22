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

import ZSQLCatalog, SQLCatalog
from ZClasses import createZClassForBase

createZClassForBase( ZSQLCatalog.ZCatalog , globals()
                   , 'ZSQLCatalogBase', 'ZSQLCatalog' )
createZClassForBase( SQLCatalog.Catalog , globals()
                   , 'SQLCatalogBase', 'SQLCatalog' )

def initialize(context):
    context.registerClass(
        ZSQLCatalog.ZCatalog,
        permission='Add ZCatalogs',
        constructors=(ZSQLCatalog.manage_addZSQLCatalogForm,
                      ZSQLCatalog.manage_addZSQLCatalog),
        icon='www/ZCatalog.gif',
        )

    context.registerClass(
        SQLCatalog.Catalog,
        permission='Add ZCatalogs',
        constructors=(SQLCatalog.manage_addSQLCatalogForm,
                      SQLCatalog.manage_addSQLCatalog),
        icon='www/ZCatalog.gif',
        )

    context.registerHelp()
    context.registerHelpTitle('Zope Help')

from AccessControl import ModuleSecurityInfo, ClassSecurityInfo
ModuleSecurityInfo('Products.ZSQLCatalog.SQLCatalog').declarePublic('ComplexQuery', 'Query')
