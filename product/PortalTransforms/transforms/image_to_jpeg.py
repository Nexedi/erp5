from Products.PortalTransforms.libtransforms.piltransform import PILTransforms

class image_to_jpeg(PILTransforms):
    __name__  = "image_to_jpeg"
    inputs    = ('image/*', )
    output   = 'image/jpeg'
    format  = 'jpeg'


def register():
    return image_to_jpeg()
