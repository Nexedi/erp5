from Products.PortalTransforms.libtransforms.imagemagick_transform import ImageMagickTransforms

class image_to_svg(ImageMagickTransforms):
    __name__  = "image_to_svg"
    inputs    = ('image/*', )
    output   = 'image/svg+xml'
    format  = 'svg'

def register():
    return image_to_svg()
