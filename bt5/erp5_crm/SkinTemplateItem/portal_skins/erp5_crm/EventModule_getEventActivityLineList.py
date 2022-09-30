from Products.PythonScripts.standard import Object
request = container.REQUEST
portal = context.getPortalObject()

request_start_date = request.get('from_date', None)
request_stop_date = request.get('at_date', None)

#define the list of ticket types
ticket_type_list = portal.getPortalTicketTypeList()

#define the list of incoming or outgoing simulation states
line_list = []
column_totals = {}
column_totals['unassigned'] = 0
for ticket_type in ticket_type_list:
  column_totals[ticket_type] = 0
total_count = 0

# Prepare the parameters to filter
query_dict = {}
if request_start_date:
  query_dict['delivery.start_date'] = dict(range='min', query=request_start_date)
if request_stop_date:
  query_dict['delivery.stop_date'] = dict(range='ngt',
                                     query=request_stop_date.latestTime())

for state in portal.ERP5Site_getWorkflowStateItemList(
     display_none_category=False,
     portal_type=portal.getPortalEventTypeList(),
     state_var='simulation_state'):
  #count number of objects in state with request parameters
  obj = Object(uid="new_")
  obj['simulation_state'] = state[0]
  obj['unassigned'] = 0
  total_count_line = 0
  #add all ticket types columns
  for ticket_type in ticket_type_list:
    obj[ticket_type] = 0
  #search all events in actual state
  event_list = portal.portal_catalog.searchResults(
                                portal_type=portal.getPortalEventTypeList(),
                                simulation_state=state[1],
                                **query_dict)
  for revent in event_list:
    event = revent.getObject()
    #count number of objects in state-ticket type with request parameters
    total_count_line += 1
    #Follow-up has priority
    if not event.getFollowUpUid() == None:
      ticket_type = portal.restrictedTraverse(event.getFollowUp()).getPortalType()
    else:
      if not event.getCausalityUid() == None:
        event_rel=portal.restrictedTraverse(event.getCausality())
        #check relationship of the event with ticket by causality
        if not event_rel.getFollowUpUid() == None:
          ticket_type = portal.restrictedTraverse(event_rel.getFollowUp()).getPortalType()
        else:
          #Unassigned
          ticket_type = 'unassigned'
      else:
        #Unassigned
        ticket_type = 'unassigned'
    obj[ticket_type] = obj[ticket_type] + 1
    column_totals[ticket_type] = column_totals[ticket_type] + 1
  obj['total'] = total_count_line
  total_count += total_count_line
  line_list.append(obj)

# Store the stat line in request
obj = Object(uid="new_")
obj['simulation_state'] = portal.Base_translateString('Total')
obj['total'] = total_count
for ticket_type in context.getPortalTicketTypeList():
  obj[ticket_type] = column_totals[ticket_type]
obj['unassigned'] = column_totals['unassigned']
line_stats_list = []
line_stats_list.append(obj)
request.set('stat_line',line_stats_list)

return line_list
