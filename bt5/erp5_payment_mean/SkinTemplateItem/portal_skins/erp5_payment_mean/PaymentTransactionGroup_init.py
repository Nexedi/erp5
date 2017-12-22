from DateTime import DateTime

context.setStopDate(DateTime())
me = context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()
if me is not None:
  context.setSourceAdministrationValue(me)
  section = me.getDefaultCareerSubordinationValue()
  if section is not None:
    context.setSourceSectionValue(section)
    context.setPriceCurrency(section.getPriceCurrency())

context.PaymentTransactionGroup_generateSourceReference()
