# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#          Vincent Pelletier <vincent@nexedi.com>
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

from Products.PageTemplates.utils import convertToUnicode

def patched_convertToUnicode(source, content_type, preferred_encodings):
    """ Convert 'source' to unicode.
        Returns (unicode_str, source_encoding).
    """

# PATCH BEGINING
# See https://bugs.launchpad.net/zope2/+bug/706946
    if isinstance(source, unicode):
        return source, 'utf-8'
# PATCH END
    if content_type.startswith('text/xml'):
        encoding = encodingFromXMLPreamble(source)
        return unicode(source, encoding), encoding

    elif content_type.startswith('text/html'):
        encoding = charsetFromMetaEquiv(source)
        if encoding:
            return unicode(source, encoding), encoding

    # Try to detect the encoding by converting it unicode without raising
    # exceptions. There are some smarter Python-based sniffer methods
    # available however we have to check their licenses first before
    # including them into the Zope 2 core

    for enc in preferred_encodings:
        try:
            return unicode(source, enc), enc
        except UnicodeDecodeError:
                continue

    return unicode(source), None

try:
    convertToUnicode(u'', 'text/xml', ())
except TypeError:
    # We need to monkey patch in-place, as it is a top-level function and
    # already imported in other places.
    convertToUnicode.__code__ = patched_convertToUnicode.__code__
