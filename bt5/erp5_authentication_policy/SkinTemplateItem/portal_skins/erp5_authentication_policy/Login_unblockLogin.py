from Products.ZSQLCatalog.SQLCatalog import Query

portal = context.getPortalObject()
portal_preferences = portal.portal_preferences

if not portal.portal_preferences.isAuthenticationPolicyEnabled():
  # no policy, no sense to unblock account
  return context.Base_redirect(form_id=form_id)

now = DateTime()
one_second = 1/24.0/60.0/60.0
check_duration = portal_preferences.getPreferredAuthenticationFailureCheckDuration()
check_time = now - check_duration*one_second

# acknowledge last authentication events for user
kw = {'portal_type': 'Authentication Event',
      'default_destination_uid': context.getUid(),
      'creation_date': Query(creation_date = check_time,
                             range='min'),
      'validation_state' : 'confirmed',
      'sort_on' : (('creation_date', 'ASC',),),
      }

authentication_event_list = [x.getObject() for x in portal.portal_catalog(**kw)]

for authentication_event in authentication_event_list:
  authentication_event.acknowledge(comment='User account unblocked.')

if not batch_mode:
  message = context.Base_translateString('User Login unblocked.')
  if cancel_url is None:
    return context.Base_redirect(form_id=form_id, keep_items={'portal_status_message': message})
  else:
    context.REQUEST.RESPONSE.redirect('%s?portal_status_message=%s' %(cancel_url, message))

return
