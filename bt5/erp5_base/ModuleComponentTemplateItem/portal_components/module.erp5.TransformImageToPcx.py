from Products.PortalTransforms.libtransforms.imagemagick_transform import ImageMagickTransforms

class TransformImageToPcx(ImageMagickTransforms):
  __name__  = "image_to_pcx"
  inputs    = ('image/*', )
  output    = 'image/pcx' # image/vnd.zbrush.pcx image/x-pcx
  format    = 'pcx'

def register():
  return TransformImageToPcx()
