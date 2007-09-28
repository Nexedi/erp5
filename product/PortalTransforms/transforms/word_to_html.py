from Products.PortalTransforms.interfaces import itransform

EXTRACT_BODY  = 1
EXTRACT_STYLE = 0

FIX_IMAGES    = 1
IMAGE_PREFIX  = "img_"

# disable office_uno because it doesn't support multithread yet
ENABLE_UNO = False

import os
if os.name == 'posix':
    try:
        if ENABLE_UNO:
            from office_uno import document
        else:
            raise
    except:
        from office_wvware import document
else:
    try:
        if ENABLE_UNO:
            from office_uno import document
        else:
            raise
    except:
        from office_com import document

import os.path

class word_to_html:
    __implements__ = itransform

    __name__ = "word_to_html"
    inputs   = ('application/msword',)
    output  = 'text/html'
    output_encoding = 'utf-8'

    tranform_engine = document.__module__

    def name(self):
        return self.__name__

    def convert(self, data, cache, **kwargs):
        orig_file = 'unknown.doc'

        doc = document(orig_file, data)
        doc.convert()
        html = doc.html()

        path, images = doc.subObjects(doc.tmpdir)
        objects = {}
        if images:
            doc.fixImages(path, images, objects)
        doc.cleanDir(doc.tmpdir)

        cache.setData(html)
        cache.setSubObjects(objects)
        return cache

def register():
    return word_to_html()
