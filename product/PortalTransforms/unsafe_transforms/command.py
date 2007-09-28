"""
A custom transform using external command
"""

__revision__ = '$Id: command.py 4439 2005-06-15 16:32:36Z panjunyong $'

import os.path
from os import popen3
from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.utils import bin_search, sansext
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.utils import log

class ExternalCommandTransform(commandtransform):
    """ Custom external command

    transform content by launching an external command

    the command should take the content in an input file (designed by '%s' in
    the command line parameters) and return output on stdout.
    Input and output mime types must be set correctly !
    """
    __implements__ = (itransform,)

    __name__ = "command_transform"

    def __init__(self, name=None, input_extension=None, **kwargs):
        self.config = {
            'binary_path'  : '',
            'command_line' : '',
            'inputs'       : ('text/plain',),
            'output'       : 'text/plain',
            }
        self.config_metadata = {
            'binary_path'  : ('string', 'Binary path',
                              'Path of the executable on the server.'),
            'command_line' : ('string', 'Command line',
                              '''Additional command line option.
There should be at least the input file (designed by "%(input)s").
The transformation\'s result must be printed on stdout.
'''),
            'inputs'       : ('list', 'Inputs', 'Input(s) MIME type. Change with care.'),
            'output'       : ('string', 'Output', 'Output MIME type. Change with care.'),
            }
        self.config.update(kwargs)
        commandtransform.__init__(self, name=name, binary=self.config['binary_path'],  **kwargs)

        # use the full binary path
        self.config.update({'binary_path':self.binary})
        self.input_extension = input_extension

    def __getattr__(self, attr):
        if attr == 'inputs':
            return self.config['inputs']
        if attr == 'output':
            return self.config['output']
        raise AttributeError(attr)


    def convert(self, data, cache, **kwargs):
        filename = kwargs.get('filename') or 'unknown'
        if self.input_extension is not None:
            kwargs['filename'] = 'unknown' + self.input_extension
        else:
            kwargs['filename'] = 'unknown' + os.path.splitext(filename)[-1]
        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)

        data = self.invokeCommand(fullname)
        cache.setData(data)
        path, images = self.subObjects(tmpdir)
        objects = {}
        if images:
            self.fixImages(path, images, objects)
            cache.setSubObjects(objects)
        self.cleanDir(tmpdir)
        return cache


    def invokeCommand(self, input_name):
        command = '%(binary_path)s %(command_line)s' % self.config
        input, output, error = popen3(command % input_name)
        input.close()
        # first read stderr, else we may hang on stout
        # but, still hang my windows, so commented it :-(
        # error_data = error.read()
        error_data = 'error while running "%s"' % (command % input_name)
        error.close()
        data = output.read()
        output.close()
        if error_data and not data:
            data = error_data
        else:
            log('Error while running "%s":\n %s' % (command % input_name,
                                                    error_data))
        return data

def register():
    return ExternalCommandTransform()
