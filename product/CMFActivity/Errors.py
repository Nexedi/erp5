"""Exception Classes for ERP5"""

# These classes are placed here so that they can be imported into TTW Python
# scripts. To do so, add the following line to your Py script:
# from Products.CMFActivity.Errors import DeferredCatalogError

from Products.PythonScripts.Utility import allow_class

class ActivityPendingError(Exception):
    """Pending activities"""

class ActivityFlushError(Exception):
    """Error during active message flush"""

allow_class(ActivityPendingError)
allow_class(ActivityFlushError)
