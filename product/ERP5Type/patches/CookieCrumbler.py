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

from future import standard_library
standard_library.install_aliases()
from AccessControl.SecurityInfo import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore.CookieCrumbler import CookieCrumbler
from Products.CMFCore.CookieCrumbler import CookieCrumblerDisabled
from urllib.parse import quote, unquote
from ZPublisher.HTTPRequest import HTTPRequest

ATTEMPT_NONE = 0       # No attempt at authentication
ATTEMPT_LOGIN = 1      # Attempt to log in
ATTEMPT_RESUME = 2     # Attempt to resume session

from base64 import standard_b64encode, standard_b64decode
from DateTime import DateTime

class PatchedCookieCrumbler(CookieCrumbler):
  """
    This class is only for backward compatibility.
  """
  pass

security = ClassSecurityInfo()

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

security.declarePublic('getLoginURL')
CookieCrumbler.getLoginURL = getLoginURL

def balancer_cookie_hook(ob, req, resp):
  """Post publishing traversal hook to automatically (un)set balancer cookie

  If authenticated, then cookie is set to use the same zope on next request,
  for a better use of caches. Otherwise, if anonymous, expire cookie so that
  the balancer redirects us on any zope.

  XXX: Because we only have persistent traversal hooks and we don't want to
       complicate code with automatic upgrade, this one is implemented by
       pluging into CookieCrumbler, although what they are quite unrelated.
  """
  # Balancer gives us the name of the cookie it wants to use.
  balancer_cookie = req.get('HTTP_X_BALANCER_CURRENT_COOKIE')
  if balancer_cookie:
    try:
      path = ob.aq_parent.absolute_url_path()
    except AttributeError:
      path = '/'
    if req['AUTHENTICATED_USER'].getUserName() == 'Anonymous User':
      if balancer_cookie in req.cookies:
        resp.expireCookie(balancer_cookie, path=path)
    else:
      if balancer_cookie not in req.cookies:
        # Balancer is expected to rewrite this cookie's value to whatever
        # our identifier (from its point of view) is.
        resp.setCookie(balancer_cookie, 'anything', path=path);

def modifyRequest(self, req, resp):
  """Copies cookie-supplied credentials to the basic auth fields.

  Returns a flag indicating what the user is trying to do with
  cookies: ATTEMPT_NONE, ATTEMPT_LOGIN, or ATTEMPT_RESUME.  If
  cookie login is disabled for this request, raises
  CookieCrumblerDisabled.
  """
  enabled = (req.__class__ is HTTPRequest
      and req['REQUEST_METHOD'] in ('HEAD', 'GET', 'PUT', 'POST')
      and 'WEBDAV_SOURCE_PORT' not in req.environ)
  if enabled:
    req.post_traverse(balancer_cookie_hook, (self, req, resp))

    # attempt may contain information about an earlier attempt to
    # authenticate using a higher-up cookie crumbler within the
    # same request.
    attempt = getattr(req, '_cookie_auth', ATTEMPT_NONE)

    if attempt == ATTEMPT_NONE:
      if req._auth:
        # An auth header was provided and no cookie crumbler
        # created it.  The user must be using basic auth.
        enabled = False
      elif self.pw_cookie in req and self.name_cookie in req:
        # Attempt to log in and set cookies.
        attempt = ATTEMPT_LOGIN
        name = req[self.name_cookie]
        pw = req[self.pw_cookie]
        ac = standard_b64encode('%s:%s' % (name, pw))
        self._setAuthHeader(ac, req, resp)
        if req.get(self.persist_cookie, 0):
          # Persist the user name (but not the pw or session)
          expires = (DateTime() + 365).toZone('GMT').rfc822()
          resp.setCookie(self.name_cookie, name,
                         path=self.getCookiePath(),
                         expires=expires)
        else:
          # Expire the user name
          resp.expireCookie(self.name_cookie,
                            path=self.getCookiePath())
        method = self.getCookieMethod( 'setAuthCookie'
                                       , self.defaultSetAuthCookie )
        method( resp, self.auth_cookie, quote( ac ) )
      elif self.auth_cookie in req:
        # Attempt to resume a session if the cookie is valid.
        # Copy __ac to the auth header.
        ac = unquote(req[self.auth_cookie])
        if ac and ac != 'deleted':
          try:
            standard_b64decode(ac)
          except:
            # Not a valid auth header.
            pass
          else:
            attempt = ATTEMPT_RESUME
            self._setAuthHeader(ac, req, resp)
            self.delRequestVar(req, self.auth_cookie)
            method = self.getCookieMethod(
              'twiddleAuthCookie', None)
            if method is not None:
              method(resp, self.auth_cookie, quote(ac))

  self.delRequestVar(req, self.auth_cookie)
  self.delRequestVar(req, self.name_cookie)
  self.delRequestVar(req, self.pw_cookie)
  if not enabled:
    raise CookieCrumblerDisabled
  req._cookie_auth = attempt
  return attempt

CookieCrumbler.modifyRequest = modifyRequest


def credentialsChanged(self, user, name, pw):
  ac = standard_b64encode('%s:%s' % (name, pw))
  method = self.getCookieMethod( 'setAuthCookie'
                                 , self.defaultSetAuthCookie )
  resp = self.REQUEST['RESPONSE']
  method( resp, self.auth_cookie, quote( ac ) )

CookieCrumbler.credentialsChanged = credentialsChanged

CookieCrumbler.security = security
InitializeClass(CookieCrumbler)
