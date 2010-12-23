# -*- coding: utf-8 -*-
from Testing import ZopeTestCase

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase

class TransformTestCase(ATSiteTestCase):
    
    def afterSetUp(self):
        ATSiteTestCase.afterSetUp(self)
        self.transforms = self.portal.portal_transforms


class TestIntelligentTextToHtml(TransformTestCase):

    def performTransform(self, orig, targetMimetype = 'text/html', mimetype='text/x-web-intelligent'):
        return self.transforms.convertTo(targetMimetype, orig, context=self.portal, mimetype=mimetype).getData()
    
    def testHyperlinks(self):
        orig = "A test http://test.com"
        new = self.performTransform(orig)
        self.assertEqual(new, 'A test <a href="http://test.com" rel="nofollow">http://test.com</a>')

    def testMailto(self):
        orig = "A test test@test.com of mailto"
        new = self.performTransform(orig)
        self.assertEqual(new, 'A test <a href="&#0109;ailto&#0058;test&#0064;test.com">test&#0064;test.com</a> of mailto')
    
    def testTextAndLinks(self):
        orig = """A test
URL: http://test.com End
Mail: test@test.com End
URL: http://foo.com End"""
        new = self.performTransform(orig)
        self.assertEqual(new, 'A test<br />' \
                              'URL: <a href="http://test.com" rel="nofollow">http://test.com</a> End<br />' \
                              'Mail: <a href="&#0109;ailto&#0058;test&#0064;test.com">test&#0064;test.com</a> End<br />' \
                              'URL: <a href="http://foo.com" rel="nofollow">http://foo.com</a> End')
                              
    def testTextAndLinksAtEndOfLine(self):
        orig = """A test
URL: http://test.com
Mail: test@test.com
URL: http://foo.com"""
        new = self.performTransform(orig)
        self.assertEqual(new, 'A test<br />' \
                              'URL: <a href="http://test.com" rel="nofollow">http://test.com</a><br />' \
                              'Mail: <a href="&#0109;ailto&#0058;test&#0064;test.com">test&#0064;test.com</a><br />' \
                              'URL: <a href="http://foo.com" rel="nofollow">http://foo.com</a>')
        
        
    def testIndents(self):
        orig = """A test
  URL: http://test.com
    Mail: test@test.com
      URL: http://foo.com"""
        new = self.performTransform(orig)
        self.assertEqual(new, 'A test<br />' \
                              '&nbsp;&nbsp;URL: <a href="http://test.com" rel="nofollow">http://test.com</a><br />' \
                              '&nbsp;&nbsp;&nbsp;&nbsp;Mail: <a href="&#0109;ailto&#0058;test&#0064;test.com">test&#0064;test.com</a><br />' \
                              '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;URL: <a href="http://foo.com" rel="nofollow">http://foo.com</a>')

    
    def testEntities(self):
        orig = "Some & funny < characters"
        new = self.performTransform(orig)
        self.assertEqual(new, "Some &amp; funny &lt; characters")
        
        
    def testAccentuatedCharacters(self):
        orig = "The French use é à ô ù à and ç"
        new = self.performTransform(orig)
        self.assertEqual(new, "The French use &eacute; &agrave; &ocirc; &ugrave; &agrave; and &ccedil;")

class TestHtmlToIntelligentText(TransformTestCase):

    def performTransform(self, orig, targetMimetype = 'text/x-web-intelligent', mimetype='text/html'):
        return self.transforms.convertTo(targetMimetype, orig, context=self.portal, mimetype=mimetype).getData()

    def testStripTags(self):
        orig = "Some <b>bold</b> text."
        new = self.performTransform(orig)
        self.assertEqual(new, "Some bold text.")
    
    def testBreaks(self):
        orig = "Some<br/>broken<BR/>text<br />"
        new = self.performTransform(orig)
        self.assertEqual(new, "Some\nbroken\ntext\n")
    
    def testStartBlocks(self):
        orig = "A block<dt>there</dt>"
        new = self.performTransform(orig)
        self.assertEqual(new, "A block\n\nthere")
    
    def testEndBlocks(self):
        orig = "<p>Paragraph</p>Other stuff"
        new = self.performTransform(orig)
        self.assertEqual(new, "Paragraph\n\nOther stuff")
        
    def testIndentBlocks(self):
        orig = "A<blockquote>Indented blockquote</blockquote>"
        new = self.performTransform(orig)
        self.assertEqual(new, "A\n\n  Indented blockquote")
    
    def testListBlocks(self):
        orig = "A list<ul><li>Foo</li><li>Bar</li></ul>"
        new = self.performTransform(orig)
        self.assertEqual(new, "A list\n\n  - Foo\n\n  - Bar\n\n")
        
    def testNbsp(self):
        orig = "Some space &nbsp;&nbsp;here"
        new = self.performTransform(orig)
        self.assertEqual(new, "Some space   here")
        
    def testAngles(self):
        orig = "Watch &lt;this&gt; and &lsaquo;that&rsaquo;"
        new = self.performTransform(orig)
        self.assertEqual(new, "Watch <this> and &#8249;that&#8250;")
    
    def testBullets(self):
        orig = "A &bull; bullet"
        new = self.performTransform(orig)
        self.assertEqual(new, "A &#8226; bullet")
        
    def testAmpersands(self):
        orig = "An &amp; ampersand"
        new = self.performTransform(orig)
        self.assertEqual(new, "An & ampersand")
        
    def testEntities(self):
        orig = "A &mdash; dash"
        new = self.performTransform(orig)
        self.assertEqual(new, "A &#8212; dash")
        
    def testPre(self):
        orig = "A <pre>  pre\n  section</pre>"
        new = self.performTransform(orig)
        self.assertEqual(new, "A \n\n  pre\n  section\n\n")
        
    def testWhitespace(self):
        orig = "A \n\t spaceful, <b>  tag-filled</b>, <b> <i>  snippet\n</b></i>"
        new = self.performTransform(orig)
        self.assertEqual(new, "A spaceful, tag-filled, snippet ")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestIntelligentTextToHtml))
    suite.addTest(makeSuite(TestHtmlToIntelligentText))
    return suite
