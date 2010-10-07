from Products.PortalTransforms.libtransforms.retransform import retransform

class xml_to_text(retransform):
    inputs  = ('text/xml', 'application/xml')
    output = 'text/plain'

def register():
    return xml_to_text("xml_to_text",
                       ('<[^>]*>', ' '),
                       )
