from Products.PortalTransforms.interfaces import itransform
from StringIO import StringIO
import PIL.Image

class PILTransforms:
    __implements__ = itransform
    __name__  = "piltransforms"
    def __init__(self, name=None):
         if name is not None:
            self.__name__ = name

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        imgio = StringIO()
        orig = StringIO(orig)
        newwidth = kwargs.get('width',None)
        newheight = kwargs.get('height',None)
        pil_img = PIL.Image.open(orig)
        if(self.format in ['jpeg','ppm']):
            pil_img.draft("RGB", pil_img.size)
            pil_img = pil_img.convert("RGB")
        if(newwidth or newheight):
            pil_img.thumbnail((newwidth,newheight),PIL.Image.ANTIALIAS)
        pil_img.save(imgio,self.format)
        data.setData(imgio.getvalue())
        return data



def register():
    return PILTransforms()
