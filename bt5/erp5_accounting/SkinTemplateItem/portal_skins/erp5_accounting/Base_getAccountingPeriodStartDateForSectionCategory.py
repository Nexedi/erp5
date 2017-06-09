from Products.ERP5Type.Cache import CachingMethod

def getAccountingPeriodStartDateForSectionCategory(section_category, date):
  portal = context.getPortalObject()
  # XXX for now we guess period start date from the first organisation having
  # accounting periods, giving priority to the organisation directly associated
  # to the section category
  section_uid = portal.Base_getSectionUidListForSectionCategory(
                                      section_category, strict_membership=True)
  section_uid.extend(portal.Base_getSectionUidListForSectionCategory(
                                      section_category, strict_membership=False))
  period_start_date = None
  for uid in section_uid:
    if uid == -1: continue # Base_getSectionUidListForSectionCategory returns [-1] if no section_uid exists
    section, = portal.portal_catalog(uid=uid, limit=2)
    for ap in section.getObject().contentValues(portal_type='Accounting Period',
                        checked_permission='Access contents information'):
      if ap.getSimulationState() not in ('planned', 'confirmed',
                                         'started', 'stopped',
                                         'closing', 'delivered'):
        continue
      if ap.getStartDate().earliestTime() <= date <= ap.getStopDate().latestTime():
        period_start_date = ap.getStartDate().earliestTime()
    if period_start_date:
      break
  else:
    period_start_date = DateTime(date.year(), 1, 1)
  return period_start_date

getAccountingPeriodStartDateForSectionCategory = CachingMethod(
              getAccountingPeriodStartDateForSectionCategory,
              id=script.getId(), cache_factory='erp5_content_long')

return getAccountingPeriodStartDateForSectionCategory(section_category, date)
