##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
##############################################################################

from Acquisition import aq_base
from webdav.NullResource import NullResource

class ExtensibleTraversableMixin:
  def __bobo_traverse__(self, request, name):
    """
    If no subobject is found through Folder API
    then try to lookup the object by invoking _getExtensibleContent
    """
    # Normal traversal
    try:
      return getattr(self, name)
    except AttributeError:
      pass

    try:
      return self[name]
    except KeyError:
      pass

    document = self.getExtensibleContent(request, name)
    if document is not None:
      return aq_base(document).__of__(self)

    # Not found section
    method = request.get('REQUEST_METHOD', 'GET')
    if not method in ('GET', 'POST'):
      return NullResource(self, name, request).__of__(self)
    # Waaa. unrestrictedTraverse calls us with a fake REQUEST.
    # There is proabably a better fix for this.
    try:
      request.RESPONSE.notFoundError("%s\n%s" % (name, method))
    except AttributeError:
      raise KeyError(name)

ExtensibleTraversableMixIn = ExtensibleTraversableMixin # Backward compatibility