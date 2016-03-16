request = container.REQUEST

portal = context.getPortalObject()
N_ = portal.Base_translateString

person_value = portal.ERP5Site_getAuthenticatedMemberPersonValue()
if person_value is None:
  portal.changeSkin(None)
  return context.Base_redirect('view', keep_items=dict(
              portal_status_message=N_("No person found for your user")))

if person_value.getDefaultEmailText('') in ('', None):
  portal.changeSkin(None)
  return context.Base_redirect('view', keep_items=dict(
              portal_status_message=N_("You haven't defined your email address")))


user_name = person_value.getReference()
tag = 'active-report-%s' % random.randint(0, 1000)
priority = 2
format = request.get('format', '')
skin_name = request['deferred_portal_skin']

# save request parameters (after calling the report_method which may tweak the
# request). XXX we exclude some reserved names in a very ad hoc way
request_other = {}
for k, v in request.items():
  if k not in ('TraversalRequestNameStack', 'AUTHENTICATED_USER', 'URL',
      'SERVER_URL', 'AUTHENTICATION_PATH', 'USER_PREF_LANGUAGES', 'PARENTS',
      'PUBLISHED', 'AcceptLanguage', 'AcceptCharset', 'RESPONSE', 'SESSION',
      'ACTUAL_URL'):
    # XXX proxy fields stores a cache in request.other that cannot be pickled
    if same_type(k, '') and k.startswith('field__proxyfield'):
      continue
    # Remove FileUpload parameters
    elif getattr(v, 'headers', ''):
      continue
    request_other[k] = v



context.activate(activity="SQLQueue", tag=tag, after_tag=after_tag,
  priority=priority).Base_computeReportSection(
    form=form.getId(), 
    request_other=request_other, 
    user_name=user_name, 
    tag=tag,
    skin_name=skin_name, 
    format=format,
    priority=priority, 
    **kw)

context.activate(activity='SQLQueue', after_tag=tag).getTitle()

portal.changeSkin(None)
return context.Base_redirect('view', keep_items=dict(
              portal_status_message=N_("Report Started")))
