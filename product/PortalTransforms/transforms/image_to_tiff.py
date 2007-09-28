from Products.PortalTransforms.libtransforms.piltransform import PILTransforms

class image_to_tiff(PILTransforms):
    __name__  = "image_to_tiff"
    inputs    = ('image/*', )
    output   = 'image/tiff'
    format  = 'tiff'


def register():
    return image_to_tiff()
