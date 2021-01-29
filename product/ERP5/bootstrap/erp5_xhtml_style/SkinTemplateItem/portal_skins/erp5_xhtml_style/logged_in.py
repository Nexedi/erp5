portal = context.getPortalObject()
translateString = portal.Base_translateString
if portal.portal_skins.updateSkinCookie():
  portal.setupCurrentSkin()
url = REQUEST.get("came_from")
if portal.portal_membership.isAnonymousUser():
  RESPONSE.expireCookie("__ac", path="/")
  keep_item_dict = {
    'portal_status_message': translateString("Login and/or password is incorrect."),
  }
  if url:
    keep_item_dict['came_from'] = url
  # handle authentication policy requests parameters
  if REQUEST.get('is_user_account_blocked'):
    keep_item_dict['portal_status_message'] = translateString('Account is blocked.')
  if REQUEST.get('is_user_account_password_expired'):
    keep_item_dict['portal_status_message'] = translateString('Password is expired.')
    if portal.portal_preferences.isPreferredSystemRecoverExpiredPassword():
      keep_item_dict['portal_status_message'] = translateString(
        'Password is expired. You will soon receive an email with details about how you can recover it.')
  context.Base_redirect(
    form_id='login_form',
    keep_items=keep_item_dict,
  )
  return
if not url:
  url = context.absolute_url()

if REQUEST.get('is_user_account_password_expired_expire_date'):
  return context.Base_redirect(
    'ERP5Site_viewNewPersonCredentialUpdateDialog',
    keep_items={
      'cancel_url': url,
      'portal_status_message': translateString(
          'Your password will expire at {date}. '
          'You are advised to change it as soon as possible.',
          mapping={'date':
            portal.Base_FormatDate(
              REQUEST.get('is_user_account_password_expired_expire_date'),
              hour_minute=1)})})

topmost_url_document = context.Base_getURLTopmostDocumentValue()
if not topmost_url_document.isURLAncestorOf(url):
  return topmost_url_document.Base_redirect(
    keep_items={
      'portal_status_message': translateString('Redirection to an external site prevented.'),
    }
  )
return RESPONSE.redirect(url)
