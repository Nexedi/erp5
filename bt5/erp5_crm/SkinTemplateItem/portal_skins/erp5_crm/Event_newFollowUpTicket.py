context.Event_createFollowUpTicket(follow_up_ticket_type=follow_up_ticket_type,
                                   follow_up_ticket_title=follow_up_ticket_title,
                                   follow_up_campaign_resource=follow_up_campaign_resource,
                                   follow_up_meeting_resource=follow_up_meeting_resource,
                                   follow_up_sale_opportunity_resource=follow_up_sale_opportunity_resource,
                                   follow_up_support_request_resource=follow_up_support_request_resource,
                                   **kw)
if context.getPortalObject().portal_workflow.isTransitionPossible(
    context, 'deliver'):
  context.deliver()
return context.Base_redirect("",
        keep_items={'portal_status_message':context.getPortalObject().Base_translateString("Follow Up Ticket Created.")})
