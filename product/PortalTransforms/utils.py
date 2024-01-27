# -*- coding: utf-8 -*-
"""some common utilities
"""

import io
import six
if six.PY2:
    from email import message_from_string as message_from_bytes
else:
    from email import message_from_bytes


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
  """Parses `text/plain;charset="utf-8"` to a email.Message object"""
  return message_from_bytes(
    b"Content-Type:"
    + content_type.replace("\r\n", "\r\n\t").encode('utf-8'))
