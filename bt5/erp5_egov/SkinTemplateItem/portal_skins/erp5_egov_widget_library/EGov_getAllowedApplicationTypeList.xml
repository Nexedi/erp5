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
            <value> <string>portal_type_list = context.portal_catalog(portal_type=\'EGov Type\')\n
portal_type_anon_list = ()\n
portal_type_auth_list = ()\n
for portal_type in portal_type_list:\n
   if portal_type.getObject().getStepAuthentication():\n
      portal_type_auth_list += (portal_type.getObject().getTitle(),)\n
   else:\n
      portal_type_anon_list += (portal_type.getObject().getTitle(),)\n
\n
if context.portal_membership.isAnonymousUser():\n
  return portal_type_anon_list\n
return portal_type_auth_list\n
\n
\n
\n
\n
portal = context.getPortalObject()\n
\n
# Be sure that the company haven\'t submitted the current form yet\n
# If not do not permit to submit another one\n
portal_type=\'Declaration TVA\'\n
user_name = portal.portal_membership.getAuthenticatedMember().getUserName()\n
user_obj = portal.ERP5Site_getPersonObjectFromUserName(user_name)\n
if user_obj:\n
  vat_code = user_obj.getCareerSubordinationValue().getVatCode()\n
  if len(vat_code)==7:\n
    vat_code=\'00%s\' % vat_code\n
\n
\n
  # Get the imposition periode from sigtas datas\n
  sigtas_information = context.DeclarationTVA_zGetSIGTASInformation(ninea_number=vat_code)\n
  if len(sigtas_information):\n
    sigtas_line = sigtas_information[0]\n
    imposition_period=sigtas_line.imposition_period\n
\n
    declaration_list = portal.declaration_tva_module.contentValues(filter={\'portal_type\': portal_type, })\n
    for dec in declaration_list:\n
      if dec.getValidationState() in (\'submitted\', \'assigned\', \'archived\', \'processed\') and dec.imposition_period==imposition_period and dec.ninea_1_part_1==vat_code:\n
        return ( \'Declaration TVA Empty\', \'Declaration TVA Amendment\')\n
    \n
    return (\'Declaration TVA\', \'Declaration TVA Empty\', \'Declaration TVA Amendment\')\n
        \n
       \n
        \n
           \n
    """\n
    declaration_list = portal.declaration_tva_module.portal_catalog(portal_type=portal_type,\n
                                                                    vat_code=vat_code,\n
                                                                    imposition_period=imposition_period)\n
    context.log(\'%s - %s - %s\' % (vat_code,imposition_period,portal_type))\n
    l=[(d.getId(),d.getCompanyName()) for d in declaration_list]\n
    context.log(l)\n
\n
    if len(declaration_list)==0:\n
      return ( \'Declaration TVA\', \'Declaration TVA Empty\', \'Declaration TVA Amendment\', \'Subscription Form\') # is not implemented yet \'Declaration TOB\', \'Mandate Form\',\n
    else:\n
      return (\'Declaration TVA Empty\', \'Declaration TVA Amendment\', \'Subscription Form\')\n
    """\n
  else:\n
    return (\'Subscription Form\', )\n
else:\n
  return (\'Subscription Form\', )\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>EGov_getAllowedApplicationTypeList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
