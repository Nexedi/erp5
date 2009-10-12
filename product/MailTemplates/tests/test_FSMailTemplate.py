# Copyright (c) 2005-2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import os
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.User import system as SystemUser,SimpleUser
from cStringIO import StringIO
from OFS.Folder import Folder
from Products.MailHost.MailHost import MailHost
from test_MailTemplate import DummyMailHost,Zope,get_transaction
from Testing.makerequest import makerequest
from unittest import TestCase,TestSuite,makeSuite,main

try:
    import Products.CMFCore
except ImportError:
    # no CMF, no use ;-)
    class TestFSMailTemplate(TestCase):
        pass
else:
    from Products.CMFCore.DirectoryView import addDirectoryViews
    from Products.CMFCore.tests.base.testcase import FSDVTest
    from Products.CMFCore.tests.base.dummy import DummyFolder
    from AccessControl import ClassSecurityInfo
    from App.class_init import default__class_init__ as InitializeClass
    
    class DummyMember:

        security = ClassSecurityInfo()
        
        security.declareObjectPublic()
        security.setDefaultAccess('allow')

        security.declarePublic('getUserName')
        def getUserName(self):
            return 'Test Member'

        security.declarePublic('getProperty')
        def getProperty(self,name):
            return 'member@example.com'

    InitializeClass(DummyMember)
    
    class DummyMembershipTool:

        security = ClassSecurityInfo()

        security.declareObjectPublic()
        security.setDefaultAccess('allow')

        security.declarePublic('listMembers')
        def listMembers(self):
            return (DummyMember(),)

    InitializeClass(DummyMembershipTool)
    
    class TestFSMailTemplate(FSDVTest):
        
        _sourceprefix = os.path.dirname(__file__)

        def setUp(self):
            FSDVTest.setUp(self)
            self.app = makerequest(Zope.app())
            self._registerDirectory()
            ob = self.ob = self.app
            addDirectoryViews(ob, self._skinname, self.tempname)
            self.r = self.app.REQUEST
            self.r.other['URL1'] = 'http://foo/test_mt'
            self._add= self.app.manage_addProduct['MailTemplates'].addMailTemplate
            self.folder = Folder('folder')
            if getattr(self.app,'test_mt',None):
                self.app.manage_delObjects(ids=['test_mt'])
            if getattr(self.app,'MailHost',None):
                self.app.manage_delObjects(ids=['MailHost'])
            self.MailHost = self.app.MailHost = DummyMailHost()
            newSecurityManager( None, SystemUser )
        
        def tearDown(self):
            noSecurityManager()
            get_transaction().abort()
            self.app._p_jar.close()
            try:
                FSDVTest.tearDown(self)
            except OSError:
                # waggh, on windows, files in .svn get locked for some reason :-(
                pass


        def test_render(self):
            self.MailHost.setExpected(mfrom='from@example.com',
                                      mto=('to@example.com','to2@example.com'),
                                      filename='mail_FSSendSimple.txt')

            self.ob.fake_skin.test.send(subject=self.ob.fake_skin.test.subject % 'out',
                                        mcc=('cc@example.com',),
                                        mbcc=('bcc@example.com',),
                                        headers={
                'To':('to@example.com','to2@example.com'),
                'Subject':'cheese',
                })

            self.MailHost.checkSent()
        
            # check we're not setting a content type
            self.failIf(self.r.RESPONSE.headers.get('content-type'),
                        self.r.RESPONSE.headers)

        def test_properties(self):
            self.assertEqual(self.ob.fake_skin.test.mailhost,'MailHost')
            self.assertEqual(self.ob.fake_skin.test.subject,'Hello %s there')
            self.assertEqual(self.ob.fake_skin.test.mfrom,'from@example.com')
            
        def test_zodbclone(self):
            from Products.MailTemplates.MailTemplate import MailTemplate
            clone = self.ob.fake_skin.test._createZODBClone()
            self.failUnless(isinstance(clone,MailTemplate),'Clone not a MailTemplate!')
            self.assertEqual(self.ob.fake_skin.test.read(),clone.read())
            self.assertEqual(clone.getProperty('mailhost'),None)
            self.assertEqual(clone.mailhost,'MailHost')
            self.assertEqual(clone.getProperty('subject'),'Hello %s there')
            self.assertEqual(clone.getProperty('mfrom'),'from@example.com')
            self.assertEqual(clone.content_type,'text/notplain')
            
        def test_view_manage_workspace(self):
            from zExceptions import Redirect
            try:
                self.assertRaises(self.ob.fake_skin.test.manage_workspace(self.r))
            except Redirect,r:
                # this may appear to be incorrect, but http://foo/test_mt
                # is what we set as REQUEST['URL1']
                self.assertEqual(r.args,('http://foo/test_mt/manage_main',))
            self.ob.fake_skin.test.manage_main()
            # ugh, okay, so we can't really test for security, but lets
            # test for the missing docstring that was causing problems!
            self.failUnless(self.ob.fake_skin.test.__doc__)
            
        def test_example2(self):
            # login
            noSecurityManager()
            self.app.aq_chain[-1].id = 'testing'
            newSecurityManager(
                None,
                SimpleUser('Test User','',('Manager',),[]).__of__(self.app)
                )
            try:
                # setup
                self.app.portal_membership = DummyMembershipTool()
                # set expected
                self.MailHost.setExpected(mfrom='webmaster@example.com',
                                          mto='member@example.com',
                                          filename='example2.txt')
                # test
                self.ob.fake_skin.send_mails()
            finally:
                # logout
                noSecurityManager()
                newSecurityManager( None, SystemUser )

def test_suite():
    return TestSuite((
        makeSuite(TestFSMailTemplate),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')

