from Products.PythonScripts.standard import Object
request = container.REQUEST
portal = context.getPortalObject()

request_start_date = request.get('from_date', None)
request_stop_date = request.get('at_date', None)
request_ticket_type = request.get('sale_opportunity_type', None)
request_validation_state = request.get('sale_opportunity_state', None)

future_state_list = portal.Event_getFutureStateList()
past_state_list = portal.Event_getPastStateList()

line_list = []

# Prepare the parameters to filter
query_dict = {}
if request_start_date:
  query_dict['delivery.start_date'] = dict(range='min', query=request_start_date)
if request_stop_date:
  query_dict['delivery.stop_date'] = dict(range='ngt', 
                                     query=request_stop_date.latestTime())
if request_validation_state:
  query_dict['simulation_state'] = request_validation_state
if request_ticket_type:
  query_dict['default_resource_uid'] =  [portal.restrictedTraverse(x).getUid() 
                                          for x in request_ticket_type]
section_uid = context.Base_getSectionUidListForSectionCategory(request.get('section_category',None))

# Make the search using parameters
ticketlist=portal.portal_catalog.searchResults(portal_type="Sale Opportunity",
                                                source_section_uid=section_uid,
                                                sort_on='title',
                                                **query_dict) 

# Get every result object
for r_ticket in ticketlist:
  ticket=r_ticket.getObject()
  future = 0
  past = 0
  #count future follow-up events
  future=int(portal.portal_catalog.countResults(portal_type=portal.getPortalEventTypeList(),
                                              follow_up_uid=ticket.getUid(),
                                              simulation_state=future_state_list)[0][0])
  #count past follow-up events
  past=int(portal.portal_catalog.countResults(portal_type=portal.getPortalEventTypeList(),
                                              follow_up_uid=ticket.getUid(),
                                              simulation_state=past_state_list)[0][0])
  #count past causality events
  past+=int(portal.portal_catalog.countResults(event_causality_ticket_uid=ticket.getUid(),
                                              portal_type=portal.getPortalEventTypeList(),
                                              simulation_state=past_state_list)[0][0])
  #count future causality events
  future+=int(portal.portal_catalog.countResults(event_causality_ticket_uid=ticket.getUid(),
                                              portal_type=portal.getPortalEventTypeList(),
                                              simulation_state=future_state_list)[0][0])  
  line_list.append(Object(uid='new_',
                   title = ticket.getTitle(),
                   ticket_type = ticket.getResourceTranslatedTitle(),
                   stop_date = ticket.getStopDate(),
                   start_date = ticket.getStartDate(),
                   destination_section = ticket.getDestinationSectionTitle(),
                   destination_decision = ticket.getDestinationDecisionTitle(),
                   source_decision = ticket.getSourceDecisionTitle(),
                   source = ticket.getSourceTitle(),
                   validation_state = ticket.getTranslatedSimulationStateTitle(),
                   future = future,
                   past = past))

if line_list == []:
  line_list.append(Object(uid='new_'))
return line_list
