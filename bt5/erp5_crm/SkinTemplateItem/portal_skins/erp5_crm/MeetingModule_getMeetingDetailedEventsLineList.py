from Products.PythonScripts.standard import Object
request = container.REQUEST
portal = context.getPortalObject()

request_start_date = request.get('from_date', None)
request_stop_date = request.get('at_date', None)
request_ticket_type = request.get('meeting_type', None)
request_validation_state = request.get('validation_state', None)

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

# Make the searsh using parameters
ticketlist=portal.portal_catalog.searchResults(portal_type="Meeting",
                                                source_section_uid=section_uid,
                                                sort_on='title',
                                                **query_dict) 
# Get every result object
for r_ticket in ticketlist: 
  ticket=r_ticket.getObject()
  #show future follow-up events
  eventlist=portal.portal_catalog.searchResults(portal_type=portal.getPortalEventTypeList(),
                                                 follow_up_uid=ticket.getUid(),
                                                 simulation_state=future_state_list)
  #sort the list by destination (recipient)
  eventlist_sorted=[]
  for event in eventlist:
    eventlist_sorted.append(event.getObject())
  eventlist_sorted.sort(key=lambda x: x.getDestinationTitle())
  for event in eventlist_sorted:
    line_list.append( Object(uid='new_',
                           meeting = ticket.getTitle(),
                           type = event.getTranslatedPortalType(),
                           destination_title_list = event.getDestinationTitleList(),
                           title = event.getTitle(),
                           stop_date = event.getStopDate(),
                           start_date = event.getStartDate(),
                           source = event.getSourceTitle(),
                           validation_state = event.getTranslatedSimulationStateTitle()))
    #show past or future causality events of every future event
    event_causality_list=portal.portal_catalog.searchResults(portal_type=
                                                      portal.getPortalEventTypeList(),
                                                      simulation_state=future_state_list+past_state_list,
                                                      causality_uid=event.getUid())
    for r_event_causality in event_causality_list:
      event_causality=r_event_causality.getObject()
      #check that one event it isn't related by causality and follow-up with the same ticket
      if ticket.getUid()<>event_causality.getFollowUpUid():
        line_list.append( Object(uid='new_',
                             meeting = "",
                             type = event_causality.getTranslatedPortalType(),
                             destination_title_list = event_causality.getDestinationTitleList(),
                             title = event_causality.getTitle(),
                             stop_date = event_causality.getStopDate(),
                             start_date = event_causality.getStartDate(),
                             source = event_causality.getSourceTitle(),
                             validation_state = event_causality.getTranslatedSimulationStateTitle()))
                            
  #show past follow-up events
  eventlist=portal.portal_catalog.searchResults(portal_type=portal.getPortalEventTypeList(),
                                                 follow_up_uid=ticket.getUid(),
                                                 simulation_state=past_state_list)
  #sort the list by source
  eventlist_sorted=[]
  for event in eventlist:
    eventlist_sorted.append(event.getObject())
  eventlist_sorted.sort(key=lambda x: x.getSourceTitle())
  for event in eventlist_sorted:
    line_list.append( Object(uid='new_',
                           meeting = ticket.getTitle(),
                           type = event.getTranslatedPortalType(),
                           destination_title_list = event.getDestinationTitleList(),
                           title = event.getTitle(),
                           stop_date = event.getStopDate(),
                           start_date = event.getStartDate(),
                           source = event.getSourceTitle(),
                           validation_state = event.getTranslatedSimulationStateTitle()))
    #show past or future causality events of every past event
    event_causality_list=portal.portal_catalog.searchResults(portal_type=
                                                      portal.getPortalEventTypeList(),
                                                      simulation_state=future_state_list+past_state_list,
                                                      causality_uid=event.getUid())
    for r_event_causality in event_causality_list:
      event_causality=r_event_causality.getObject()
      #check that one event it isn't related by causality and follow-up with the same ticket
      if ticket.getUid()<>event_causality.getFollowUpUid():
        line_list.append( Object(uid='new_',
                             meeting = "",
                             type = event_causality.getTranslatedPortalType(),
                             destination_title_list = event_causality.getDestinationTitleList(),
                             title = event_causality.getTitle(),
                             stop_date = event_causality.getStopDate(),
                             start_date = event_causality.getStartDate(),
                             source = event_causality.getSourceTitle(),
                             validation_state = event_causality.getTranslatedSimulationStateTitle()))
        
if line_list==[]:
  line_list.append(Object(uid='new_'))
return line_list
