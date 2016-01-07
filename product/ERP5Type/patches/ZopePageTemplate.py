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
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ERP5Type import _dtmldir
import os

# Patch for displaying textearea in full window instead of
# remembering a quantity of lines to display in a cookie
pt_editForm = PageTemplateFile(os.path.join(_dtmldir, "ptEdit"), globals(),
                               __name__='pt_editForm' )
pt_editForm._owner = None
ZopePageTemplate.pt_editForm = pt_editForm
ZopePageTemplate.manage = pt_editForm
ZopePageTemplate.manage_main = pt_editForm

