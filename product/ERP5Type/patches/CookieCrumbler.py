##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2003 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""
Patch CookieCrumbler to prevent came_from to appear in the URL
when ERP5 runs in "require_referer" mode.
"""

from Products.CMFCore.CookieCrumbler import CookieCrumbler

class PatchedCookieCrumbler(CookieCrumbler):
  """
    This class is only for backward compatibility.
  """
  pass
    
def getLoginURL(self):
    '''
    Redirects to the login page.
    '''
    if self.auto_login_page:
        req = self.REQUEST
        resp = req['RESPONSE']
        iself = getattr(self, 'aq_inner', self)
        parent = getattr(iself, 'aq_parent', None)
        page = getattr(parent, self.auto_login_page, None)
        if page is not None:
            retry = getattr(resp, '_auth', 0) and '1' or ''
            came_from = req.get('came_from', None)
            if came_from is None:
                came_from = req['URL']
            if hasattr(self, 'getPortalObject') and self.getPortalObject()\
                          .getProperty('require_referer', 0) :
              url = '%s?retry=%s&disable_cookie_login__=1' % (
                page.absolute_url(), retry)
            else :
              url = '%s?came_from=%s&retry=%s&disable_cookie_login__=1' % (
                page.absolute_url(), quote(came_from), retry)
            return url
    return None

CookieCrumbler.getLoginURL = getLoginURL
