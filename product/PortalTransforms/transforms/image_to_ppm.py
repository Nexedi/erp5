from Products.PortalTransforms.libtransforms.imagemagick_transform import ImageMagickTransforms

class image_to_ppm(ImageMagickTransforms):
    __name__  = "image_to_ppm"
    inputs    = ('image/*', )
    output   = 'image/x-portable-pixmap'
    format  = 'ppm'


def register():
    return image_to_ppm()
