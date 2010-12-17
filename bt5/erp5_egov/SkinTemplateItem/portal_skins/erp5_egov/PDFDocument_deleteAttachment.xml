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

request=context.REQUEST\n
portal = context.getPortalObject()\n
N_ = portal.Base_translateString\n
\n
if id_list == None:\n
  message = N_("Please+select+one+or+more+items+to+delete+first.")\n
  qs = \'?portal_status_message=%s\' % message\n
  return request.RESPONSE.redirect( context.absolute_url() + \'/\' + form_id + qs )\n
\n
if not same_type(id_list, []):\n
  id_list=[id_list,]\n
\n
if len(id_list) >1:\n
  message = N_("Please+select+only+one+item+to+delete.")\n
  qs = \'?portal_status_message=%s\' % message\n
  return request.RESPONSE.redirect( context.absolute_url() + \'/\' + form_id + qs )\n
\n
object = getattr(context, id_list[0], None)\n
\n
portal.portal_workflow.doActionFor(object, \'delete_action\')\n
message = N_(\'Attachment ${file_name} has been deleted\', mapping = { \'file_name\': \'"%s"\' % file_name})\n
qs = \'?portal_status_message=%s\' % message\n
return request.RESPONSE.redirect( context.absolute_url() + \'/\' + form_id + qs )\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>id_list=None, form_id=\'view\', file_name=\'\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PDFDocument_deleteAttachment</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
