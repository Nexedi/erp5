from ZTUtils import make_query
portal = context.getPortalObject()

query = make_query({
    'response_type': 'code',
    'client_id': portal.portal_preferences.getPreferredGoogleClientId(),
    'redirect_uri': "{0}/ERP5Site_receiveGoogleCallback".format(portal.absolute_url()),
    'scope': 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email'
})

context.REQUEST.RESPONSE.redirect('''https://accounts.google.com/o/oauth2/auth?''' + query)
