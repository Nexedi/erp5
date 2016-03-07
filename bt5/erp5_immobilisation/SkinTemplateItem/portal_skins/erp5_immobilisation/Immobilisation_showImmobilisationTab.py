# Return true if Immobilisation Tab is needed
method = context.getAmortisationMethod()
if method in (None, "", "no_change", "unimmobilise"):
  return 0
return 1
