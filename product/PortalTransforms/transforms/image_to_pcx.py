from Products.PortalTransforms.libtransforms.piltransform import PILTransforms

class image_to_pcx(PILTransforms):
    __name__  = "image_to_pcx"
    inputs    = ('image/*', )
    output   = 'image/pcx'
    format  = 'pcx'


def register():
    return image_to_pcx()
