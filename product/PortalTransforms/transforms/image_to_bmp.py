from Products.PortalTransforms.libtransforms.piltransform import PILTransforms

class image_to_bmp(PILTransforms):
    __name__  = "image_to_bmp"
    inputs    = ('image/*', )
    output   = 'image/x-ms-bmp'
    format  = 'bmp'


def register():
    return image_to_bmp()
