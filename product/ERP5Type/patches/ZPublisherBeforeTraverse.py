import ZPublisher.BeforeTraverse

# Make ZPublisher.BeforeTraverse.MultiHook a new style classes already on
# Zope2, so that we can install business templates exported on Zope4 in
# Zope2 instances.
_MultiHook = ZPublisher.BeforeTraverse.MultiHook
if not isinstance(_MultiHook, type):
  class MultiHook(_MultiHook, object):
    def __init__(self, hookname='<undefined hookname>', prior=None,
                 defined_in_class=False):
      _MultiHook.__init__(self, hookname, prior, defined_in_class)
  MultiHook.__module__ = _MultiHook.__module__

  ZPublisher.BeforeTraverse.MultiHook = MultiHook
