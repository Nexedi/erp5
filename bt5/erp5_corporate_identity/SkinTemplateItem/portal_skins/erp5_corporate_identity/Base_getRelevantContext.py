"""
================================================================================
Return relevant (predecessor) context if Letter is a subobject
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
# context_url:                   relative url of the context calling this script

if context_url is not None:
  try:
    underlying_context = context.restrictedTraverse(context_url)
    underlying_portal_type = underlying_context.getPortalType()
    if underlying_portal_type == "Letter":
      for aggregate in underlying_context.getAggregateValueList() or []:
        for predecessor in aggregate.getPredecessorValueList() or []:
          if predecessor.getRelativeUrl() == context_url:
            return aggregate
  except:
    pass

return context

#setPredecessorValueList([object]) = referenced documents
#setSuccessorValueList([object]) = related documents
#getPredecessor()
