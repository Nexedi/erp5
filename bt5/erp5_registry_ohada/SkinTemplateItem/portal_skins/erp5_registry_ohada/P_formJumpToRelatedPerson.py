# Jump to a person of the current P form
request=context.REQUEST
p_form = context.getObject()

if p_form is not None:
  portal = context.getPortalObject()
  rccm = p_form.getCorporateRegistrationCode()
  pers_result = portal.organisation.searchFolder(corporate_registration_code=rccm)
  person_uid_list = [pers.getObject().getUid() for pers in pers_result]

  if len(person_uid_list) != 0 :
    kw = {'uid': person_uid_list}
    context.portal_selections.setSelectionParamsFor('Base_jumpToRelatedObjectList', kw)
    request.set('object_uid', context.getUid())
    request.set('uids', person_uid_list)
    return context.Base_jumpToRelatedObjectList(uids=person_uid_list, REQUEST=request)

redirect_url = '%s/view?%s' % (context.getPath(),
            'portal_status_message=No+Person+Related+Current+Form')

return context.REQUEST[ 'RESPONSE' ].redirect(redirect_url)
