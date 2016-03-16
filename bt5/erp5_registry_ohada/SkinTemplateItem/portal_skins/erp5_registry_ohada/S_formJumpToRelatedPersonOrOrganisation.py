# Jump to a person of the current P form

request=context.REQUEST
s_form = context.getObject()

if s_form is not None:
  portal = context.getPortalObject()
  rccm = s_form.getCorporateRegistrationCode()
  org_result = portal.organisation_module.searchFolder(corporate_registration_code=rccm)
  organisation_uid_list = [org.getObject().getUid() for org in org_result]
  if len(organisation_uid_list) != 0 : 
    kw = {'uid': organisation_uid_list}
    context.portal_selections.setSelectionParamsFor('Base_jumpToRelatedObjectList', kw)
    request.set('object_uid', context.getUid())
    request.set('uids', organisation_uid_list)
    return context.Base_jumpToRelatedObjectList(uids=organisation_uid_list, REQUEST=request)


redirect_url = '%s/view?%s' % (context.getPath(),
            'portal_status_message=No+Organisation+Related+Current+Form')

return context.REQUEST[ 'RESPONSE' ].redirect(redirect_url)
