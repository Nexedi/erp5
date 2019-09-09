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

import base64
from cStringIO import StringIO
import unittest
import urllib

from OFS.DTMLMethod import DTMLMethod
from OFS.Folder import Folder
from AccessControl.User import UserFolder

from Products.CMFCore.CookieCrumbler import CookieCrumbler, manage_addCC
from Products.CMFCore.tests.test_CookieCrumbler import makerequest
from Products.CMFCore.tests.test_CookieCrumbler import CookieCrumblerTests

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

    self.credentials = urllib.quote(
        base64.encodestring('abraham:pass-w').replace('\012', ''))

  def testCookieLongLogin(self):
    # verify the user and auth cookie get set
    long_name = 'abrahammmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm'
    long_pass = 'pass-wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww'
    self.req.cookies['__ac_name'] = long_name
    self.req.cookies['__ac_password'] = long_pass
    self.req.traverse('/')

    self.assert_(self.req.has_key('AUTHENTICATED_USER'))
    self.assertEqual(self.req['AUTHENTICATED_USER'].getId(),
                         'abrahammmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm')
    resp = self.req.response
    self.assert_(resp.cookies.has_key('__ac'))
    self.credentials = base64.encodestring('%s:%s' % (long_name, long_pass)).replace('\012', '')
    self.assertEqual(resp.cookies['__ac']['value'],
                         self.credentials)
    self.assertEqual(resp.cookies['__ac']['path'], '/')

def test_suite():
    return unittest.makeSuite(ERP5CookieCrumblerTests)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
