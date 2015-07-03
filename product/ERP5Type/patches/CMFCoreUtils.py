##############################################################################
#
# Copyright (c) 2001 Zope Foundation and Contributors.
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName, SUBTEMPLATE

# patch _setCacheHeaders so that existing headers are not overridden
def _setCacheHeaders(obj, extra_context):
    """Set cache headers according to cache policy manager for the obj."""
    REQUEST = getattr(obj, 'REQUEST', None)

    if REQUEST is not None:
        call_count = getattr(REQUEST, SUBTEMPLATE, 1) - 1
        setattr(REQUEST, SUBTEMPLATE, call_count)
        if call_count != 0:
           return

        # cleanup
        delattr(REQUEST, SUBTEMPLATE)

        content = aq_parent(obj)
        manager = getToolByName(obj, 'caching_policy_manager', None)
        if manager is None:
            return

        view_name = obj.getId()
        headers = manager.getHTTPCachingHeaders(
                          content, view_name, extra_context
                          )
        RESPONSE = REQUEST['RESPONSE']
        for key, value in headers:
            if key == 'ETag':
                RESPONSE.setHeader(key, value, literal=1)
            # PATCH BEGIN: respect existing Cache-Control header if exists
            if key.lower() == 'cache-control':
                cache_control = RESPONSE.getHeader('cache-control')
                if cache_control:
                    existing_key_list = \
                        [e.split('=', 2)[0].strip().lower() for e in \
                         cache_control.split(',')]
                    for e in value.split(','):
                        if e.split('=', 2)[0].strip().lower() not in existing_key_list:
                            cache_control += ', %s' % e.strip()
                else:
                    cache_control = value
                RESPONSE.setHeader(key, cache_control)
            # PATCH END
            else:
                RESPONSE.setHeader(key, value)
        if headers:
            RESPONSE.setHeader('X-Cache-Headers-Set-By',
                               'CachingPolicyManager: %s' %
                               '/'.join(manager.getPhysicalPath()))

import Products.CMFCore.utils
Products.CMFCore.utils._setCacheHeaders = _setCacheHeaders
