from Products.PythonScripts.standard import Object
request = container.REQUEST
portal = context.getPortalObject()

request_start_date = request.get('from_date', None)
request_stop_date = request.get('at_date', None)
request_ticket_type = request.get('ticket_type', None)
request_simulation_state = request.get('simulation_state', None)

line_list = []

# Prepare the parameters to filter
query_dict = {}
if request_start_date:
  query_dict['delivery.start_date'] = dict(range='min', query=request_start_date)
if request_stop_date:
  query_dict['delivery.stop_date'] = dict(range='ngt', query=request_stop_date.latestTime())
if request_simulation_state:
  query_dict['simulation_state'] = request_simulation_state
if request_ticket_type:
  query_dict['default_resource_uid'] = [portal.restrictedTraverse(x).getUid() for x in request_ticket_type]
section_uid = portal.Base_getSectionUidListForSectionCategory(request.get('section_category',None))

allowed_content_type_list = portal.portal_types[context.getPortalType()].getTypeAllowedContentTypeList()

# Make the searsh using parameters
ticket_list = portal.portal_catalog.searchResults(portal_type=allowed_content_type_list,
                                                  source_section_uid=section_uid,
                                                  **query_dict)
# Get every result object
for r_ticket in ticket_list:
  ticket=r_ticket.getObject()
  #show follow-up events
  event_list=portal.portal_catalog.searchResults(portal_type=portal.getPortalEventTypeList(),
                                                 follow_up_uid=ticket.getUid())
  for event in event_list:
    line_list.append(Object(uid='new_',
                            ticket=ticket.getTitle(),
                            type=event.getTranslatedPortalType(),
                            destination_title=', '.join(event.getDestinationTitleList()),
                            title=event.getTitle(),
                            stop_date=event.getStopDate(),
                            start_date=event.getStartDate(),
                            source=event.getSourceTitle(),
                            simulation_state=event.getTranslatedSimulationStateTitle()))
    #show causality events of every event
    event_causality_list = portal.portal_catalog.searchResults(portal_type=portal.getPortalEventTypeList(),
                                                               causality_uid=event.getUid())
    for r_event_causality in event_causality_list:
      event_causality = r_event_causality.getObject()
      #check that one event it isn't related by causality and follow-up with the same ticket
      if ticket.getUid() != event_causality.getFollowUpUid():
        line_list.append(Object(uid='new_',
                                ticket='',
                                type=event_causality.getTranslatedPortalType(),
                                destination_title=', '.join(event_causality.getDestinationTitleList()),
                                title=event_causality.getTitle(),
                                stop_date=event_causality.getStopDate(),
                                start_date=event_causality.getStartDate(),
                                source=event_causality.getSourceTitle(),
                                simulation_state=event_causality.getTranslatedSimulationStateTitle()))

return line_list
