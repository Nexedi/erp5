from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements

class image_to_html:
    implements(ITransform)

    __name__  = "image_to_html"
    inputs    = ('image/*', )
    output   = 'text/html'

    def name(self):
        return self.__name__

    def convert(self, data, cache, **kwargs):
        imageName = kwargs.get("image")
        cache.setData('<img src="%s"/>' %imageName)
        return cache
