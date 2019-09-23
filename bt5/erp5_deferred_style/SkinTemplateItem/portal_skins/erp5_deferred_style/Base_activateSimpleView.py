from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()
request = portal.REQUEST
format = request.get('format', '')
skin_name = request.get('deferred_portal_skin', portal.portal_skins.getDefaultSkin())
previous_skin_selection = request.get('previous_skin_selection', None)

tag = 'active-report-wrapped-%s' % random.randint(0, 1000)
priority = 3

user = portal.portal_membership.getAuthenticatedMember()
person_value = user.getUserValue()
if person_value is None:
  portal.changeSkin(previous_skin_selection)
  return context.Base_redirect('view', keep_items=dict(
              portal_status_message=translateString(
                        "No person found for your user"),
              portal_status_level='error'))

if person_value.getDefaultEmailText('') in ('', None):
  portal.changeSkin(previous_skin_selection)
  return context.Base_redirect('view', keep_items=dict(
              portal_status_message=translateString(
                        "You haven't defined your email address"),
              portal_status_level='error'))

# save request parameters
request_form = portal.ERP5Site_filterRequestForDeferredStyle(request)

localizer_language = portal.Localizer.get_selected_language()

activity_context = context
if activity_context == portal:
  # portal is not an active object
  activity_context = portal.portal_simulation


params = {}
form = getattr(context, deferred_style_dialog_method)
if hasattr(form, 'ZScriptHTML_tryParams'):
  # Some actions are wrapped by a script.
  # In that case we look at script signature to pass them the sames
  for param in form.ZScriptHTML_tryParams():
    params[param] = request.get(param)
else:
  params['format'] = format

activity_context.activate(
    activity='SQLQueue', tag=tag, priority=priority).Base_renderSimpleView(
           localizer_language=localizer_language,
           skin_name=skin_name,
           request_form=request_form,
           deferred_style_dialog_method=deferred_style_dialog_method,
           user_name=user.getId(),
           params=params,
          )

context.activate(activity='SQLQueue', after_tag=tag).getTitle()

portal.changeSkin(previous_skin_selection)
return context.Base_redirect('view', keep_items=dict(
              portal_status_message=translateString("Report Started")))
