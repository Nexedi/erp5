"""some common utilities
"""
import logging
from time import time
from types import UnicodeType, StringType

STRING_TYPES = (UnicodeType, StringType)

class TransformException(Exception):
    pass

FB_REGISTRY = None

# logging function
logger = logging.getLogger('PortalTransforms')

def log(message, severity=logging.INFO):
    logger.log(severity, message)

# directory where template for the ZMI are located
import os.path
_www = os.path.join(os.path.dirname(__file__), 'www')
skins_dir = os.path.join(os.path.dirname(__file__), 'skins')

from zExceptions import BadRequest

# directory where template for the ZMI are located
import os.path
_www = os.path.join(os.path.dirname(__file__), 'www')
skins_dir = None
