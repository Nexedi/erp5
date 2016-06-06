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
            <value> <string encoding="cdata"><![CDATA[

from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
current_object = context.getObject()\n
assignment_list = current_object.getDestinationFormRelatedValueList()\n
for assignment in assignment_list:\n
  if current_object.getPortalType()==\'M0\':\n
    legal_form = current_object.getLegalForm().lower()\n
  elif current_object.getPortalType()==\'M2\':\n
    legal_form = current_object.getNewLegalForm().lower()\n
  else:\n
    portal = context.getPortalObject()\n
    rccm = current_object.getCorporateRegistrationCode()\n
    pers_result = context.ERP5RegistryOhada_getRelatedPersonList()\n
    if len(pers_result) < 1:\n
      raise ValidationFailed, \'There is no Person corresponding to the corporate registration code %s\' % rccm\n
    person = pers_result[0].getObject()\n
    #legal_form = person.getSocialForm()\n
  if assignment.getFunction()==\'entreprise/associe\' :\n
    if legal_form == \'gie\':\n
      assignment.getFunctionValue().setTitle(\'Membre du GIE\')\n
    elif legal_form == \'sarl\':\n
      assignment.getFunctionValue().setTitle(\'Associé de SARL\')\n
    elif legal_form == \'sa\': \n
      assignment.getFunctionValue().setTitle(\'Actionnaire de SA\')\n
\n
return assignment_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
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
            <value> <string>Form_getDestinationFormRelatedValueList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
