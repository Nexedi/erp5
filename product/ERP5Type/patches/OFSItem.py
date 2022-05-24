from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem

"""
Very simple volatile-attribute-based caching.

Especially useful to cache processed pseudo-constants in PythonScripts: cached
value will be set as a volatile on the PythonScript, so it gets flushed when
script is edited.
For such use, it would be even better to be able to put evaluate-once code
in PythonScripts (ie, make python scripts really become Python *Scripts*, not
"python-function-body-and-parameters").

NOTE: This patches OFS.Item.SimpleItem as it's the lowest patchable class
before persistence.Persistent, where this patch would actually belong.
"""

security = ClassSecurityInfo()
security.declarePublic('volatileCached')
def volatileCached(self, func):
  """
  Cache "func()" return value using a volatile on self.
  Return that value, calling func only if needed.

  Usual volatile rules apply:
  - outlives transaction duration
  - bound to a thread only while a transaction is executed (ie, it can be
    reused by a different thread on next processed transaction)
  - destroyed when object is modified by another transaction
  - destroyed when object is modified by transaction and transaction gets
    aborted
  - destroyed when connection cache is minimized and holder (self) is pruned
    (minimization can be triggered in many places...)

  Of course, you should only cache values which *only* depends on self's
  pertistent properties, and no other object (persistent or not). Otherwise
  your cache will not be flushed when it needs to.
  """
  try:
    cache_dict = self._v_SimpleItem_Item_vCache
  except AttributeError:
    # It's safe to use a non-persistence-aware instance, we are setting a
    # volatile property anyway.
    self._v_SimpleItem_Item_vCache = cache_dict = {}
  # Use whole func_code as a key, as it is the only reliable way to identify a
  # function.
  key = func.__code__
  try:
    return cache_dict[key]
  except KeyError:
    cache_dict[key] = value = func()
    return value

SimpleItem.volatileCached = volatileCached
security.apply(SimpleItem)
