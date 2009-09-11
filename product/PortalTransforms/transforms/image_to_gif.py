from Products.PortalTransforms.libtransforms.imagemagick_transform import ImageMagickTransforms

class image_to_gif(ImageMagickTransforms):
    __name__  = "image_to_gif"
    inputs    = ('image/*', )
    output   = 'image/gif'
    format  = 'gif'


def register():
    return image_to_gif()
