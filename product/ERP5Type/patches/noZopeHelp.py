##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# Copyright (c) 2013 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

# copied & pasted from Testing.ZopeTestCase.ZopeLite
import App.ProductContext

if 1:
    # Avoid expensive help registration
    def null_register_topic(self,id,topic): pass
    App.ProductContext.ProductContext.registerHelpTopic = null_register_topic
    def null_register_title(self,title): pass
    App.ProductContext.ProductContext.registerHelpTitle = null_register_title
    def null_register_help(self,directory='',clear=1,title_re=None): pass
    App.ProductContext.ProductContext.registerHelp = null_register_help
