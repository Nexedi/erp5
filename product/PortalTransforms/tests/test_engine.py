
from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase

from zope.interface import implementer
from Products.PortalTransforms.utils import TransformException
from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.chain import chain

import urllib.request, urllib.parse, urllib.error
import re

class BaseTransform:
    def name(self):
        return getattr(self, '__name__', self.__class__.__name__)


@implementer(ITransform)
class HtmlToText(BaseTransform):
    inputs = ('text/html',)
    output = 'text/plain'

    def __call__(self, orig, **kwargs):
        orig = re.sub('<[^>]*>(?i)(?m)', '', orig)
        return urllib.parse.unquote(re.sub('\n+', '\n', orig)).strip()

    def convert(self, orig, data, **kwargs):
        orig = self.__call__(orig)
        data.setData(orig)
        return data

class HtmlToTextWithEncoding(HtmlToText):
    output_encoding = 'ascii'

@implementer(ITransform)
class FooToBar(BaseTransform):
    inputs = ('text/*',)
    output = 'text/plain'

    def __call__(self, orig, **kwargs):
        orig = re.sub('foo', 'bar', orig)
        return urllib.parse.unquote(re.sub('\n+', '\n', orig)).strip()

    def convert(self, orig, data, **kwargs):
        orig = self.__call__(orig)
        data.setData(orig)
        return data

@implementer(ITransform)
class DummyHtmlFilter1(BaseTransform):
    __name__ = 'dummy_html_filter1'
    inputs = ('text/html',)
    output = 'text/html'

    def convert(self, orig, data, **kwargs):
        data.setData("<span class='dummy'>%s</span>" % orig)
        return data

@implementer(ITransform)
class DummyHtmlFilter2(BaseTransform):
    __name__ = 'dummy_html_filter2'
    inputs = ('text/html',)
    output = 'text/html'

    def convert(self, orig, data, **kwargs):
        data.setData("<div class='dummy'>%s</div>" % orig)
        return data


class QuxToVHost(DummyHtmlFilter1):
    __name__ = 'qux_to_vhost'

    def convert(self, orig, data, context, **kwargs):
        data.setData(re.sub('qux', context.REQUEST['SERVER_URL'], orig))
        return data


@implementer(ITransform)
class TransformNoIO(BaseTransform):
    pass

class BadTransformMissingImplements(BaseTransform):
    #__implements__ = None
    inputs = ('text/*',)
    output = 'text/plain'

@implementer(ITransform)
class BadTransformBadMIMEType1(BaseTransform):
    inputs = ('truc/muche',)
    output = 'text/plain'

@implementer(ITransform)
class BadTransformBadMIMEType2(BaseTransform):
    inputs = ('text/plain',)
    output = 'truc/muche'

@implementer(ITransform)
class BadTransformNoInput(BaseTransform):
    inputs = ()
    output = 'text/plain'

@implementer(ITransform)
class BadTransformWildcardOutput(BaseTransform):
    inputs = ('text/plain',)
    output = 'text/*'

