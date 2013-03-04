# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
##############################################################################

from logging import getLogger
import traceback
logger = getLogger(__name__)

from Products.PageTemplates.unicodeconflictresolver \
       import PreferredCharsetResolver

def PreferredCharsetResolver_resolve(context, text, expression):
    # Since we use UTF-8 only in PageTemplate, it is enough here. It is
    # faster than the original implementation, and it is compatible with
    # requests that do not contain Accept-Charset header.
    try:
      result = unicode(text, 'utf-8')
    except UnicodeDecodeError, e:
      tb_info = ''.join(traceback.format_stack())
      logger.warn('UnicodeDecodeError: %s\ntext: %r\nat:\n%s' %
                  (e, repr(text), tb_info))
      result = unicode(text, 'utf-8', 'replace')
    return result
PreferredCharsetResolver.resolve = PreferredCharsetResolver_resolve
