"""
================================================================================
Return relevant (predecessor) context from which letter was created
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
# context_url:                   relative url of the context calling this script

from zExceptions import Unauthorized

if context_url is not None:
  try:
    underlying_context = context.restrictedTraverse(context_url)
    underlying_portal_type = underlying_context.getPortalType()
    if underlying_portal_type == "Letter":
      for aggregate in underlying_context.getAggregateValueList() or []:
        for predecessor in aggregate.getPredecessorValueList() or []:
          if predecessor.getRelativeUrl() == context_url:
            return aggregate

  # restricted traverse => Unauthoried, Not found, aggregate => Attribue
  except (AttributeError, KeyError, Unauthorized):
    pass

return context

#setPredecessorValueList([object]) = referenced documents
#setSuccessorValueList([object]) = related documents
#getPredecessor()
