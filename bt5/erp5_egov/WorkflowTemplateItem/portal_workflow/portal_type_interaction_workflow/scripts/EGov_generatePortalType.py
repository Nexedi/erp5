procedure_request = state_change['object']

portal_type_name = procedure_request.getProcedureTitle()
portal_type_name = portal_type_name.replace("'", "")
portal_type_name = portal_type_name.replace('é', 'e')
portal_type_name = portal_type_name.replace('è', 'e')
portal_type_name = portal_type_name.replace('à', 'a')
portal_type_name = portal_type_name.replace('ç', 'c')
portal_type_name = portal_type_name.replace('ê', 'e')
portal_type_name = ' '.join([word.capitalize() for word in portal_type_name.split(' ')])

## verifying if portal_type exist or not

portal = context.getPortalObject()
result = portal.portal_catalog(reference=portal_type_name)

content_type_list = ['File','Email']

if len(result) == 0:
  procedure_request.setId(portal_type_name)
  procedure_request.setTitle(portal_type_name)
  procedure_request.setTypeFactoryMethodId('addEGovTypeInformation')
  procedure_request.setTypeAllowedContentTypeList(content_type_list)
  procedure_request.setTypeHiddenContentTypeList(content_type_list)
  procedure_request.setTypeFilterContentType(1)

## Associate workflows with the new portal_type

workflow_list  = ('egov_interaction_workflow', 'egov_universal_workflow')


portal.EgovType_setWorkflowList(portal, portal_type_name, workflow_list)


## adding Attachments section

if procedure_request.getStepAttachment():
  procedure_request.newContent(reference='attachment',
                               title='Attachments',
                               action_type='object_view',
                               action='string:${object_url}/PDFDocument_viewAttachmentList',
                               float_index=2.0,
                               portal_type = 'Action Information')

  procedure_request.newContent(reference='history',
                               title='History',
                               action_type='object_view',
                               action='string:${object_url}/PDFDocument_viewHistory',
                               float_index=4.0,
                               portal_type = 'Action Information')

  procedure_request.newContent(reference='print',
                               title='Print',
                               action_type='object_print',
                               action='string:${object_url}/PDFType_viewAsPdf',
                               float_index=7.0,
                               portal_type = 'Action Information')



## Create module containing portal_types if it doesn't exists

portal_type_module_name =  portal_type_name + ' Module'
result = portal.portal_catalog(reference=portal_type_module_name)

type_allowed_content_type_list = [portal_type_name,]

if len(result) == 0:
  portal_type_module = portal.portal_types.newContent(id=portal_type_module_name,
                                      title=portal_type_module_name,
                                      portal_type='Base Type',
                                      type_acquire_local_role = 1,
                                      type_filter_content_type = 1,
                                      type_factory_method_id='addFolder',
                                      type_allowed_content_type_list=type_allowed_content_type_list,
                                      type_group_list=['module',],)
  portal_type_module.newContent(reference='view',
                         title='Form List',
                         action_type='object_list',
                         action='string:${object_url}/Folder_viewEgovContentList',
                         float_index=1,
                         portal_type = 'Action Information')

  procedure_target = procedure_request.getProcedureTarget()
  procedure_organisation_direction = procedure_request.getOrganisationDirectionService()
  procedure_publication_section =  procedure_request.getProcedurePublicationSection()
  procedure_step_subscription = procedure_request.getStepSubscription()
  
  citizen_category_list = ['role/citoyen', 'role/citoyen/national', 'role/citoyen/etranger']
  company_category_list = ['role/entreprise', 'role/entreprise/agence', 'role/entreprise/siege', 'role/entreprise/succursale']
  madatary_category_list = ['function/entreprise/mandataire', 'role/entreprise']
  procedure_publication_section_category = 'publication_section/%s' % procedure_publication_section
  
  # If procedure needs subcription add the publication_section in role_category_list
  if procedure_step_subscription:
    citizen_category_list.append(procedure_publication_section_category)
    company_category_list.append(procedure_publication_section_category)
    madatary_category_list.append(procedure_publication_section_category)

  if procedure_target :
    if procedure_target == "tous":
      portal_type_module.newContent(portal_type='Role Information',
		      title='Citizens Role Information',
		      role_name='Agent',
		      role_category_list=citizen_category_list)
      portal_type_module.newContent(portal_type='Role Information',
		      title='Companies Role Information',
		      role_name='Agent',
		      role_category_list=company_category_list)
      portal_type_module.newContent(portal_type='Role Information',
		      title='Mandataries Role Information',
		      role_name='Agent',
		      role_category_list=madatary_category_list)
    if procedure_target=="citoyen":
      portal_type_module.newContent(portal_type='Role Information',
		      title='Citizens Role Information',
		      role_name='Agent',
		      role_category_list=citizen_category_list)
    if procedure_target == "entreprise":
      portal_type_module.newContent(portal_type='Role Information',
		      title='Companies Role Information',
		      role_name='Agent',
		      role_category_list=company_category_list)
      
  if procedure_organisation_direction is not None:
    portal_type_module.newContent(portal_type='Role Information',
		      title='Administrative Agent Role Information',
		      role_name='Auditor',
		      role_category_list='group/%s*' % procedure_organisation_direction)


portal_type_module_id = '_'.join(portal_type_module_name.lower().split(' '))

## create folder containing objects

module_object = getattr(portal, portal_type_module_id, None)

if module_object is not None:
  portal_type_module_object = module_object.getTypeInfo()
  allowed_content_type_list = portal_type_module_object.getTypeAllowedContentTypeList()
  allowed_content_type_list.append(portal_type_name)
  portal_type_module_object.setTypeAllowedContentTypeList(allowed_content_type_list)
else:
  module_object = portal.newContent( id = portal_type_module_id,
                              portal_type = portal_type_module_name,
                              title = portal_type_module_name)

#Use _generatePerDayId as id_generator
module_object.setIdGenerator('_generatePerDayId') 

## initialize security on the module

module_object.EGov_setPermissionsOnEGovModule(procedure_request)

# Allow anonymous procedure to login

if not procedure_request.getStepAuthentication():
  procedure_request.EGov_enableProcedureLogin(portal_type_name)
