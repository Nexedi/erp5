"""
  Called by WebPage.getImplicitSuccessorValueList

  `reference_list` is list of dicts containing reference and/or version
  and/or language and maybe some more things. But this implementation
  just ignores it.

  It extracts href and their according objects from this ERP5 instance,
  and returns the list of uniq objects.
"""
uid_set = set()
for o in context.WebPage_extractReferredObjectDict().values():
  if o is not None:
    uid_set.add(o.getUid())
return context.portal_catalog(uid=list(uid_set))
