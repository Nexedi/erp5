### Register Transforms
### This is interesting because we don't expect all transforms to be
### available on all platforms. To do this we allow things to fail at
### two levels
### 1) Imports
###    If the import fails the module is removed from the list and
###    will not be processed/registered
### 2) Registration
###    A second phase happens when the loaded modules register method
###    is called and this produces an instance that will used to
###    implement the transform, if register needs to fail for now it
###    should raise an ImportError as well (dumb, I know)

from logging import DEBUG, ERROR
from Products.PortalTransforms.utils import log
from Products.PortalTransforms.libtransforms.utils import MissingBinary
modules = (
            'html_to_odt',
            'odt_to_doc',
            'odt_to_pdf',
          )

g = globals()
transforms = []
for m in modules:
  try:
    ns = __import__(m, g, g, None)
    transforms.append(ns.register())
  except ImportError as e:
    msg = "Problem importing module %s : %s" % (m, e)
    log(msg, severity=ERROR)
  except MissingBinary as e:
    log(str(e), severity=DEBUG)
  except Exception as e:
    import traceback
    traceback.print_exc()
    log("Raised error %s for %s" % (e, m), severity=ERROR)

def initialize(engine):
  for transform in transforms:
    engine.registerTransform(transform)
