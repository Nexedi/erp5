request = container.REQUEST

portal = context.getPortalObject()
N_ = portal.Base_translateString

previous_skin_selection = request.get('previous_skin_selection', None)

user = portal.portal_membership.getAuthenticatedMember()
person_value = user.getUserValue()
if person_value is None:
  portal.changeSkin(previous_skin_selection)
  return context.Base_redirect('view', keep_items=dict(
              portal_status_message=N_("No person found for your user")))

if person_value.getDefaultEmailText('') in ('', None):
  portal.changeSkin(previous_skin_selection)
  return context.Base_redirect('view', keep_items=dict(
              portal_status_message=N_("You haven't defined your email address")))


tag = 'active-report-%s' % random.randint(0, 1000)
priority = 2
format_ = request.get('format', '')
skin_name = request['deferred_portal_skin']

# save request parameters (after calling the report_method which may tweak the
# request).
report_request = portal.ERP5Site_filterRequestForDeferredStyle(request)

localizer_language = portal.Localizer.get_selected_language()

context.activate(
    activity="SQLQueue",
    node=portal.portal_preferences.getPreferredDeferredReportActivityFamily(),
    tag=tag,
    after_tag=after_tag,
    priority=priority,
).Base_computeReportSection(
    form=form.getId(),
    report_request=report_request,
    user_name=user.getId(),
    tag=tag,
    skin_name=skin_name,
    format=format_,
    priority=priority,
    localizer_language=localizer_language,
    **kw)

context.activate(activity='SQLQueue', after_tag=tag).getTitle()

portal.changeSkin(previous_skin_selection)
return context.Base_redirect('view', keep_items=dict(
              portal_status_message=N_("Report Started")))
