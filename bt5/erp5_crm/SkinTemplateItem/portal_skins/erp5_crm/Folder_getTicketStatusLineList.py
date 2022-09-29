from Products.PythonScripts.standard import Object
request = container.REQUEST
portal = context.getPortalObject()

request_start_date = request.get('from_date', None)
request_stop_date = request.get('at_date', None)
request_ticket_type = request.get('ticket_type', None)
request_simulation_state = request.get('simulation_state', None)
request_section_category = request.get('section_category', None)

line_list = []

# Prepare the parameters to filter
query_dict = {}
if request_start_date:
  query_dict['delivery.start_date'] = dict(range='min', query=request_start_date)
if request_stop_date:
  query_dict['delivery.stop_date'] = dict(range='ngt',
                                     query=request_stop_date.latestTime())
if request_simulation_state:
  query_dict['simulation_state'] = request_simulation_state
if request_ticket_type:
  query_dict['default_resource_uid'] =  [portal.restrictedTraverse(x).getUid() for x in request_ticket_type]
section_uid = context.Base_getSectionUidListForSectionCategory(request_section_category)

allowed_content_type_list = portal.portal_types[context.getPortalType()].getTypeAllowedContentTypeList()

# Make the searsh using parameters
ticket_list = portal.portal_catalog.searchResults(portal_type=allowed_content_type_list,
                                                  source_section_uid=section_uid,
                                                  **query_dict)

# Get every result object
for r_ticket in ticket_list:
  ticket=r_ticket.getObject()
  #count follow-up events
  event_count = portal.portal_catalog.countResults(portal_type=portal.getPortalEventTypeList(),
                                                   follow_up_uid=ticket.getUid())[0][0]
  #count causality events
  event_count += portal.portal_catalog.countResults(event_causality_ticket_uid=ticket.getUid(),
                                                    portal_type=portal.getPortalEventTypeList())[0][0]
  line_list.append(Object(uid='new_',
                          title=ticket.getTitle(),
                          ticket_type=ticket.getResourceTranslatedTitle(),
                          stop_date=ticket.getStopDate(),
                          start_date=ticket.getStartDate(),
                          destination_section=ticket.getDestinationSectionTitle(),
                          destination_decision=ticket.getDestinationDecisionTitle(),
                          source=ticket.getSourceTitle(),
                          simulation_state=ticket.getTranslatedSimulationStateTitle(),
                          event_count=event_count
                          ))

return line_list
