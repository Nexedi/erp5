"""
Uses the http://www.freewisdom.org/projects/python-markdown/ module to do its handy work

author: Tom Lazar <tom@tomster.org> at the archipelago sprint 2006

"""
import os

from zope.interface import implements

from Products.CMFDefault.utils import bodyfinder

from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.libtransforms.utils import bin_search
from Products.PortalTransforms.libtransforms.utils import sansext
from Products.PortalTransforms.utils import log

try:
    import markdown as markdown_transformer
except ImportError:
    HAS_MARKDOWN = False
    log('markdown_to_html: Could not import python-markdown.')
else:
    HAS_MARKDOWN = True
    

class markdown:
    implements(ITransform)

    __name__ = "markdown_to_html"
    inputs  = ("text/x-web-markdown",)
    output = "text/html"

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        if HAS_MARKDOWN:
            html = markdown_transformer.markdown(orig)
        else:
            html = orig
        data.setData(html)
        return data

def register():
    return markdown()
