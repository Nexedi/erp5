from Products.PortalTransforms.libtransforms.imagemagick_transform import ImageMagickTransforms

class image_to_png(ImageMagickTransforms):
    __name__  = "image_to_png"
    inputs    = ('image/*', )
    output   = 'image/png'
    format  = 'png'

def register():
    return image_to_png()