class TestEngine(ATSiteTestCase):

    def afterSetUp(self):
        ATSiteTestCase.afterSetUp(self)
        self.engine = self.portal.portal_transforms
        self.data = '<b>foo</b>'

    def register(self):
        #A default set of transforms to prove the interfaces work
        self.engine.registerTransform(HtmlToText())
        self.engine.registerTransform(FooToBar())

    def testRegister(self):
        self.register()

    def testFailRegister(self):
        register = self.engine.registerTransform
        self.assertRaises(TransformException, register, TransformNoIO())
        self.assertRaises(TransformException, register, BadTransformMissingImplements())
        self.assertRaises(TransformException, register, BadTransformBadMIMEType1())
        self.assertRaises(TransformException, register, BadTransformBadMIMEType2())
        self.assertRaises(TransformException, register, BadTransformNoInput())
        self.assertRaises(TransformException, register, BadTransformWildcardOutput())

    def testCall(self):
        self.register()
        data = self.engine('HtmlToText', self.data)
        self.assertEqual(data, "foo")

        data = self.engine('FooToBar', self.data)
        self.assertEqual(data, "<b>bar</b>")

    def testConvert(self):
        self.register()

        data = self.engine.convert('HtmlToText', self.data)
        self.assertEqual(data.getData(), "foo")
        self.assertEqual(data.getMetadata()['mimetype'], 'text/plain')
        self.assertEqual(data.getMetadata().get('encoding'), None)
        self.assertEqual(data.name(), "HtmlToText")

        self.engine.registerTransform(HtmlToTextWithEncoding())
        data = self.engine.convert('HtmlToTextWithEncoding', self.data)
        self.assertEqual(data.getMetadata()['mimetype'], 'text/plain')
        self.assertEqual(data.getMetadata()['encoding'], 'ascii')
        self.assertEqual(data.name(), "HtmlToTextWithEncoding")

    def testConvertTo(self):
        self.register()

        data = self.engine.convertTo('text/plain', self.data, mimetype="text/html")
        self.assertEqual(data.getData(), "foo")
        self.assertEqual(data.getMetadata()['mimetype'], 'text/plain')
        self.assertEqual(data.getMetadata().get('encoding'), None)
        self.assertEqual(data.name(), "text/plain")

        self.engine.unregisterTransform('HtmlToText')
        self.engine.unregisterTransform('FooToBar')
        self.engine.registerTransform(HtmlToTextWithEncoding())
        data = self.engine.convertTo('text/plain', self.data, mimetype="text/html")
        self.assertEqual(data.getMetadata()['mimetype'], 'text/plain')
        # HtmlToTextWithEncoding. Now None is the right
        #self.assertEqual(data.getMetadata()['encoding'], 'ascii')
        # XXX the new algorithm is choosing html_to_text instead of
        self.assertEqual(data.getMetadata()['encoding'], None)
        self.assertEqual(data.name(), "text/plain")

    def testChain(self):
        self.register()
        hb = chain('hbar')
        hb.registerTransform(HtmlToText())
        hb.registerTransform(FooToBar())

        self.engine.registerTransform(hb)
        cache = self.engine.convert('hbar', self.data)
        self.assertEqual(cache.getData(), "bar")
        self.assertEqual(cache.name(), "hbar")

    def testPolicy(self):
        mt = 'text/x-html-safe'
        data = '<script>this_is_unsafe();</script><p>this is safe</p>'

        cache = self.engine.convertTo(mt, data, mimetype='text/html')
        self.assertEqual(cache.getData(), '<p>this is safe</p>')

        self.engine.registerTransform(DummyHtmlFilter1())
        self.engine.registerTransform(DummyHtmlFilter2())
        required = ['dummy_html_filter1', 'dummy_html_filter2']

        self.engine.manage_addPolicy(mt, required)
        expected_policy = [('text/x-html-safe',
                            ('dummy_html_filter1', 'dummy_html_filter2'))]
        self.assertEqual(self.engine.listPolicies(), expected_policy)

        cache = self.engine.convertTo(mt, data, mimetype='text/html')
        self.assertEqual(cache.getData(), '<div class="dummy"><span class="dummy"><p>this is safe</p></span></div>')

        self.assertEqual(cache.getMetadata()['mimetype'], mt)
        self.assertEqual(cache.name(), mt)

        path = self.engine._findPath('text/html', mt, required)
        self.assertEqual(str(path),
                             "[<Transform at dummy_html_filter1>, "
                             "<Transform at dummy_html_filter2>, "
                             "<Transform at safe_html>]")

    def testSame(self):
        data = "This is a test"
        mt = "text/plain"
        out = self.engine.convertTo('text/plain', data, mimetype=mt)
        self.assertEqual(out.getData(), data)
        self.assertEqual(out.getMetadata()['mimetype'], 'text/plain')

    def testCache(self):
        data = "This is a test"
        other_data = 'some different data'
        mt = "text/plain"
        self.engine.max_sec_in_cache = 20
        out = self.engine.convertTo(mt, data, mimetype=mt, object=self)
        self.assertEqual(out.getData(), data, out.getData())
        out = self.engine.convertTo(mt, other_data, mimetype=mt, object=self)
        self.assertEqual(out.getData(), data, out.getData())
        self.engine.max_sec_in_cache = -1
        out = self.engine.convertTo(mt, data, mimetype=mt, object=self)
        self.assertEqual(out.getData(), data, out.getData())
        out = self.engine.convertTo(mt, other_data, mimetype=mt, object=self)
        self.assertEqual(out.getData(), other_data, out.getData())

    def testCacheWithVHost(self):
        """Ensure that the transform cache key includes virtual
        hosting so that transforms which are dependent on the virtual
        hosting don't get invalid data from the cache.  This happens,
        for example, in the resolve UID functionality used by visual
        editors."""
        mt = 'text/x-html-safe'
        self.engine.registerTransform(QuxToVHost())
        required = ['qux_to_vhost']
        self.engine.manage_addPolicy(mt, required)

        data = '<a href="qux">vhost link</a>'

        out = self.engine.convertTo(
            mt, data, mimetype='text/html', object=self.folder,
            context=self.folder)
        self.assertEqual(
            out.getData(), '<a href="http://nohost">vhost link</a>',
            out.getData())

        # Test when object is not a context
        out = self.engine.convertTo(
            mt, data, mimetype='text/html', object=self,
            context=self.folder)
        self.assertEqual(
            out.getData(), '<a href="http://nohost">vhost link</a>',
            out.getData())

        # Change the virtual hosting
        self.folder.REQUEST['SERVER_URL'] = 'http://otherhost'

        out = self.engine.convertTo(
            mt, data, mimetype='text/html', object=self.folder,
            context=self.folder)
        self.assertEqual(
            out.getData(), '<a href="http://otherhost">vhost link</a>',
            out.getData())

        # Test when object is not a context
        out = self.engine.convertTo(
            mt, data, mimetype='text/html', object=self,
            context=self.folder)
        self.assertEqual(
            out.getData(), '<a href="http://otherhost">vhost link</a>',
            out.getData())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestEngine))
    return suite
