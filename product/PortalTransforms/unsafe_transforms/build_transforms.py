"""try to build some usefull transformations with the command and xml
transforms and the available binaries
"""
from Products.PortalTransforms.libtransforms.utils import bin_search, MissingBinary

COMMAND_CONFIGS = (
    ('lynx_dump', '.html',
     {'binary_path'  : 'lynx',
      'command_line' : '-dump %s',
      'inputs'       : ('text/html',),
      'output'       : 'text/plain',
      }),
    ('tidy_html', '.html',
     {'binary_path'  : 'tidy',
      'command_line' : '%s',
      'inputs'       : ('text/html',),
      'output'       : 'text/html',
      }),
    ('rtf_to_html', None,
     {'binary_path'  : 'unrtf',
      'command_line' : '%s',
      'inputs'       : ('application/rtf',),
      'output'       : 'text/html',
      }),
    ('ppt_to_html', None,
     {'binary_path'  : 'ppthtml',
      'command_line' : '%s',
      'inputs'       : ('application/vnd.ms-powerpoint',),
      'output'       : 'text/html',
      }),
    ('excel_to_html', None,
     {'binary_path'  : 'xlhtml',
      'command_line' : '-nh -a %s',
      'inputs'       : ('application/vnd.ms-excel',),
      'output'       : 'text/html',
      }),
    ('ps_to_text', None,
     {'binary_path'  : 'ps2ascii',
      'command_line' : '%s',
      'inputs'       : ('application/postscript',),
      'output'       : 'text/plain',
      }),
    )

TRANSFORMS = {}

from command import ExternalCommandTransform
for tr_name, extension, config in COMMAND_CONFIGS:
    try:
        bin = bin_search(config['binary_path'])
    except MissingBinary:
        print 'no such binary', config['binary_path']
    else:
        tr = ExternalCommandTransform(tr_name, extension)
        tr.config['binary_path'] = bin
        tr.__name__ = tr_name
        tr.config = config
        TRANSFORMS[tr_name] = tr

XMLPROCS_CONF = {
    'xsltproc' : '--catalogs --xinclude -o %(output)s %(transform)s %(input)s',
    '4xslt' : ' -o %(output)s %(input)s %(transform)s'
    }

bin = None
for proc in XMLPROCS_CONF.keys():
    try:
        bin = bin_search(proc)
        break
    except MissingBinary:
        print 'no such binary', proc

if bin is not None:
    print 'Using %s as xslt processor' % bin
    from xml import XsltTransform
    for output in ('html', 'plain'):
        name = "xml_to_" + output
        command_line = XMLPROCS_CONF[proc]
        tr = XsltTransform(name=name, inputs=('text/xml',), output='text/'+output,
                           binary_path=bin, command_line=command_line)
        TRANSFORMS[name] = tr

def initialize(engine):
    for transform in TRANSFORMS.values():
        engine.registerTransform(transform)
