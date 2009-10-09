from Products.PortalTransforms.libtransforms.retransform import retransform

class html_to_text(retransform):
    inputs  = ('text/html',)
    output = 'text/plain'

def register():
    # XXX convert entites with htmlentitydefs.name2codepoint ?
    return html_to_text("html_to_text",
                       ('<script [^>]>.*</script>(?im)', ''),
                       ('<style [^>]>.*</style>(?im)', ''),
                       ('<head [^>]>.*</head>(?im)', ''),
                       
                       # added for ERP5, we want to transform <br/> in newlines
                       ('<br\s*/?>(?im)', '\n'),

                       ('(?im)<(h[1-6r]|address|p|ul|ol|dl|pre|div|center|blockquote|form|isindex|table)(?=\W)[^>]*>', ' '),
                       ('<[^>]*>(?i)(?m)', ''),
                       )
