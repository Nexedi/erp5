## Script (Python) "register_and_addToCart"
##bind container=container
##bind context=context
##bind namespace=_
##bind script=script
##bind subpath=traverse_subpath
##parameters=password='password', confirm='confirm'
##title=Register a user
##
REQUEST=context.REQUEST
portal_properties = context.portal_properties
portal_registration = context.portal_registration

# Validate Login Name
if not portal_registration.isMemberIdAllowed(REQUEST['username']):
  failMessage = 'Bad name. Login names must only contain letters (without accents) and numbers'
  REQUEST.set( 'portal_status_message', failMessage )
  return context.custommer_registration( context, REQUEST, portal_status_message=failMessage )

if not portal_properties.validate_email:
  failMessage = portal_registration.testPasswordValidity(password, confirm)
  if failMessage:
      REQUEST.set( 'portal_status_message', failMessage )
      return context.custommer_registration( context, REQUEST, portal_status_message=failMessage )

failMessage = portal_registration.testPropertiesValidity(REQUEST)

if failMessage:
    REQUEST.set( 'portal_status_message', failMessage )
    return context.custommer_registration( context, REQUEST, portal_status_message=failMessage )
else:
    REQUEST.set('pref_currency','EUR')
    password=REQUEST.get('password') or portal_registration.generatePassword()
    portal_registration.addMember(REQUEST['username'], password, properties=REQUEST)

    if portal_properties.validate_email or REQUEST.get('mail_me', 0):
        portal_registration.registeredNotify(REQUEST['username'])

    REQUEST.set('__ac_name',REQUEST['username'])
    REQUEST.set('__ac_password',password)
    #context.cookie_authentication.modifyRequest(REQUEST, None)
    return context.registered_before_addToCart( context, REQUEST )
