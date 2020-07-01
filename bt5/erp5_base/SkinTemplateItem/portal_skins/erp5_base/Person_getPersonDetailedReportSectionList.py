from Products.ERP5Form.Report import ReportSection
from erp5.component.module.DateUtils import getIntervalListBetweenDates
from DateTime import DateTime
result=[]
# civil status
result.append(ReportSection(
              path=context.getPhysicalPath(),
              title=context.Base_translateString('Civil Status'),
              form_id='Person_viewPersonDetailedCivilStatus'))

# career list
result.append(ReportSection(
              path=context.getPhysicalPath(),
              title=context.Base_translateString('Careers'),
              listbox_display_mode='FlatListMode',
              form_id='Person_viewPersonDetailedCareerList'))

# event list only if event module exists
if context.getPortalObject().hasObject('event_module'):
  result.append(ReportSection(
    path=context.getPhysicalPath(),
    title=context.Base_translateString('Events'),
    listbox_display_mode='FlatListMode',
    form_id='Person_viewPersonDetailedEventList'))

# contributions list
if context.Person_getUserId() not in (None, ""):
  # list only if user has a login defined
  aggregation_level = context.REQUEST.get('aggregation_level')
  from_date = context.REQUEST.get('from_date')
  to_date = context.REQUEST.get('at_date')

  selection_columns = [('document_type', "Document Type")]
  if from_date is None:
    # get the minimum creation date in catalog
    from_date = context.portal_catalog(
      select_list=['creation_date'],
      sort_on=[['creation_date', 'ASC']],
      limit=1,
    )[0].creation_date
  # get period list between given date
  interval_list_dict = getIntervalListBetweenDates(from_date=from_date, to_date=to_date,
                                              keys={'year':aggregation_level=="year",
                                                    'month':aggregation_level=="month",
                                                    'week' : aggregation_level=="week",
                                                    'day':aggregation_level=="day"})
  interval_list = interval_list_dict[aggregation_level]
  # list columns of the listbox
  selection_columns.extend([(x,x) for x in interval_list])
  selection_columns.append(('total', 'Total'))
  params=dict(period_list=interval_list)

  # stat columns of the listbox
  stat_columns = [('document_type','document_type'),]+[(x,x) for x in interval_list]+[('total', 'total'),]
  context.REQUEST.set('stat_columns', stat_columns)

  result.append(ReportSection(
                path=context.getPhysicalPath(),
                selection_columns=selection_columns,
                listbox_display_mode='FlatListMode',
                title=context.Base_translateString('Contributions'),
                selection_params=params,
                form_id='Person_viewPersonDetailedContributionList'))


return result
