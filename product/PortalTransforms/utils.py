# -*- coding: utf-8 -*-
"""some common utilities
"""

import mimetools
import cStringIO

class TransformException(Exception):
    pass

FB_REGISTRY = None

# logging function
from zLOG import LOG, DEBUG
#logger = logging.getLogger('PortalTransforms')

def log(message, severity=DEBUG):
    LOG('PortalTransforms', severity, message)
    #logger.log(severity, message)

# directory where template for the ZMI are located
import os.path
_www = os.path.join(os.path.dirname(__file__), 'www')

def safeToInt(value):
    """Convert value to integer or just return 0 if we can't"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0

def parseContentType(content_type):
  """Parses `text/plain;charset="utf-8"` to a mimetools.Message object.

  Note: Content type or MIME type are built like `maintype/subtype[;params]`.

      parsed_content_type = parseContentType('text/plain;charset="utf-8"')
      parsed_content_type.gettype()  -> 'text/plain'
      parsed_content_type.getmaintype()  -> 'text'
      parsed_content_type.getsubtype()  -> 'plain'
      parsed_content_type.getplist()  -> 'charset="utf-8"'
      parsed_content_type.getparam('charset')  -> 'utf-8'
      parsed_content_type.typeheader  -> 'text/plain;charset="utf-8"'
  """
  return mimetools.Message(cStringIO.StringIO("Content-Type:" + content_type.replace("\r\n", "\r\n\t")))
