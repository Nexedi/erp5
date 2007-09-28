"""some common utilities
"""
from time import time
from types import UnicodeType, StringType

STRING_TYPES = (UnicodeType, StringType)

class MimeTypeException(Exception):
    pass

# logging function
from zLOG import LOG, INFO
def log(msg, severity=INFO, id='MimetypesRegistry'):
    LOG(id, severity, msg)

# directory where template for the ZMI are located
import os.path
_www = os.path.join(os.path.dirname(__file__), 'www')
skins_dir = os.path.join(os.path.dirname(__file__), 'skins')
