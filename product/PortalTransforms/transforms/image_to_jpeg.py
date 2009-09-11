from Products.PortalTransforms.libtransforms.imagemagick_transform import ImageMagickTransforms

class image_to_jpeg(ImageMagickTransforms):
    __name__  = "image_to_jpeg"
    inputs    = ('image/*', )
    output   = 'image/jpeg'
    format  = 'jpeg'


def register():
    return image_to_jpeg()
