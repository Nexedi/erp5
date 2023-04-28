portal = context.getPortalObject()
N_ = portal.Base_translateString

user = portal.portal_membership.getAuthenticatedMember()
person_value = user.getUserValue()

if person_value is None:
  portal.changeSkin(None)
  return context.Base_redirect('view', keep_items=dict(
              portal_status_message=N_("No person found for your user")))

if person_value.getDefaultEmailText('') in ('', None):
  portal.changeSkin(None)
  return context.Base_redirect('view', keep_items=dict(
              portal_status_message=N_("You haven't defined your email address")))

context.activate(
  activity='SQLDict',
  tag=script.id
).LetterPostModule_exportExportableLetterPostActivity(
  user.getUserId(),
  comment,
  portal.Localizer.get_selected_language(),
)

return context.Base_redirect('view',
  keep_items=dict(portal_status_message=N_("Report Started")))
