<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string>procedure_request = state_change[\'object\']\n
\n
portal_type_name = procedure_request.getProcedureTitle()\n
portal_type_name = portal_type_name.replace("\'", "")\n
portal_type_name = portal_type_name.replace(\'é\', \'e\')\n
portal_type_name = portal_type_name.replace(\'è\', \'e\')\n
portal_type_name = portal_type_name.replace(\'à\', \'a\')\n
portal_type_name = portal_type_name.replace(\'ç\', \'c\')\n
portal_type_name = portal_type_name.replace(\'ê\', \'e\')\n
portal_type_name = \' \'.join([word.capitalize() for word in portal_type_name.split(\' \')])\n
\n
## verifying if portal_type exist or not\n
\n
portal = context.getPortalObject()\n
result = portal.portal_catalog(reference=portal_type_name)\n
\n
content_type_list = [\'File\',\'Email\']\n
\n
if len(result) == 0:\n
  procedure_request.setId(portal_type_name)\n
  procedure_request.setTitle(portal_type_name)\n
  procedure_request.setTypeFactoryMethodId(\'addEGovTypeInformation\')\n
  procedure_request.setTypeAllowedContentTypeList(content_type_list)\n
  procedure_request.setTypeHiddenContentTypeList(content_type_list)\n
  procedure_request.setTypeFilterContentType(1)\n
\n
## Associate workflows with the new portal_type\n
\n
workflow_list  = (\'egov_interaction_workflow\', \'egov_universal_workflow\')\n
\n
\n
portal.EgovType_setWorkflowList(portal, portal_type_name, workflow_list)\n
\n
\n
## adding Attachments section\n
\n
if procedure_request.getStepAttachment():\n
  procedure_request.newContent(reference=\'attachment\',\n
                               title=\'Attachments\',\n
                               action_type=\'object_view\',\n
                               action=\'string:${object_url}/PDFDocument_viewAttachmentList\',\n
                               float_index=2.0,\n
                               portal_type = \'Action Information\')\n
\n
  procedure_request.newContent(reference=\'history\',\n
                               title=\'History\',\n
                               action_type=\'object_view\',\n
                               action=\'string:${object_url}/PDFDocument_viewHistory\',\n
                               float_index=4.0,\n
                               portal_type = \'Action Information\')\n
\n
  procedure_request.newContent(reference=\'print\',\n
                               title=\'Print\',\n
                               action_type=\'object_print\',\n
                               action=\'string:${object_url}/PDFType_viewAsPdf\',\n
                               float_index=7.0,\n
                               portal_type = \'Action Information\')\n
\n
\n
\n
## Create module containing portal_types if it doesn\'t exists\n
\n
portal_type_module_name =  portal_type_name + \' Module\'\n
result = portal.portal_catalog(reference=portal_type_module_name)\n
\n
type_allowed_content_type_list = [portal_type_name,]\n
\n
if len(result) == 0:\n
  portal_type_module = portal.portal_types.newContent(id=portal_type_module_name,\n
                                      title=portal_type_module_name,\n
                                      portal_type=\'Base Type\',\n
                                      type_acquire_local_role = 1,\n
                                      type_filter_content_type = 1,\n
                                      type_factory_method_id=\'addFolder\',\n
                                      type_allowed_content_type_list=type_allowed_content_type_list,\n
                                      type_group_list=[\'module\',],)\n
  portal_type_module.newContent(reference=\'view\',\n
                         title=\'Form List\',\n
                         action_type=\'object_list\',\n
                         action=\'string:${object_url}/Folder_viewEgovContentList\',\n
                         float_index=1,\n
                         portal_type = \'Action Information\')\n
\n
  procedure_target = procedure_request.getProcedureTarget()\n
  procedure_organisation_direction = procedure_request.getOrganisationDirectionService()\n
  procedure_publication_section =  procedure_request.getProcedurePublicationSection()\n
  procedure_step_subscription = procedure_request.getStepSubscription()\n
  \n
  citizen_category_list = [\'role/citoyen\', \'role/citoyen/national\', \'role/citoyen/etranger\']\n
  company_category_list = [\'role/entreprise\', \'role/entreprise/agence\', \'role/entreprise/siege\', \'role/entreprise/succursale\']\n
  madatary_category_list = [\'function/entreprise/mandataire\', \'role/entreprise\']\n
  procedure_publication_section_category = \'publication_section/%s\' % procedure_publication_section\n
  \n
  # If procedure needs subcription add the publication_section in role_category_list\n
  if procedure_step_subscription:\n
    citizen_category_list.append(procedure_publication_section_category)\n
    company_category_list.append(procedure_publication_section_category)\n
    madatary_category_list.append(procedure_publication_section_category)\n
\n
  if procedure_target :\n
    if procedure_target == "tous":\n
      portal_type_module.newContent(portal_type=\'Role Information\',\n
\t\t      title=\'Citizens Role Information\',\n
\t\t      role_name=\'Agent\',\n
\t\t      role_category_list=citizen_category_list)\n
      portal_type_module.newContent(portal_type=\'Role Information\',\n
\t\t      title=\'Companies Role Information\',\n
\t\t      role_name=\'Agent\',\n
\t\t      role_category_list=company_category_list)\n
      portal_type_module.newContent(portal_type=\'Role Information\',\n
\t\t      title=\'Mandataries Role Information\',\n
\t\t      role_name=\'Agent\',\n
\t\t      role_category_list=madatary_category_list)\n
    if procedure_target=="citoyen":\n
      portal_type_module.newContent(portal_type=\'Role Information\',\n
\t\t      title=\'Citizens Role Information\',\n
\t\t      role_name=\'Agent\',\n
\t\t      role_category_list=citizen_category_list)\n
    if procedure_target == "entreprise":\n
      portal_type_module.newContent(portal_type=\'Role Information\',\n
\t\t      title=\'Companies Role Information\',\n
\t\t      role_name=\'Agent\',\n
\t\t      role_category_list=company_category_list)\n
      \n
  if procedure_organisation_direction is not None:\n
    portal_type_module.newContent(portal_type=\'Role Information\',\n
\t\t      title=\'Administrative Agent Role Information\',\n
\t\t      role_name=\'Auditor\',\n
\t\t      role_category_list=\'group/%s*\' % procedure_organisation_direction)\n
\n
\n
portal_type_module_id = \'_\'.join(portal_type_module_name.lower().split(\' \'))\n
\n
## create folder containing objects\n
\n
module_object = getattr(portal, portal_type_module_id, None)\n
\n
if module_object is not None:\n
  portal_type_module_object = module_object.getTypeInfo()\n
  allowed_content_type_list = portal_type_module_object.getTypeAllowedContentTypeList()\n
  allowed_content_type_list.append(portal_type_name)\n
  portal_type_module_object.setTypeAllowedContentTypeList(allowed_content_type_list)\n
else:\n
  module_object = portal.newContent( id = portal_type_module_id,\n
                              portal_type = portal_type_module_name,\n
                              title = portal_type_module_name)\n
\n
#Use _generatePerDayId as id_generator\n
module_object.setIdGenerator(\'_generatePerDayId\') \n
\n
## initialize security on the module\n
\n
module_object.EGov_setPermissionsOnEGovModule(procedure_request)\n
\n
# Allow anonymous procedure to login\n
\n
if not procedure_request.getStepAuthentication():\n
  procedure_request.EGov_enableProcedureLogin(portal_type_name)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>EGov_generatePortalType</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
