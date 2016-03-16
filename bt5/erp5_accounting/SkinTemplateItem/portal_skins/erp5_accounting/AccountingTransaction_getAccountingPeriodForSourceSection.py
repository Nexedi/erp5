"""Returns the accounting period for the source section that should be applied for this
accounting transaction.
"""

operation_date = context.getStartDate()
if not operation_date:
  return None

section = context.getSourceSectionValue(portal_type='Organisation')
if section is not None:
  section = section.Organisation_getMappingRelatedOrganisation()
  for accounting_period in section.contentValues(
                          portal_type='Accounting Period',
                          checked_permission='Access contents information'):
    if accounting_period.getSimulationState() in (
              'draft', 'cancelled', 'deleted'):
      continue
    if accounting_period.getStartDate().earliestTime()\
              <=  operation_date <= \
       accounting_period.getStopDate().latestTime():
      return accounting_period
