"""
"""
import os, sys
if __name__ == '__main__':
   execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase


class TestXSSFilter(ATSiteTestCase):

   def afterSetUp(self):
       ATSiteTestCase.afterSetUp(self)
       self.engine = self.portal.portal_transforms

   def doTest(self, data_in, data_out):
       html = self.engine.convertTo('text/x-html-safe', data_in, mimetype="text/html")
       self.assertEqual (data_out,html.getData())

   def test_1(self):
       data_in = """<html><body><img src="javascript:Alert('XSS');" /></body></html>"""
       data_out = """<img />"""
       self.doTest(data_in, data_out)

   def test_2(self):
       data_in = """<img src="javascript:Alert('XSS');" />"""
       data_out = """<img />"""
       self.doTest(data_in, data_out)

   def test_3(self):
       data_in = """<html><body><IMG SRC=&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;></body></html>"""
       data_out = """<img />"""
       self.doTest(data_in, data_out)

   def test_4(self):
       data_in = """<IMG SRC=&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;>"""
       data_out = """<img />"""

       self.doTest(data_in, data_out)

   def test_5(self):
       data_in = """<img src="jav
       asc
       ript:Alert('XSS');" />"""
       data_out = """<img />"""
       self.doTest(data_in, data_out)


   def test_6(self):
       data_in = """<img src="jav asc ript:Alert('XSS');"/>"""
       data_out = """<img />"""
       self.doTest(data_in, data_out)

   def test_7(self):
       data_in = """<a href=&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;>test med a-tag</a>"""
       data_out = """<a>test med a-tag</a>"""
       self.doTest(data_in, data_out)

   def test_8(self):
       data_in = """<div style="bacground:url(jav asc ript:Alert('XSS')">test</div>"""
       data_out = """<div>test</div>"""
       self.doTest(data_in, data_out)

   def test_9(self):
       data_in = """<div style="bacground:url(jav
       asc
       ript:
       Alert('XSS')">test</div>"""
       data_out = """<div>test</div>"""
       self.doTest(data_in, data_out)

   def test_10(self):
       data_in = """<div style="bacground:url(&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;">test</div>"""
       data_out = """<div>test</div>"""
       self.doTest(data_in, data_out)

   def test_11(self):
       data_in = """<div style="bacground:url(v b  sc  ript:msgbox('XSS')">test</div>"""
       data_out = """<div>test</div>"""
       self.doTest(data_in, data_out)

   def test_12(self):
       data_in = """<img src="vbscript:msgbox('XSS')"/>"""
       data_out = """<img />"""
       self.doTest(data_in, data_out)

   def test_13(self):
       data_in = """<img src="vb
       sc
       ript:msgbox('XSS')"/>"""
       data_out = """<img />"""
       self.doTest(data_in, data_out)

   def test_14(self):
       data_in = """<a href="vbscript:Alert('XSS')">test</a>"""
       data_out = """<a>test</a>"""
       self.doTest(data_in, data_out)

   def test_15(self):
       data_in = """<div STYLE="width: expression(window.location='http://www.dr.dk';);">div</div>"""
       data_out = """<div>div</div>"""
       self.doTest(data_in, data_out)

   def test_16(self):
       data_in = """<div STYLE="width: ex pre ss   io n(window.location='http://www.dr.dk';);">div</div>"""
       data_out = """<div>div</div>"""
       self.doTest(data_in, data_out)

   def test_17(self):
       data_in = """<div STYLE="width: ex
       pre
       ss
       io
       n(window.location='http://www.dr.dk';);">div</div>"""
       data_out = """<div>div</div>"""
       self.doTest(data_in, data_out)

   def test_18(self):
       data_in = """<div style="width: 14px;">div</div>"""
       data_out = data_in
       self.doTest(data_in, data_out)

   def test_19(self):
       data_in = """<a href="http://www.headnet.dk">headnet</a>"""
       data_out = data_in
       self.doTest(data_in, data_out)

   def test_20(self):
       data_in = """<img src="http://www.headnet.dk/log.jpg" />"""
       data_out = data_in
       self.doTest(data_in, data_out)

   def test_21(self):
       data_in = """<mustapha name="mustap" tlf="11 11 11 11" address="unknown">bla bla bla</mustapha>"""
       data_out = """bla bla bla"""
       self.doTest(data_in, data_out)

   def test_22(self):
       data_in = '<<frame></frame>script>alert("XSS");<<frame></frame>/script>'
       data_out = '&lt;script&gt;alert("XSS");&lt;/script&gt;'
       self.doTest(data_in, data_out)

def test_suite():
   from unittest import TestSuite, makeSuite
   suite = TestSuite()
   suite.addTest(makeSuite(TestXSSFilter))
   return suite

if __name__ == '__main__':
   framework()
