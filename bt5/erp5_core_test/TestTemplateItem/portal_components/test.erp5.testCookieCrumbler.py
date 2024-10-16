##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import six
if six.PY2:
  from base64 import encodestring as encodebytes
else:
  from base64 import encodebytes
from six.moves import cStringIO as StringIO
import unittest
from six.moves.urllib.parse import quote

from OFS.DTMLMethod import DTMLMethod
from OFS.Folder import Folder
from OFS.userfolder import UserFolder

from Products.CMFCore.CookieCrumbler import CookieCrumbler
from Products.CMFCore.tests.test_CookieCrumbler import makerequest
from Products.CMFCore.tests.test_CookieCrumbler import CookieCrumblerTests
from Products.ERP5Type.Utils import bytes2str, str2bytes
try:
  from Products.CMFCore.tests.test_CookieCrumbler import normalizeCookieParameterName
except ImportError: # BBB Zope2
  normalizeCookieParameterName = lambda s: s

class ERP5CookieCrumblerTests (CookieCrumblerTests):
  """ Modify original CMFCore Cookie Crumbler unit test to test long login """

  def setUp(self):
    CookieCrumblerTests.setUp(self)
    root = Folder()
    self.root = root
    root.isTopLevelPrincipiaApplicationObject = 1  # User folder needs this
    root.getPhysicalPath = lambda: ()  # hack
    root._View_Permission = ('Anonymous',)

    users = UserFolder()
    users._setId('acl_users')
    users._doAddUser('abraham', 'pass-w', ('Patriarch',), ())
    users._doAddUser('isaac', 'pass-w', ('Son',), ())
    users._doAddUser('abrahammmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm',
                     'pass-wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww',
                     ('Son',), ())
    root._setObject(users.id, users)

    cc = CookieCrumbler()
    cc.id = 'cookie_authentication'
    root._setObject(cc.id, cc)
    self.cc = getattr(root, cc.id)

    index = DTMLMethod()
    index.munge('This is the default view')
    index._setId('index_html')
    root._setObject(index.getId(), index)

    login = DTMLMethod()
    login.munge('Please log in first.')
    login._setId('login_form')
    root._setObject(login.getId(), login)

    protected = DTMLMethod()
    protected._View_Permission = ('Manager',)
    protected.munge('This is the protected view')
    protected._setId('protected')
    root._setObject(protected.getId(), protected)

    self.responseOut = StringIO()
    self.req = makerequest(root, self.responseOut)

    self.credentials = quote(
        bytes2str(encodebytes(b'abraham:pass-w')).replace('\012', ''))

  def testCookieLongLogin(self):
    # verify the user and auth cookie get set
    long_name = 'abrahammmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm'
    long_pass = 'pass-wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
    self.req.cookies['__ac_name'] = long_name
    self.req.cookies['__ac_password'] = long_pass
    self.req.traverse('/')

    self.assertIn('AUTHENTICATED_USER', self.req)
    self.assertEqual(self.req['AUTHENTICATED_USER'].getId(),
                         'abrahammmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm')
    resp = self.req.response
    self.assertIn('__ac', resp.cookies)
    self.credentials = bytes2str(encodebytes(str2bytes('%s:%s' % (long_name, long_pass)))).replace('\012', '')
    self.assertEqual(resp.cookies['__ac']['value'],
                         self.credentials)
    self.assertEqual(resp.cookies['__ac'][normalizeCookieParameterName('path')], '/')

  def testCacheHeaderDisabled(self):
    # Cache header is forcibly set on any authenticated user independently from
    # CookieCrumbler's presence.
    _, cc, req, credentials = self._makeSite()
    cc.cache_header_value = ''
    req.cookies['__ac'] = credentials
    req.traverse('/')
    self.assertEqual(
        req.response.headers.get('cache-control', ''), 'private')


def test_suite():
  return unittest.makeSuite(ERP5CookieCrumblerTests)

if __name__ == '__main__':
  unittest.main(defaultTest='test_suite')
