##############################################################################
#
# Base18: a Zope product which provides multilingual services for CMF Default
#         documents.
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
#
# This program as such is not intended to be used by end users. End
# users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the Zope Public License (ZPL) Version 2.0
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################

from Products.CMFCore.CookieCrumbler import CookieCrumbler
from urllib import quote
from AccessControl import ClassSecurityInfo

class Base18CookieCrumbler(CookieCrumbler):
   # Dynamic Patch Class

   # Declarative security
   security = ClassSecurityInfo()

   security.declarePublic('getLoginURL')
   def getLoginURL(self):
       """
       Redirects to the login page.
       XXX Take from CookieCrumbler -> license should be ZPL
       """
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
               came_from_list = list(came_from.split('/'))
               # Find the object where we came form
               # And forget about trailing URL
               try:
                came_from_object = parent.restrictedTraverse(came_from_list[3:-1])
                url = '%s?came_from=%s&retry=%s&disable_cookie_login__=1' % (
                    came_from_object.local_absolute_url(target=page), quote(came_from), retry)
                return url
               except:
                try:
                 url = '%s?came_from=%s&retry=%s&disable_cookie_login__=1' % (
                    self.local_absolute_url(), quote(came_from), retry)
                    #self.local_absolute_url(target=page), quote(came_from), retry)
                except:
                 relative_url = self.portal_url.getRelativeUrl(self)
                 absolute_url=self.portal_url.getPortalObject().absolute_url()
                 local_absolute_url='%s/%s' % (absolute_url,relative_url)
                 url = '%s?came_from=%s&retry=%s&disable_cookie_login__=1' % (
                    local_absolute_url, quote(came_from), retry)
                return url
       return None

# Dynamic Patch
CookieCrumbler.getLoginURL = Base18CookieCrumbler.getLoginURL
