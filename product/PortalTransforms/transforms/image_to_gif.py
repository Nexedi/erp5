from Products.PortalTransforms.libtransforms.piltransform import PILTransforms

class image_to_gif(PILTransforms):
    __name__  = "image_to_gif"
    inputs    = ('image/*', )
    output   = 'image/gif'
    format  = 'gif'


def register():
    return image_to_gif()
