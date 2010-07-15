# -*- coding: utf-8 -*-
from Products.PortalTransforms.libtransforms.imagemagick_transform import ImageMagickTransforms

class pdf_to_png(ImageMagickTransforms):
    __name__  = "pdf_to_png"
    inputs    = ('application/pdf', )
    output   = 'image/png'
    format  = 'png'

def register():
    return pdf_to_png()
