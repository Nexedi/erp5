##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
import OFS.Image
from zExceptions import Forbidden

PUT_orig = OFS.Image.File.PUT

def PUT(self, REQUEST, RESPONSE):
  """Handle HTTP PUT requests"""
  if REQUEST.environ['REQUEST_METHOD'] != 'PUT':
    raise Forbidden('REQUEST_METHOD should be PUT.')
  return PUT_orig(self, REQUEST, RESPONSE)

OFS.Image.File.PUT = PUT
