"""
we search for docs that reference us in any way (reference only or more specific)
by making a union of a number of searches
we can return raw set, the class will get objects and make the records unique
and make sure we get latest/most relevant version
should be reimplemented in SQL some sunny day.
"""
reference = context.getReference()
if reference is None or not context.isSearchableReference():
  # empty or not following format preference
  return ()

return context.Base_zGetImplicitPredecessorValueList(reference=reference)
