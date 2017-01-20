from Products.PortalTransforms.libtransforms.imagemagick_transform import ImageMagickTransforms

class image_to_bmp(ImageMagickTransforms):
  __name__  = "image_to_bmp"
  inputs    = ('image/*', )
  output    = 'image/x-ms-bmp' # image/bmp
  format    = 'bmp'

def register():
  return image_to_bmp()
