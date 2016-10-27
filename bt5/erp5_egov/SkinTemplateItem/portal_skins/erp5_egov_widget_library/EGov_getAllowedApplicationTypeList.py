portal_type_list = context.portal_catalog(portal_type='EGov Type')
portal_type_anon_list = ()
portal_type_auth_list = ()
for portal_type in portal_type_list:
   if portal_type.getObject().getStepAuthentication():
      portal_type_auth_list += (portal_type.getObject().getTitle(),)
   else:
      portal_type_anon_list += (portal_type.getObject().getTitle(),)

if context.portal_membership.isAnonymousUser():
  return portal_type_anon_list
return portal_type_auth_list




portal = context.getPortalObject()

# Be sure that the company haven't submitted the current form yet
# If not do not permit to submit another one
portal_type='Declaration TVA'
user_obj = portal.portal_membership.getAuthenticatedMember().getUserValue()
if user_obj:
  vat_code = user_obj.getCareerSubordinationValue().getVatCode()
  if len(vat_code)==7:
    vat_code='00%s' % vat_code


  # Get the imposition periode from sigtas datas
  sigtas_information = context.DeclarationTVA_zGetSIGTASInformation(ninea_number=vat_code)
  if len(sigtas_information):
    sigtas_line = sigtas_information[0]
    imposition_period=sigtas_line.imposition_period

    declaration_list = portal.declaration_tva_module.contentValues(filter={'portal_type': portal_type, })
    for dec in declaration_list:
      if dec.getValidationState() in ('submitted', 'assigned', 'archived', 'processed') and dec.imposition_period==imposition_period and dec.ninea_1_part_1==vat_code:
        return ( 'Declaration TVA Empty', 'Declaration TVA Amendment')
    
    return ('Declaration TVA', 'Declaration TVA Empty', 'Declaration TVA Amendment')
        
       
        
           
    """
    declaration_list = portal.declaration_tva_module.portal_catalog(portal_type=portal_type,
                                                                    vat_code=vat_code,
                                                                    imposition_period=imposition_period)
    context.log('%s - %s - %s' % (vat_code,imposition_period,portal_type))
    l=[(d.getId(),d.getCompanyName()) for d in declaration_list]
    context.log(l)

    if len(declaration_list)==0:
      return ( 'Declaration TVA', 'Declaration TVA Empty', 'Declaration TVA Amendment', 'Subscription Form') # is not implemented yet 'Declaration TOB', 'Mandate Form',
    else:
      return ('Declaration TVA Empty', 'Declaration TVA Amendment', 'Subscription Form')
    """
  else:
    return ('Subscription Form', )
else:
  return ('Subscription Form', )
