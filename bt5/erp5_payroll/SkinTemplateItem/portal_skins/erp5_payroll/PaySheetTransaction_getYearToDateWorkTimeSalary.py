portal = context.getPortalObject()
accounting_module = portal.accounting_module

from_date=DateTime(context.getStartDate().year(), 1, 1)
to_date=context.getStartDate()

search_params = \
  {
   'portal_type'         : 'Pay Sheet Transaction',
   'delivery.start_date' : {'range': "minmax", 'query': (from_date, to_date)},
   'delivery.source_section_uid' : context.getSourceSectionUid(),
   'delivery.destination_section_uid' : context.getDestinationSectionUid(),
   'simulation_state'    : ['confirmed', 'stopped', 'delivered'],
  }

paysheet_list = accounting_module.searchFolder( **search_params)

yearly_work_time = 0
for paysheet in paysheet_list:
  annotation_line = paysheet.getAnnotationLineFromReference(\
      reference='work_time_annotation_line')
  if annotation_line is None:
    annotation_line = getattr(paysheet, 'work_time_annotation_line', None)
  if annotation_line is None:
    raise ValueError("Paysheet %s has no Annotation Line with reference work_time_annotation_line"
                             % paysheet.getRelativeUrl())
  nb_heures = annotation_line.getQuantity()
  yearly_work_time += nb_heures

return yearly_work_time
