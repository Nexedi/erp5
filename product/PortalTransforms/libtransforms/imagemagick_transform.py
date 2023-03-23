from Products.PortalTransforms.interfaces import ITransform
import os
import subprocess
from zope.interface import implementer


@implementer(ITransform)
class ImageMagickTransforms:
    __name__  = "imagemagick_transforms"
    def __init__(self, name=None):
         if name is not None:
            self.__name__ = name

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        parameter_list = ['convert']
        parameter_list.append('-')
        newwidth = kwargs.get('width','')
        newheight = kwargs.get('height','')
        if newwidth and newheight:
            parameter_list.extend(['-resize', '%sx%s!' % (newwidth, newheight)])
        elif newwidth or newheight:
            parameter_list.extend(['-resize', '%sx%s' % (newwidth, newheight)])
        depth = kwargs.get('depth','')
        if depth:
            parameter_list.extend(['-depth', '%s' % depth, '-type', 'Palette'])
        parameter_list.append('%s:-' % self.format)
        env = os.environ.copy()
        env.update({'LC_NUMERIC':'C'})
        p = subprocess.Popen(parameter_list,
                             env=env,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             close_fds=True)
        try:
            image, err = p.communicate(bytes(orig))
        finally:
            del p

        data.setData(image)
        return data

def register():
    return ImageMagickTransforms()
