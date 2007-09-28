"""
A custom transform using external command
"""

__revision__ = '$Id: xml.py 4787 2005-08-19 21:43:41Z dreamcatcher $'

from os.path import join, dirname, exists
import re
from os import popen3, popen4, system
from cStringIO import StringIO

from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.utils import bin_search, sansext
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.utils import log

class XsltTransform(commandtransform):
    """ Custom external command

    transform xml content by launching an external XSLT processor

    Input and output mime types must be set correctly !

    You can associate different document type to different transformations.
    """
    __implements__ = (itransform,)

    __name__ = "xml_to_html"

    def __init__(self, name=None, **kwargs):
        self.config = {
            # sample configuration
            'binary_path'  : bin_search('xsltproc'),
            'command_line' : '%(transform)s %(input)s',
            'inputs'       : ('text/xml',),
            'output'       : 'text/html',
            'output_encoding' : 'UTF-8',
            'dtds'         : {
            '-//OASIS//DTD DocBook V4.1//EN' : '/usr/share/sgml/docbook/xsl-stylesheets-1.29/html/docbook.xsl'
            },
            'default_transform': ''
            }
        self.config_metadata = {
            'binary_path'  : ('string', 'Binary path',
                              'Path of the executable on the server.'),
            'command_line' : ('string', 'Command line',
                              '''Additional command line option.
There should be at least the input file (designed by "%(input)s") and the xsl
file (designed by "%(transform)s").The transformation\'s result must be printed on stdout.
'''),
            'inputs'       : ('list', 'Inputs', 'Input(s) MIME type. Change with care.'),
            'output'       : ('string', 'Output', 'Output MIME type. Change with care.'),
            'output_encoding': ('string', 'Output encoding', 'Output encoding.'),
            'dtds'         : ('dict', 'DTDs',
                              'Association of public ids or dtds to XSL transformations.',
                              ('Public id', 'XSLT path')),
            'default_transform' : ('string', 'Default xslt',
                                   'Default xslt, used when no specific transformation is found.'),
            }
        self.config.update(kwargs)
        if name:
            self.__name__ = name

    def __getattr__(self, attr):
        if attr == 'inputs':
            return self.config['inputs']
        if attr == 'output':
            return self.config['output']
        if attr == 'output_encoding':
            return self.config['output_encoding']
        raise AttributeError(attr)


    def convert(self, data, cache, **kwargs):
        base_name = sansext(kwargs.get("filename") or 'unknown.xml')
        dtds = self.config['dtds']
        tmpdir, fullname = self.initialize_tmpdir(data, filename=base_name)
        try:
            try:
                doctype = get_doctype(data)
            except DTException:
                try:
                    doctype = get_dtd(data)
                except DTException:
                    log('Unable to get doctype nor dtd in %s' % data)
                    doctype = None
            if doctype and dtds.has_key(doctype):
                data = self.invokeCommand(fullname, dtds[doctype])
            elif self.config['default_transform']:
                data = self.invokeCommand(fullname, self.config['default_transform'])
            cache.setData(data)
            path, images = self.subObjects(tmpdir)
            objects = {}
            if images:
                self.fixImages(path, images, objects)
                cache.setSubObjects(objects)
            return cache
        finally:
            self.cleanDir(tmpdir)


    def invokeCommand(self, input_name, xsl):
        dest_dir = dirname(input_name)
        output_file = join(dirname(input_name), 'tr_output')
        command = '%(binary_path)s %(command_line)s' % self.config
        data = {'input': input_name, 'output': output_file, 'transform': xsl}
        system(command % data)

        if exists(output_file):
            data = open(output_file).read()
        else:
            data = 'error occurs during transform. See error log'
        return data



def register():
    return XsltTransform()

DT_RGX = re.compile('<!DOCTYPE \w* PUBLIC \"([^"]*)\" \"([^"]*)\"')
DT_RGX2 = re.compile('<!DOCTYPE \w* SYSTEM \"([^"]*)\"')

class DTException(Exception): pass

def get_doctype(data):
    """ return the public id for the doctype given some raw xml data
    """
    if not hasattr(data, 'readlines'):
        data = StringIO(data)
    for line in data.readlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('<?xml') or line.startswith('<!-- '):
            continue
        m = DT_RGX.match(line)
        if m is not None:
            return m.group(1)
        else:
            raise DTException('Unable to match doctype in "%s"' % line)

def get_dtd(data):
    """ return the public id for the doctype given some raw xml data
    """
    if not hasattr(data, 'readlines'):
        data = StringIO(data)
    for line in data.readlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('<?xml') or line.startswith('<!-- '):
            continue
        m = DT_RGX.match(line)
        if m is not None:
            return m.group(2)
        m = DT_RGX2.match(line)
        if m is not None:
            return m.group(1)
        else:
            raise DTException('Unable to match doctype in "%s"' % line)


if __name__ == '__main__':
    print get_doctype('''<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE article PUBLIC "-//LOGILAB/DTD DocBook V4.1.2-Based Extension V0.1//EN" "dcbk-logilab.dtd" []>

<book id="devtools_user_manual" lang="fr">
''')
