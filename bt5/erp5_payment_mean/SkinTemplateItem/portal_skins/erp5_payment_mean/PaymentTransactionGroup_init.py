from DateTime import DateTime

context.setStopDate(DateTime())
me = context.ERP5Site_getAuthenticatedMemberPersonValue()
if me is not None:
  context.setSourceAdministrationValue(me)
  section = me.getDefaultCareerSubordinationValue()
  if section is not None:
    context.setSourceSectionValue(section)
    context.setPriceCurrency(section.getPriceCurrency())
new_id = context.portal_ids.generateNewLengthId(id_group = "PTGR",  default=1)
reference = "PTGR-%06d" % (new_id)
context.setSourceReference(reference)
