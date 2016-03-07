"""
  Return latest discussion threads on a web site public forum.
"""

reference = context.WebSection_getDiscussionApplicablity()

if reference is not None:
  document = context.restrictedTraverse(reference)
  return document.getPredecessorRelatedValueList()

return []
