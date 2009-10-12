from Products.PortalTransforms.interfaces import itransform
import subprocess
from zope.interface import implements


class ImageMagickTransforms:
    implements(itransform)
    __name__  = "imagemagick_transforms"
    def __init__(self, name=None):
         if name is not None:
            self.__name__ = name

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        parameter_list = ['convert']
        newwidth = kwargs.get('width','')
        newheight = kwargs.get('height','')
        if newwidth and newheight:
            parameter_list.extend('-resize', '%sx%s!' % (newwidth, newheight))
        elif newwidth or newheight:
            parameter_list.extend('-resize', '%sx%s' % (newwidth, newheight))
        parameter_list.append('-')
        parameter_list.append('%s:-' % self.format)
        process = subprocess.Popen(parameter_list,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   close_fds=True)
        imgin, imgout, err = process.stdin, process.stdout, process.stderr

        def writeData(stream, data):
          if isinstance(data, str):
            stream.write(data)
          else:
            # Use PData structure to prevent
            # consuming too much memory
            while data is not None:
              stream.write(data.data)
              data = data.next

        writeData(imgin, orig)
        imgin.close()
        data.setData(imgout.read())
        return data

def register():
    return ImageMagickTransforms()
