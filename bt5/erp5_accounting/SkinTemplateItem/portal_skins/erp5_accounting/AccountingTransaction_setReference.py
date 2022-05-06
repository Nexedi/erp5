# Get sections.
source_section = None
source_section_value = context.getSourceSectionValue()
if source_section_value is not None \
      and source_section_value.getPortalType() == 'Organisation':
  source_section_value = \
      source_section_value.Organisation_getMappingRelatedOrganisation()
  source_section = source_section_value.getRelativeUrl()

destination_section = None
destination_section_value = context.getDestinationSectionValue()
if destination_section_value is not None \
      and destination_section_value.getPortalType() == 'Organisation':
  destination_section_value = \
      destination_section_value.Organisation_getMappingRelatedOrganisation()
  destination_section = destination_section_value.getRelativeUrl()

portal = context.getPortalObject()
id_generator = portal.portal_ids.generateNewId
previous_id_getter = portal.portal_ids.getLastGeneratedId

# Invoice Reference is automatically filled only for Sale Invoice context.
if context.getPortalType() == 'Sale Invoice Transaction':
  if not context.getReference():
    invoice_id_group = ('accounting', 'invoice', source_section)
    invoice_reference = id_generator(id_generator='document',
                                     id_group=invoice_id_group,
                                     default=previous_id_getter(invoice_id_group,
                                     default=0) + 1)
    context.setReference(invoice_reference)


# Generate new values for Source Reference and Destination Reference.
if not context.getSourceReference():
  period = context.AccountingTransaction_getAccountingPeriodForSourceSection()
  period_code = ''
  if period is not None:
    period_code = period.getShortTitle() or period.getTitle() or ''
  if not period_code:
    period_code = str(context.getStartDate().year())
  source_id_group = ('accounting', 'section', source_section, period_code)
  source_reference = id_generator(id_generator='uid',
                                  id_group=source_id_group,
                                  default=previous_id_getter(source_id_group,
                                                             default=0) + 1)
  context.setSourceReference('%s-%s' % (period_code, source_reference))

if not context.getDestinationReference():
  period = context.AccountingTransaction_getAccountingPeriodForDestinationSection()
  period_code = ''
  if period is not None:
    period_code = period.getShortTitle() or period.getTitle() or ''
  if not period_code:
    period_code = str(context.getStopDate().year())
  destination_id_group = ('accounting', 'section', destination_section, period_code)
  destination_reference = id_generator(id_generator='uid',
                                       id_group=destination_id_group,
                                       default=previous_id_getter(destination_id_group,
                                                                    default=0) + 1)
  context.setDestinationReference('%s-%s' % (period_code, destination_reference))
