## Script (Python) "secure_redirect"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from ZTUtils import make_query

request = context.REQUEST

if context.portal_membership.isAnonymousUser():
  form_method = 'custommer_registration'
else:
  form_method = 'login_and_addToCart'

request.RESPONSE.redirect( '%s/%s?%s' % (context.secure_absolute_url(), form_method, make_query(request.form)) )
