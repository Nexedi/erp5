# -*- coding: latin-1 -*-
# Copyright (c) 2005-2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.
import os

try:
    import Zope2 as Zope
except ImportError:
    import Zope

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.User import system as SystemUser, SimpleUser
from io import StringIO
from difflib import unified_diff
from Products.MailHost.MailHost import MailHost
from Testing.makerequest import makerequest
from unittest import TestCase,TestSuite,makeSuite,main

try:
    # Zope 2.8 only
    from transaction import get as get_transaction
except ImportError:
    # Zope 2.7 only, allows get_transaction
    # to be imported from test_FSMailTemplate.
    get_transaction = get_transaction

test_folder = os.path.dirname(__file__)

class DummyFieldStorage:
    def __init__(self,filename,value):
        self.filename = filename
        self.value = value
        self.file = StringIO(value)
        self.content_type = None
        self.headers = {}

class DummyMailHost(MailHost):

    sent = False

    def setExpected(self,mfrom,mto,filename):
        self.mfrom = mfrom
        self.mto = mto
        self.messageText = open(
            os.path.join(test_folder,filename)
            ).read().replace('\r','')
        self.filename = filename

    def getId(self):
        return 'MailHost'

    def title_and_id(self):
        return 'MHTID'

    def assertEqual(self,x,y,message=None,field=None):
        if x!=y:
            if message:
                raise AssertionError(message)
            error = '%r!=%r' % (x,y)
            if field:
                error = field+':'+error
            raise AssertionError(error)


    def _send(self,mfrom,mto,messageText):
        self.assertEqual(self.mfrom,mfrom,field='mfrom')
        self.assertEqual(self.mto,mto,field='mto')
        expected_data = self.messageText.strip().split('\n')
        actual_data = messageText.strip().split('\n')
        # ignore dates
        for i in range(len(actual_data)):
            if actual_data[i].startswith('Date:'):
                actual_data[i]='Date:'
        diff = tuple(unified_diff(
            expected_data,
            actual_data,
            self.filename,
            'Test results',
            ))
        if diff:
            raise AssertionError(
                'Mail sent was not as expected:\n\n'+'\n'.join(diff)
                )

        self.sent = True

    def checkSent(self,value=True):
        if value:
            error = "Mail not sent"
        else:
            error = "Mail sent when it shouldn't have been"
        self.assertEqual(self.sent,value,error)

class DummyMailDropHost(DummyMailHost):

    meta_type = 'Maildrop Host'

