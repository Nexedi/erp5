portal = context.getPortalObject()
#We must be anonymous to no create conflict in security
if not portal.portal_membership.isAnonymousUser():
  return context.WebSite_logout(message="You have been disconnect from your previous document. Please resend your file.")

#Create reference
reference = context.WebSection_generateRandomReference()

#Create new user with this reference
module = portal.getDefaultModule('Person')
person = module.newContent(portal_type='Person',
                  reference=reference,
                  description=context.REQUEST.get('HTTP_X_FORWARDED_FOR','Found no ip'),
                 )
person.setGroup(reference)
assignment = person.newContent(portal_type="Assignment", group="cloudooo_group")
assignment.open()
person.validate()

document = context.Base_contribute(file=file,
                                   url=None,
                                   portal_type=None,
                                   classification="personal/private",
                                   synchronous_metadata_discovery=None,
                                   redirect_to_document=False,
                                   attach_document_to_context=False,
                                   use_context_for_container=False,
                                   redirect_url=None,
                                   cancel_url=None,
                                   batch_mode=False,
                                   max_repeat=0,
                                   editable_mode=1,
                                   follow_up_list=None,
                                   user_login=reference,
                                   reference=reference
                                  )

#XXX-Conflict between contributor property and contributor property. We must use value to be sure to use the property
document.setContributorValue(person);
original_name = document.getSourceReference()
if original_name:
  dot_position = original_name.rfind('.')
  if dot_position > 0:
    document.setTitle(original_name[0:dot_position])
  else:
    document.setTitle(original_name)

#Set document in release_alive state to allow assignee to see and modify the document
document.releaseAlive()

#Get param and key to connect the user
param, key = person.Person_getEncryptedLogin()

#Store real path in session for Document_getJSONInformation
portal_sessions = context.portal_sessions
session = portal_sessions[reference]
session['document_url'] = document.getRelativeUrl()

#Redirect the user on waiting conversion dialog
context.Base_redirect('WebSection_viewWaitingConversion',
                      keep_items={'portal_status_message': "Please wait : we are converting your file",
                                  param: key})
