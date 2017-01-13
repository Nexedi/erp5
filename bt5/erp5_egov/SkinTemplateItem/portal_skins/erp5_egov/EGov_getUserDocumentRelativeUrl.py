'''
  In case of the user is a document, return the url of the this document
'''

document_type_list = context.EGov_getAllowedFormTypeList()
portal = context.getPortalObject()

user_name = context.portal_membership.getAuthenticatedMember().getIdOrUserName()

form_list = portal.portal_catalog(\
                                portal_type=document_type_list, 
                                reference=user_name)

if len(form_list) == 0:
  return None
return form_list[0].getRelativeUrl()
