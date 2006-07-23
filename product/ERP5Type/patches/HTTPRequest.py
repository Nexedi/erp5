##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002,2005 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

# This patch is used by WebSite to rewrite URLs in such way
# that once a user gets into a Web Site object, all
# documents referenced by the web site are accessed
# through the web site rather than directly.

website_key = 'web_site_value'

from ZPublisher.HTTPRequest import HTTPRequest
def HTTPRequest_physicalPathToVirtualPath(self, path):
    """
      Remove the path to the VirtualRoot from a physical path
      and add the path to the WebSite is any
    """
    if type(path) is type(''):
      path = path.split( '/')

    website_path = self.get(website_key, None)
    if website_path:
      website_path = tuple(website_path)    # Make sure all path are tuples
      path = tuple(path)                    # Make sure all path are tuples
      # Search for the common part index
      # XXX more testing should be added to check
      # if the URL is the kind of URL which is a Web Site
      # XXX more support required for ignore_layout
      i = 0
      path_len = len(path)
      for name in website_path:
        if i >= path_len: break
        if path[i] == name:
          common_index = i
        i += 1
      # Insert the web site path after the common part of the path
      if path_len > common_index + 1:
        path = website_path + path[common_index + 1:]

    rpp = self.other.get('VirtualRootPhysicalPath', ('',))
    i = 0
    for name in rpp[:len(path)]:
      if path[i] == name:
        i = i + 1
      else:
        break
    return path[i:]

HTTPRequest.physicalPathToVirtualPath = HTTPRequest_physicalPathToVirtualPath