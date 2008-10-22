from Products.PortalTransforms.libtransforms.piltransform import PILTransforms

class image_to_ppm(PILTransforms):
    __name__  = "image_to_ppm"
    inputs    = ('image/*', )
    output   = 'image/x-portable-pixmap'
    format  = 'ppm'


def register():
    return image_to_ppm()
