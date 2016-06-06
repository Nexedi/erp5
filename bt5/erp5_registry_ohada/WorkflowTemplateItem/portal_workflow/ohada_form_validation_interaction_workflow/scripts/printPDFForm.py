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
            <value> <string>from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
# This script is used to the automatic printing\n
# It is called after the validation of the registry officer\n
request_eform = state_change[\'object\']\n
request = request_eform.REQUEST\n
response = request.RESPONSE\n
printer_name = request_eform.portal_preferences.getPreferredPrinterName()\n
form_pdf_portal_type = request_eform.getPortalType()\n
pdf_view_name = \'%s_view%sAsPdf\' % (form_pdf_portal_type, form_pdf_portal_type)\n
form_view_pdf = getattr(request_eform, pdf_view_name, None)\n
if form_view_pdf is None:\n
  raise ValidationFailed, \'PDF view %s not found\' % pdf_view_name\n
\n
signed_pdf_name = context.addBackgroundOnPdfFile(form_view_pdf.generatePDF(),\n
                                                 getattr(context,\'signature.pdf\'))\n
\n
context.printFile(printer_name = printer_name,\n
                  file_path_to_print = signed_pdf_name,\n
                  use_ps_file = True,\n
                  nb_copy = 4)\n
\n
# print sub forms (as M0 Bis)\n
form_bis_result = request_eform.searchFolder(portal_type=\'%s Bis\' % form_pdf_portal_type)\n
form_bis_list = [form.getObject() for form in form_bis_result]\n
for form_bis in form_bis_list:\n
  form_portal_type = form_bis.getPortalType().replace(\' \', \'\')\n
  view_name = \'%s_view%sAsPdf\' % (form_portal_type, form_portal_type)\n
  form_pdf_view = getattr(form_bis, view_name, None)\n
  if form_pdf_view is None:\n
    raise ValidationFailed, \'PDF view %s not found\' % form_pdf_view\n
  form_bis_signed_pdf_name = context.addBackgroundOnPdfFile(form_pdf_view.generatePDF(),\n
                                                            getattr(context,\'signature.pdf\'))\n
  context.printFile(printer_name = printer_name,\n
                    file_path_to_print = signed_pdf_name,\n
                    use_ps_file = True,\n
                    nb_copy = 4)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
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
            <value> <string>printPDFForm</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
