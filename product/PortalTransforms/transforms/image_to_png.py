from Products.PortalTransforms.libtransforms.piltransform import PILTransforms

class image_to_png(PILTransforms):
    __name__  = "image_to_png"
    inputs    = ('image/*', )
    output   = 'image/png'
    format  = 'png'

def register():
    return image_to_png()