class TestMailTemplate(TestCase):

    def setUp(self):
        self.app = makerequest(Zope.app())
        self.r = self.app.REQUEST
        self.r.other['URL1'] = 'http://foo/test_mt'
        self._add= self.app.manage_addProduct['MailTemplates'].addMailTemplate
        if getattr(self.app,'test_mt',None):
            self.app.manage_delObjects(ids=['test_mt'])
        if getattr(self.app,'MailHost',None):
            self.app.manage_delObjects(ids=['MailHost'])
        self.MailHost = self.app.MailHost = DummyMailHost()
        o = list(self.app._objects)
        o.append({'meta_type': 'Mail Host', 'id': 'MailHost'})
        self.app._objects = tuple(o)
        newSecurityManager( None, SystemUser )

    def tearDown(self):
        noSecurityManager()
        get_transaction().abort()
        self.app._p_jar.close()

    def makeFileUpload(self,filename='test.txt',value='test text',
                       diskname=''):
        if diskname:
            filename = diskname
            value = open(
                os.path.join(test_folder,diskname)
                ).read().replace('\r','').strip()
        from ZPublisher.HTTPRequest import FileUpload
        return FileUpload(DummyFieldStorage(
            filename,
            value
            ))

    def checkContent(self,text='test text'):
        if text is None:
            text = open(os.path.join(test_folder,'..','www','default.txt')).read()
        self.assertEqual(
            self.app.test_mt.document_src({'raw':1}),
            text
            )

    # Test Adding

    def test_addAddForm(self):
        self.app.manage_addProduct['MailTemplates'].addMailTemplateForm()

    def test_addAddFormNoMailHosts(self):
        self.app.manage_delObjects(ids=['MailHost'])
        res = self.app.manage_addProduct['MailTemplates'].addMailTemplateForm()
        self.assertTrue(
            res.find(
            '<option value="MailHost">MHTID</option>'
            )==-1
            )

    def test_addAddFormMailHost(self):
        self.app._objects = ({'meta_type': 'Mail Host', 'id': 'MailHost'},)
        res = self.app.manage_addProduct['MailTemplates'].addMailTemplateForm()
        self.assertFalse(
            res.find(
            '<option value="MailHost">MHTID</option>'
            )==-1
            )

    def test_addAddFormMailDropHost(self):
        if getattr(self.app,'MailHost',None):
            self.app.manage_delObjects(ids=['MailHost'])
        self.MailHost = self.app.MailHost = DummyMailDropHost()
        self.app._objects = ({'meta_type': 'Maildrop Host', 'id': 'MailHost'},)
        res = self.app.manage_addProduct['MailTemplates'].addMailTemplateForm()
        self.assertFalse(
            res.find(
            '<option value="MailHost">MHTID</option>'
            )==-1
            )

    def test_addNoREQUEST(self):
        self._add('test_mt','MailHost')
        # check settings
        self.assertEqual(self.app.test_mt.expand,0)
        self.assertEqual(self.app.test_mt.mailhost,'MailHost')
        self.assertEqual(self.app.test_mt.content_type,'text/plain')
        # check default content
        self.checkContent(None)

    def test_addNoMailHostSelected(self):
        self._add('test_mt',REQUEST=self.r)
        # check settings
        self.assertEqual(self.app.test_mt.expand,0)
        self.assertEqual(self.app.test_mt.mailhost,None)
        self.assertEqual(self.app.test_mt.content_type,'text/plain')
        # check default content
        self.checkContent(None)
        # check the error we get when we try to send
        self.assertRaises(
            RuntimeError,self.app.test_mt,
            mfrom='from@example.com',
            mto='to@example.com',
            subject='Test Subject',
            )
        # no put a mogus mailhost in and check we get the same error
        self.app.test_mt.mailhost='bogus'
        self.assertRaises(
            RuntimeError,self.app.test_mt,
            mfrom='from@example.com',
            mto='to@example.com',
            subject='Test Subject',
            )

    def test_add(self,body = None):
        text = open(os.path.join(test_folder,'..','www','default.txt')).read()
        if body is not None:
            text = text[:-12] + body + text[-11:]
            self._add('test_mt','MailHost',text=text,REQUEST=self.r)
        else:
            self._add('test_mt','MailHost',REQUEST=self.r)

        self.assertEqual(
            self.r.RESPONSE.headers,
            {'status': '302 Moved Temporarily', 'location': 'http://foo/manage_main'}
            )
        self.mt = self.app.test_mt
        # check settings
        self.assertEqual(self.mt.expand,0)
        self.assertEqual(self.mt.mailhost,'MailHost')
        self.assertEqual(self.mt.content_type,'text/plain')
        # check default content
        self.assertEqual(
            self.app.test_mt.read(),
            text
            )
        # check default content type is text/plain
        self.assertEqual(self.app.test_mt.content_type,'text/plain')

    def test_addFile(self):
        self.r.form['file'] = self.makeFileUpload()
        self._add('test_mt','MailHost',REQUEST=self.r)
        # check settings
        self.assertEqual(self.app.test_mt.expand,0)
        self.assertEqual(self.app.test_mt.mailhost,'MailHost')
        self.assertEqual(self.app.test_mt.content_type,'text/plain')
        # check default content
        self.checkContent()

    def test_addEdit(self):
        self._add('test_mt','MailHost',REQUEST=self.r,submit=' Add and Edit ')
        self.assertEqual(
            self.r.RESPONSE.headers,
            {'status': '302 Moved Temporarily', 'location': 'http://foo/test_mt/manage_main'}
            )
        # check settings
        self.assertEqual(self.app.test_mt.expand,0)
        self.assertEqual(self.app.test_mt.mailhost,'MailHost')
        self.assertEqual(self.app.test_mt.content_type,'text/plain')
        # check default content
        self.checkContent(None)

    def test_addEditFile(self):
        self.r.form['file'] = self.makeFileUpload()
        self._add('test_mt','MailHost',REQUEST=self.r,submit=' Add and Edit ')
        self.assertEqual(
            self.r.RESPONSE.headers,
            {'status': '302 Moved Temporarily', 'location': 'http://foo/test_mt/manage_main'}
            )
        # check settings
        self.assertEqual(self.app.test_mt.expand,0)
        self.assertEqual(self.app.test_mt.mailhost,'MailHost')
        self.assertEqual(self.app.test_mt.content_type,'text/plain')
        # check default content
        self.checkContent()

    # Test Properties Tab
    # Not much here, as we assume PropertyManager does its job ;-)

    def test_PropertiesForm(self):
        self.test_add()
        self.mt.manage_propertiesForm()

    def test_PropertiesStartsEmpty(self):
        self.test_add()
        self.assertFalse(self.mt.propertyMap())

    # Test Test tab, well, actually, make sure it's not there ;-)

    def test_NoTestTab(self):
        from Products.MailTemplates.MailTemplate import MailTemplate
        for option in MailTemplate.manage_options:
            if option['label']=='Test':
                self.fail('Test label found')
        self.assertFalse(MailTemplate.ZScriptHTML_tryForm, 'try form not None')

    # Test Editing

    def test_editForm(self):
        self.test_add()
        self.mt.pt_editForm()

    def test_editFormMailHostGone(self):
        self.test_add()
        self.app.manage_delObjects('MailHost')
        r = self.mt.pt_editForm()
        self.assertFalse(
            r.find(
            """<option selected="selected" value="MailHost">'MailHost' is no longer valid!</option>"""
            )==-1,'No warning for MailHost being invalid found in:\n'+r
            )

    def test_editAction(self):
        self.test_add()
        self.mt.pt_editAction(REQUEST=self.r,
                              mailhost='MH2',
                              text='new text',
                              content_type='text/fish',
                              expand=1)
        self.assertEqual(self.mt.expand,1)
        self.assertEqual(self.mt.mailhost,'MH2')
        self.assertEqual(self.mt.content_type,'text/fish')
        self.checkContent('new text')

    def test_view_manage_workspace(self):
        self.test_add()
        from zExceptions import Redirect
        try:
            self.assertRaises(self.mt.manage_workspace(self.r))
        except Redirect as r:
            # this may appear to be incorrect, but http://foo/test_mt
            # is what we set as REQUEST['URL1']
            self.assertEqual(r.args,('http://foo/test_mt/pt_editForm',))
        # ugh, okay, so we can't really test for security, but lets
        # test for the missing docstring that was causing problems!
        self.assertTrue(self.mt.__doc__)

    def test_view_manage_main(self):
        self.test_add()
        # for some bizare reason the output differs by a newline the first time these are called :-(
        self.mt.manage_main()
        self.mt.pt_editForm()
        self.assertEqual(self.mt.manage_main(),self.mt.pt_editForm())

    # Test Sending
    def testSendSimple(self):
        self.test_add('Test Body')
        self.MailHost.setExpected(mfrom='from@example.com',
                                  mto=('to@example.com', 'to2@example.com',
                                       'cc@example.com', 'bcc@example.com'),
                                  filename='mail_SendSimple.txt')
        self.mt.send(
            mfrom='from@example.com',
            mto=('to@example.com','to2@example.com'),
            mcc=('cc@example.com',),
            mbcc=('bcc@example.com',),
            subject='Hello out there',
            )

        self.MailHost.checkSent()

        # check we're not setting a content type
        self.assertFalse(self.r.RESPONSE.headers.get('content-type'),
                    self.r.RESPONSE.headers)

    def testMailHostNotAMailHost(self):
        self.test_add('Test Body')
        self.app.MailHost='Hahaha, not a MailHost'
        self.assertRaises(
            RuntimeError,
            self.mt.send,
            mfrom='from@example.com',
            mto=('to@example.com','to2@example.com'),
            mcc=('cc@example.com',),
            mbcc=('bcc@example.com',),
            subject='Hello out there',
            )

    def _shouldFail(self,error,**params):
        self.test_add('Test Body')
        try:
            self.mt.send(**params)
        except TypeError as e:
            self.assertEqual(e.args[0],error)
        else:
            self.fail('Mail sent even though params missing')
        self.MailHost.checkSent(False)

    def testSendMissingParams1(self):
        self._shouldFail(
            'The following parameters were required by not specified: subject',
            mto='to@example.com',
            mfrom='from@example.com'
            )

    def testSendMissingParams2(self):
        self._shouldFail(
            'The following parameters were required by not specified: mfrom',
            mto='to@example.com',
            subject='Test Subject'
            )

    def testSendMissingParams3(self):
        self._shouldFail(
            'The following parameters were required by not specified: mto',
            mfrom='from@example.com',
            subject='Test Subject'
            )

    def testSendMissingParamsAll(self):
        self._shouldFail(
            'The following parameters were required by not specified: mfrom, mto, subject',
            )

    def testSendProperties(self):
        self.test_add('Test Body')
        self.MailHost.setExpected(mfrom='from@example.com',
                                  mto=('to@example.com', 'to2@example.com',
                                       'cc@example.com', 'bcc@example.com'),
                                  filename='mail_SendSimple.txt')
        for name,type,value in (
            ('mfrom','string','from@example.com'),
            ('mto','string','to@example.com, to2@example.com'),
            ('mbcc','lines',('bcc@example.com',)),
            ('subject','string','Hello out there'),
            ('headers','lines',
             ('Cc:cc@example.com',)),
            ):
            self.mt.manage_addProperty(name,value,type)

        self.mt.send()

        self.MailHost.checkSent()

    def testSendHeadersDict(self):
        self.test_add('Test Body')
        self.MailHost.setExpected(mfrom='from@example.com',
                                  mto=('to@example.com','to2@example.com',
                                       'cc@example.com', 'bcc@example.com'),
                                  filename='mail_SendHeaders.txt')
        self.mt.send(
            headers = {
            'From':'from@example.com',
            'To':('to@example.com','to2@example.com'),
            'Cc':('cc@example.com',),
            'Bcc':('bcc@example.com',),
            'Subject':'Hello out there',
            'X-Mailer':'MailTemplates',
            }
            )

        self.MailHost.checkSent()

    def testSendParametersOverrideHeadersDictOverridesProperties(self):
        self.test_add('Test Body')
        self.MailHost.setExpected(mfrom='from@example.com',
                                  mto=('to@example.com','to2@example.com',
                                       'cc@example.com', 'bcc@example.com'),
                                  filename='mail_SendHeaders2.txt')
        for name,type,value in (
            ('mfrom','string','from@example.com'),
            ('mto','string','frog@example.com'),
            ('mcc','lines',('cc@example.com',)),
            ('mbcc','lines',('bcc@example.com',)),
            ('subject','string','Hello %s there'),
            ('headers','lines',(
                'X-Mailer: MailTemplates',
                'X-Mailer2: MailTemplatesBad',
                ))
            ):
            self.mt.manage_addProperty(name,value,type)

        self.mt.send(subject=self.mt.subject % 'out',
                     headers={
            'To':('to@example.com','to2@example.com'),
            'Subject':'cheese',
            'X-Mailer2':'MailTemplates',
            })

        self.MailHost.checkSent()

    def testSendParametersGoToOptions(self):
        self.test_add('Test <tal:x replace="options/body"/>')
        self.MailHost.setExpected(mfrom='from@example.com',
                                  mto=('to@example.com','to2@example.com',
                                       'cc@example.com', 'bcc@example.com'),
                                  filename='mail_SendSimple.txt')
        for name,type,value in (
            ('mfrom','string','from@example.com'),
            ('mto','string','frog@example.com'),
            ('mcc','lines',('cc@example.com',)),
            ('mbcc','lines',('bcc@example.com',)),
            ('subject','string','Hello %s there'),
            ):
            self.mt.manage_addProperty(name,value,type)

        self.mt.send(subject=self.mt.subject % 'out',
                     headers={
            'To':('to@example.com','to2@example.com'),
            'Subject':'cheese',
            },
                     body='Body')

        self.MailHost.checkSent()

    def testPropertiesParametersAndSubstitution(self):
        self.test_add('Test Body')
        self.MailHost.setExpected(mfrom='from@example.com',
                                  mto=('to@example.com', 'to2@example.com',
                                       'cc@example.com', 'bcc@example.com'),
                                  filename='mail_SendSimple.txt')
        for name,type,value in (
            ('mfrom','string','from@example.com'),
            ('mto','string','to@example.com, to2@example.com'),
            ('mcc','lines',('cc@example.com',)),
            ('mbcc','lines',('bcc@example.com',)),
            ('subject','string','Hello %s there'),
            ):
            self.mt.manage_addProperty(name,value,type)

        self.mt.send(subject=self.mt.subject % 'out')

        self.MailHost.checkSent()

    def testGetMessage(self):
        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEText import MIMEText

        self.test_add('Test <tal:x replace="options/body"/>')
        self.MailHost.setExpected(mfrom='from@example.com',
                                  mto=('to@example.com','to2@example.com'),
                                  filename='mail_SendAttachment.txt')
        for name,type,value in (
            ('mfrom','string','from@example.com'),
            ('mto','string','frog@example.com'),
            ('mcc','lines',('cc@example.com',)),
            ('mbcc','lines',('bcc@example.com',)),
            ('subject','string','Hello %s there'),
            ):
            self.mt.manage_addProperty(name,value,type)

        msg = self.mt.as_message(subject=self.mt.subject % 'out',
                                 headers={
            'To':('to@example.com','to2@example.com'),
            'Subject':'cheese',
            },
                                 body='Body',
                                 boundary='111',
                                 subtype='alternative')

        self.assertTrue(isinstance(msg,MIMEMultipart))
        attachment = MIMEText('A Test Attachment',_subtype='plain')
        attachment.add_header('Content-Disposition', 'attachment', filename='test.txt')
        msg.attach(attachment)
        msg.send()

        self.MailHost.checkSent()

    def _addFileSetup(self):
        from email.MIMEMultipart import MIMEMultipart

        self.test_add('Test <tal:x replace="options/body"/>')
        self.MailHost.setExpected(mfrom='from@example.com',
                                  mto=('to@example.com','to2@example.com'),
                                  filename='mail_SendFile.txt')
        for name,type,value in (
            ('mfrom','string','from@example.com'),
            ('mto','string','frog@example.com'),
            ('mcc','lines',('cc@example.com',)),
            ('mbcc','lines',('bcc@example.com',)),
            ('subject','string','Hello %s there'),
            ):
            self.mt.manage_addProperty(name,value,type)

        msg = self.mt.as_message(subject=self.mt.subject % 'out',
                                 headers={
            'To':('to@example.com','to2@example.com'),
            'Subject':'cheese',
            },
                                 body='Body',
                                 boundary='111',
                                 subtype='alternative')

        self.assertTrue(isinstance(msg,MIMEMultipart))
        return msg

    def testZopeFileObject(self):
        self.app.manage_addFile('test.txt',
                                'A Test Attachment')
        msg = self._addFileSetup()
        msg.add_file(self.app['test.txt'])
        msg.send()

        self.MailHost.checkSent()

    def testPythonFileObject(self):
        msg = self._addFileSetup()
        msg.add_file(open(
            os.path.join(test_folder,'test.txt')
            ))
        msg.send()

        self.MailHost.checkSent()

    def testFileUploadObject(self):
        msg = self._addFileSetup()
        msg.add_file(self.makeFileUpload(
            value='A Test Attachment'
            ))
        msg.send()

        self.MailHost.checkSent()

    def testStringWithContentType(self):
        msg = self._addFileSetup()
        msg.add_file(
            data=open(
            os.path.join(test_folder,'test.txt')
            ).read(),
            filename='test.txt',
            content_type='text/plain'
            )
        msg.send()

        self.MailHost.checkSent()

    def testStringWithoutContentType(self):
        msg = self._addFileSetup()
        msg.add_file(
            data=open(
            os.path.join(test_folder,'test.txt')
            ).read(),
            filename='test.txt'
            )
        msg.send()

        self.MailHost.checkSent()

    def testTooManyParameters(self):
        msg = self._addFileSetup()
        self.assertRaises(
            TypeError,
            msg.add_file,
            self.makeFileUpload(
            value='A Test Attachment'
            ),
            data=open(
            os.path.join(test_folder,'test.txt')
            ).read(),
            filename='test.txt',
            content_type='text/plain'
            )

    def testTooFewParameters(self):
        msg = self._addFileSetup()
        self.assertRaises(
            TypeError,
            msg.add_file
            )

    def testDataWithoutFilename(self):
        msg = self._addFileSetup()
        self.assertRaises(
            TypeError,
            msg.add_file,
            data=open(
            os.path.join(test_folder,'test.txt')
            ).read(),
            content_type='text/plain'
            )

    def testFilenameWithoutData(self):
        msg = self._addFileSetup()
        self.assertRaises(
            TypeError,
            msg.add_file,
            filename='test.txt',
            content_type='text/plain'
            )

    def testCallAliasesSend(self):
        self.test_add('Test Body')
        self.MailHost.setExpected(mfrom='from@example.com',
                                  mto=('to@example.com',),
                                  filename='mail_SendSimpleSomeHeaders.txt')
        self.mt(
            mfrom='from@example.com',
            mto=('to@example.com',),
            subject='Test Subject'
            )

        self.MailHost.checkSent()

    def test_encoded_not_html_mode(self):
        self.MailHost.setExpected(mfrom='from@example.com',
                                  mto=('to@example.com',),
                                  filename='mail_unicode.txt')
        self.test_add('Test <tal:x replace="options/unicode"/>')
        # we get a unicode error here because we're trying to
        # use an encoded string in a non-html-mode page template.
        # It should have been decoded first.
        self.assertRaises(
            UnicodeDecodeError,
            self.mt,
            mfrom='from@example.com',
            mto=('to@example.com',),
            subject='Test Subject',
            unicode=u'£££'.encode('utf-8'),
            encoding='utf-8'
            )

    def test_encoded_html_mode(self):
        self.MailHost.setExpected(mfrom='from@example.com',
                                  mto=('to@example.com',),
                                  filename='mail_unicode2.txt')
        self.test_add('')
        self.mt.pt_edit('Test <tal:x replace="options/unicode"/>',
                        'text/html')

        self.mt(
            mfrom='from@example.com',
            mto=('to@example.com',),
            subject='Test Subject',
            unicode=u'£££'.encode('utf-8'),
            encoding='utf-8'
            )

    def test_unicode_not_html_mode(self):
        self.MailHost.setExpected(mfrom='from@example.com',
                                  mto=('to@example.com',),
                                  filename='mail_unicode.txt')
        self.test_add('Test <tal:x replace="options/unicode"/>')
        self.mt(
            mfrom='from@example.com',
            mto=('to@example.com',),
            subject='Test Subject',
            unicode=u'£££',
            encoding='utf-8'
            )

    def test_unicode_html_mode(self):
        self.MailHost.setExpected(mfrom='from@example.com',
                                  mto=('to@example.com',),
                                  filename='mail_unicode2.txt')
        self.test_add('')
        self.mt.pt_edit('Test <tal:x replace="options/unicode"/>',
                        'text/html')

        # We get a unicode error here because we're trying to
        # insert a unicode into an html-mode template.
        # It should have been encoded first.
        self.assertRaises(
            UnicodeEncodeError,
            self.mt,
            mfrom='from@example.com',
            mto=('to@example.com',),
            subject='Test Subject',
            unicode=u'£££',
            encoding='utf-8'
            )

    def test_example1(self):
        # login
        noSecurityManager()
        self.app.aq_chain[-1].id = 'testing'
        newSecurityManager(
            None,
            SimpleUser('Test User','',('Manager',),[]).__of__(self.app)
            )
        try:
            # setup
            self.r.form['file']=self.makeFileUpload(diskname='example1.mt')
            self.app.manage_addProduct['MailTemplates'].addMailTemplate(
                id='my_mt',
                mailhost='MailHost',
                REQUEST=self.r
                )
            self.r.form['file']=self.makeFileUpload(diskname='example1.py')
            self.app.manage_addProduct['PythonScripts'].manage_addPythonScript(
                id='test_mt',
                REQUEST=self.r
                )
            # set expected
            self.MailHost.setExpected(mfrom='webmaster@example.com',
                                      mto=('user@example.com',),
                                      filename='example1.txt')
            # test
            self.assertEqual(self.app.test_mt(),'Mail Sent!')
            self.MailHost.checkSent()
        finally:
            # logout
            noSecurityManager()
            newSecurityManager( None, SystemUser )

    def test_example3(self):
        # login
        noSecurityManager()
        self.app.aq_chain[-1].id = 'testing'
        newSecurityManager(
            None,
            SimpleUser('Test User','',('Manager',),[]).__of__(self.app)
            )
        try:
            # setup
            self.r.form['file']=self.makeFileUpload(diskname='example3.mt')
            self.app.manage_addProduct['MailTemplates'].addMailTemplate(
                id='my_mt',
                mailhost='MailHost',
                REQUEST=self.r
                )
            self.app.manage_addFile(
                id='myfile.bin',
                file=self.makeFileUpload(diskname='example3.bin')
                )
            self.r.form['file']=self.makeFileUpload(diskname='example3.py')
            self.app.manage_addProduct['PythonScripts'].manage_addPythonScript(
                id='send_mail',
                REQUEST=self.r
                )
            # set expected
            self.MailHost.setExpected(mfrom='from@example.com',
                                      mto='to1@example.com',
                                      filename='example3.txt')
            # test
            self.assertEqual(self.app.send_mail(),'Mail Sent!')
            self.MailHost.checkSent()
        finally:
            # logout
            noSecurityManager()
            newSecurityManager( None, SystemUser )

    def test_example4(self):
        # login
        noSecurityManager()
        self.app.aq_chain[-1].id = 'testing'
        newSecurityManager(
            None,
            SimpleUser('Test User','',('Manager',),[]).__of__(self.app)
            )
        try:
            # setup
            self.r.form['file']=self.makeFileUpload(diskname='example4.mt')
            self.app.manage_addProduct['MailTemplates'].addMailTemplate(
                id='my_mt',
                mailhost='MailHost',
                REQUEST=self.r
                )
            self.app.my_mt.manage_addProperty(
                'subject','Welcome to %s','string'
                )
            self.app.my_mt.manage_addProperty(
                'mfrom','webmaster@example.com','string'
                )
            self.r.form['file']=self.makeFileUpload(diskname='example4.py')
            self.app.manage_addProduct['PythonScripts'].manage_addPythonScript(
                id='send_mail',
                REQUEST=self.r
                )
            # set expected
            self.MailHost.setExpected(mfrom='webmaster@example.com',
                                      mto=('user@example.com',),
                                      filename='example4.txt')
            # test
            self.assertEqual(self.app.send_mail(),'Mail Sent!')
            self.MailHost.checkSent()
        finally:
            # logout
            noSecurityManager()
            newSecurityManager( None, SystemUser )

def test_suite():
    return TestSuite((
        makeSuite(TestMailTemplate),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')

