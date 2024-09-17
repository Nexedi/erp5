from Products.PortalTransforms.libtransforms.imagemagick_transform import ImageMagickTransforms

class image_to_pcx(ImageMagickTransforms):
  __name__  = "image_to_pcx"
  inputs    = ('image/*', )
  output    = 'image/vnd.zbrush.pcx'
  format    = 'pcx'

def register():
  return image_to_pcx()
