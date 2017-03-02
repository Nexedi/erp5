# this script allows to create a new follow up ticket for a given event
portal = context.getPortalObject()
event = context

operator_list = event.getDestinationList()
try:
  source_value = portal.portal_membership.getAuthenticatedMember().getUserValue()
  if source_value:
    operator_list.append(source_value.getRelativeUrl())
except ValueError:
  source_value = None
source_section = portal.portal_preferences.getPreferredSection(),


resource_kw = {
  "Campaign" : "follow_up_campaign_resource",
  "Meeting" : "follow_up_meeting_resource",
  "Sale Opportunity" : "follow_up_sale_opportunity_resource",
  "Support Request" : "follow_up_support_request_resource",
}

resource = None
if follow_up_ticket_type in resource_kw:
  resource = kw.get(resource_kw[follow_up_ticket_type], None)


module = portal.getDefaultModule(follow_up_ticket_type)
ticket = module.newContent(
            portal_type=follow_up_ticket_type,
            title=follow_up_ticket_title,
            start_date=event.getStartDate(),
            destination_decision_list=event.getSourceList(),
            # destination_section=event.getSourceSection() or event.getSource(),
            source_trade_set=operator_list,
            source_value=source_value,
            source_section=source_section,
            resource=resource,
           )
if follow_up_ticket_type == 'Support Request':
  ticket.setCausalityValue(event)

follow_up_list = event.getFollowUpList()
follow_up_list.append(ticket.getRelativeUrl())
event.edit(follow_up_list=follow_up_list)

if portal.portal_workflow.isTransitionPossible(
    ticket, 'submit'):
  ticket.submit()
