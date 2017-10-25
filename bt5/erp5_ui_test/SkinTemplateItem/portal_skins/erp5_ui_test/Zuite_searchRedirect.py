if REQUEST is not None:
  kw = REQUEST.form.copy()

def sanitizeSortOn(s):
  if isinstance(s, basestring):
    s = s.split(":", 1)
    if len(s) > 1:
      return (s[0], s[1])
    return (s[0], "ascending")
  return s  # XXX raise ?

kw["limit"] = 1

if "sort_on" in kw:
  sort = kw["sort_on"]
  if isinstance(sort, (tuple, list)):
    kw["sort_on"] = tuple([sanitizeSortOn(s) for s in sort])
  else:
    kw["sort_on"] = (sanitizeSortOn(sort),)

return context.getPortalObject().portal_catalog(**kw)[0].Base_redirect()
