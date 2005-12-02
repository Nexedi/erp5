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

#CookieCrumbler: remove "?came_from" from getLoginUrl (called by request.unauthorized)
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
            url = '%s?retry=%s&disable_cookie_login__=1' % (
                page.absolute_url(), retry)
            return url
    return None

CookieCrumbler.getLoginURL = getLoginURL
