import mtr_mimetypes
import py_mimetypes
import smi_mimetypes
import suppl_mimetypes
import magic

from mtr_mimetypes import *

def initialize(registry):
    mtr_mimetypes.initialize(registry)
    smi_mimetypes.initialize(registry)
    suppl_mimetypes.initialize(registry)
    py_mimetypes.initialize(registry)
