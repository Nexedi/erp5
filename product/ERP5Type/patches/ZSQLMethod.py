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
from Products.ZSQLMethods.SQL import SQL
from App.special_dtml import DTMLFile
from Products.ERP5Type import _dtmldir

# Patch for displaying textearea in full window instead of
# remembering a quantity of lines to display in a cookie
manage_editForm = DTMLFile('ZSQLMethod_edit', _dtmldir)
SQL.manage = manage_editForm
SQL.manage_main = manage_editForm
