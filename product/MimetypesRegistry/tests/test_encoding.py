import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase

from Products.MimetypesRegistry.encoding import guess_encoding

class TestGuessEncoding(ATSiteTestCase):

    def testUTF8(self):
        e = guess_encoding('\xef\xbb\xbf any UTF-8 data')
        self.failUnlessEqual(e, 'UTF-8')
        e = guess_encoding(' any UTF-8 data \xef\xbb\xbf')
        self.failUnlessEqual(e, None)

    def testEmacs(self):
        e = guess_encoding('# -*- coding: UTF-8  -*-')
        self.failUnlessEqual(e, 'UTF-8')
        e = guess_encoding('''
        ### -*- coding: ISO-8859-1  -*-
        ''')
        self.failUnlessEqual(e, 'ISO-8859-1')
        e = guess_encoding('''

        ### -*- coding: ISO-8859-1  -*-
        ''')
        self.failUnlessEqual(e, None)

    def testVim(self):
        e = guess_encoding('# vim:fileencoding=UTF-8')
        self.failUnlessEqual(e, 'UTF-8')
        e = guess_encoding('''
        ### vim:fileencoding=ISO-8859-1
        ''')
        self.failUnlessEqual(e, 'ISO-8859-1')
        e = guess_encoding('''

        ### vim:fileencoding= ISO-8859-1
        ''')
        self.failUnlessEqual(e, None)

    def testXML(self):
        e = guess_encoding('<?xml?>')
        self.failUnlessEqual(e, 'UTF-8')
        e = guess_encoding('''<?xml version="1.0" encoding="ISO-8859-1" ?>
        ''')
        self.failUnlessEqual(e, 'ISO-8859-1')
        e = guess_encoding('''<?xml version="1.0" encoding="ISO-8859-1"?>
        ''')
        self.failUnlessEqual(e, 'ISO-8859-1')
        e = guess_encoding('''<?xml version="1.0" encoding="ISO-8859-1"?><truc encoding="UTF-8">
        </truc>
        ''')
        self.failUnlessEqual(e, 'ISO-8859-1')

    def testHTML(self):
        e = guess_encoding('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
<title>ASPN : Python Cookbook : Auto-detect XML encoding</title>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
    <meta name="robots" content="all" />
    <meta name="description" content="ActiveState Open Source Programming tools for Perl Python XML xslt scripting with free trials. Quality development tools for programmers systems administrators database administrators network administrators and webmasters" />
    <meta name="keywords" content="ActiveState,Perl,xml,xslt,mozilla,Open Source,Python,Perl for Win32,resources,PerlScript,ActivePerl,Programming,Programmers,Integrated,Development,Environment,SOAP,Linux,Solaris,Web,development,tools,free,software,download,support,Perl Resource Kit,System Administration,Sys Admin,WinNT,SQL,Oracle,Email,XML,Linux,Programming,perl,NT,2000,windows,Unix,Software,Security,   Administration,systems,windows,database,database,consulting,support,Microsoft,developer,resource,code,tutorials,IDE,Integrated development environment,developer,resources,tcl,php" />

<link rel="stylesheet" href="/ASPN/aspn.css" />

</head>

<body bgcolor="#FFFFFF" leftmargin="0" topmargin="0" marginwidth="0" marginheight="0">
charset=utf-8
</body>
</html> ''')
        self.failUnlessEqual(e, 'iso-8859-1')


    def test_broken_percent(self):
        e = guess_encoding(
r"""<pre>
&lt;metal:block tal:define="dummy python:
request.RESPONSE.setHeader('Content-Type',
'text/html;;charset=%s' % charset)" /&gt;
&lt;metal:block tal:define="dummy
python:request.RESPONSE.setHeader('Content-Language', lang)"
/
&gt;
</pre>
"""
    )
        # unable to detect a valid encoding
        self.failUnlessEqual(e, None) 


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGuessEncoding))
    return suite

if __name__ == '__main__':
    framework()
