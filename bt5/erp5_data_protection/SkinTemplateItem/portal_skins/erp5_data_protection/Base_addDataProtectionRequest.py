portal = context.getPortalObject()
portal_type = 'Data Protection Request'
module = portal.getDefaultModule(portal_type)
current_user = portal.portal_membership.getAuthenticatedMember().getUserValue()

reference_index = portal.portal_ids.generateNewId(id_group=('data_protection_request'), default=1)
reference = 'DPR-%s' % (reference_index,)
data_protection = module.newContent(portal_type=portal_type,
                                    contributor_value=current_user,
                                    agent_value=context,
                                    description=description,
                                    reference=reference)
data_protection.submit()
msg = portal.Base_translateString('New data protection request added.')
return context.Base_redirect(form_id, keep_items={'portal_status_message': msg}, **kw)
