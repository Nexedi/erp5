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
            <value> <string>\'\'\'\n
  return the dict of the possible attached files\n
\'\'\'\n
require = [\'Optional\', \'Required\']\n
attachment_count = 39\n
attachement_type_dict = {}\n
portal_type_object = context.getTypeInfo()\n
\n
if portal_type_object.getStepAttachment():\n
  for i in range(attachment_count+1)[1:]:\n
    title = getattr(portal_type_object, "getAttachmentTitle%s" % i, None)\n
    requirement = getattr(portal_type_object, "getAttachmentRequired%s" % i, None)\n
    attachment = getattr(portal_type_object, "getAttachmentJustificative%s" % i, None)\n
    type = getattr(portal_type_object, "getAttachmentModel%s" % i, None)\n
    if type is not None:\n
      type = type()\n
      attachement_format = \'   Format :  %s\' % type\n
    else:\n
      type = []\n
    if requirement is not None and requirement() is not None:\n
      required = require[requirement()]\n
    if title is not None and title()!="" and attachment is not None and attachment():\n
      attachement_type_dict[title()] = {\n
           \'description\': attachement_format,\n
           \'requirement\': required,  \n
           \'outcome\'    : False,\n
           \'type\'       : type,\n
      }\n
\n
return attachement_type_dict\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args,**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PDFDocument_getApplicationIncomeDict</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
