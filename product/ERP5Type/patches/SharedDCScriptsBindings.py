import Shared.DC.Scripts.Bindings

# Make Shared.DC.Scripts.Bindings a new style classes already on Zope2, so that
# we can install business templates exported on Zope4 in Zope2 instances.
_NameAssignments = Shared.DC.Scripts.Bindings.NameAssignments
if not isinstance(_NameAssignments, type):
  class NameAssignments(_NameAssignments, object):
    def __init__(self, mapping=None):
      if mapping is None:
        mapping = {}
      _NameAssignments.__init__(self, mapping)
  NameAssignments.__module__ = _NameAssignments.__module__

  Shared.DC.Scripts.Bindings.NameAssignments = NameAssignments
