# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#          Leonardo Rochael Almeida <leonardo@nexedi.com>
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

# BBB: This whole file is unnecessary once we drop support for Zope 2.8

from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate

marker = object()

if getattr(ZopePageTemplate, 'output_encoding', marker) is marker:
    # pre-Zope 2.10, non-unicode Zope Page Templates.
    # downgrade source code and title to utf-8 for compatibility
    def __setstate__(self, state):
        # Perform on-the-fly migration from unicode.
        if isinstance(state.get('_text'), unicode):
            state['_text'] = state['_text'].encode('utf-8')
        if isinstance(state.get('title'), unicode):
            state['title'] = state['title'].encode('utf-8')
        ZopePageTemplate.inheritedAttribute('__setstate__')(self, state)

    ZopePageTemplate.__setstate__ = __setstate__


