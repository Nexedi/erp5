portal = context.getPortalObject()
current_object = context.getObject()
rccm = current_object.getCorporateRegistrationCode()
form_list = []
if not rccm:
  return form_list
form_portal_type_list = context.ERP5RegistryOhada_getFormPortalTypeList()  
form_result = portal.portal_catalog(portal_type=form_portal_type_list, 
                                    corporate_registration_code=rccm,)
form_list = [form.getObject() for form in form_result]
return form_list
