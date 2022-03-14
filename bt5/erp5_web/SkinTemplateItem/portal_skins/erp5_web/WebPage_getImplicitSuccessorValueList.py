"""
  Called by WebPage.getImplicitSuccessorValueList

  `reference_list` is list of dicts containing reference and/or version
  and/or language and maybe some more things. But this implementation
  just ignores it.

  It extracts href and their according objects from this ERP5 instance,
  and returns the list of uniq objects.
"""
uid_set = set()
for obj in list(context.WebPage_extractReferredObjectDict().values()):
  if obj is not None:
    uid_set.add(obj.getUid())
if uid_set:
  return context.portal_catalog(uid=list(uid_set))
return ()
