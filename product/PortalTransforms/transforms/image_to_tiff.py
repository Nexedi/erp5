from Products.PortalTransforms.libtransforms.imagemagick_transform import ImageMagickTransforms

class image_to_tiff(ImageMagickTransforms):
    __name__  = "image_to_tiff"
    inputs    = ('image/*', )
    output   = 'image/tiff'
    format  = 'tiff'


def register():
    return image_to_tiff()
