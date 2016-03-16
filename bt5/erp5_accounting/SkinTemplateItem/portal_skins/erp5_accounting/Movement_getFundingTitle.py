movement = context.getObject()
funding_uid = context.funding_uid

title_dict = container.REQUEST.get(
      'Movement_getFundingTitle.funding_title_dict') or {}
if funding_uid in title_dict:
  return title_dict[funding_uid]

if movement.getSourceFundingUid() == funding_uid:
  reference = movement.getSourceFundingReference()
  if reference:
    return '%s - %s' % (reference, movement.getSourceFundingTranslatedTitle())
  return movement.getSourceFundingTranslatedTitle()

reference = movement.getDestinationFundingReference()
if reference:
  return '%s - %s' % (reference, movement.getDestinationFundingTranslatedTitle())
return movement.getDestinationFundingTranslatedTitle()
