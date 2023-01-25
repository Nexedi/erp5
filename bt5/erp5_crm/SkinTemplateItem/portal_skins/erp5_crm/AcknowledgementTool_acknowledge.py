user_name = context.portal_membership.getAuthenticatedMember()

context.portal_acknowledgements.acknowledge(path=acknowledgement_url,
       user_name=user_name)

return container.REQUEST.RESPONSE.redirect(context.absolute_url())
