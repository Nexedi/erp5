portal = context.getPortalObject()
insolvency_proceeding = portal.insolvency_proceeding_module.newContent(
  destination_section_value=context,
  start_date=start_date,
  resource=resource,
  continuation_of_activity=continuation_of_activity,
  description=description
)
insolvency_proceeding.submit()

return insolvency_proceeding.Base_redirect(
  keep_items={
    'portal_status_message': portal.Base_translateString(
      'New ${portal_type} created.',
      mapping={
        'portal_type': portal.Base_translateString('Insolvency Proceeding'),
      },
    ),
  },
)
