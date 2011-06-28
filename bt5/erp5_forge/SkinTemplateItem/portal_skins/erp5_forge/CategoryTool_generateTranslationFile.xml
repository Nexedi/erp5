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

"""Return a po file from a spreadsheet of categories."""\n
from Products.ERP5Type.Message import translateString\n
from Products.ERP5Type.Document import newTempBase\n
\n
# Initialise some general variables\n
detailed_report_result = []\n
detailed_report_append = detailed_report_result.append\n
category_dict = {}\n
translation_dict = {}\n
translated_attributes_list = ["title", "description", "short_title"]\n
import_filename = getattr(import_file, \'filename\', \'?\')\n
request = container.REQUEST\n
response = request.RESPONSE\n
\n
if import_filename==\'\':\n
  raise ValueError, "You must upload a file"\n
\n
def addReportLine(error, category, message):\n
  report_line = newTempBase(context, \'item\')\n
  report_line.edit(field_type=error, field_category=category, field_message=message)    \n
  detailed_report_append(report_line)\n
\n
def invalid_category_spreadsheet_handler(message):\n
  # action taken when an invalid spreadsheet is provided.\n
  # we *raise* a Redirect, because we don\'t want the transaction to succeed\n
  # note, we could make a dialog parameter to allow import invalid spreadsheet:\n
  raise \'Redirect\', \'%s/view?portal_status_message=%s\' % (\n
                         context.portal_categories.absolute_url(),\n
                         message)\n
\n
category_list_mapping = context.Base_getCategoriesSpreadSheetMapping(import_file,\n
                                    invalid_spreadsheet_error_handler=invalid_category_spreadsheet_handler)\n
\n
if category_list_mapping.has_key(\'error_list\'):\n
  context.REQUEST.other[\'category_import_report\'] = initial_category_list_mapping[\'error_list\']\n
  return context.CategoryTool_viewImportReport()\n
\n
\n
\n
#Process on each category\n
for base_category, category_list in category_list_mapping.items():\n
  for category in category_list:\n
    #Take only needed attributes\n
    for attribute in translated_attributes_list:\n
      #Test attribute exist\n
      if category.has_key(attribute) and category.has_key(translation_prefix+attribute):\n
        initial_value = category.get(attribute,\'\').strip().replace(\'"\',"\'")\n
        if initial_value != \'\':\n
          translate_value = category.get(translation_prefix+attribute,\'\').strip().replace(\'"\',"\'")\n
          if translate_value != \'\':\n
            if translation_dict.has_key(initial_value):\n
              #Test any duplicate  translation (\'car\' can\'t be translated to \'voiture\' and \'auto\', \n
              #user should be choice \'voiture\' or \'car\')\n
              if translation_dict[initial_value] != translate_value: \n
                message = "\'%s\' can\'t be translated by \'%s\'. It\'s already translated by \'%s\'" % (initial_value, translate_value, translation_dict[initial_value])\n
                addReportLine(error="Duplicate",category=category[\'path\'], message=message)\n
            else:\n
              translation_dict[initial_value] = translate_value\n
          else:\n
            message = "No translation for attribute " + attribute\n
            addReportLine(error="No translation",category=category[\'path\'], message=message)  \n
\n
if len(translation_dict) == 0:\n
  message = "Empty File"\n
  addReportLine(error="No Results",category="General", message=message)\n
\n
if error_report and len(detailed_report_result) > 0:\n
  context.REQUEST.other[\'category_import_report\'] = detailed_report_result\n
  return context.CategoryTool_viewImportReport()\n
\n
#No error, we build the file\n
po_data = ""\n
for msgid, msgstr in translation_dict.items():\n
  po_data += \'msgid "%s"\\nmsgstr "%s"\\n\\n\' % (msgid, msgstr)\n
\n
filename = "%s%s.po" % (translation_prefix,"".join(import_filename.split(\'.\')[:-1]))\n
document = context.portal_contributions.newContent(data=po_data,\n
                                                  temp_object=1,\n
                                                  filename=filename)\n
\n
response.setHeader(\'Content-disposition\', \'attachment; filename="%s"\' % filename)\n
return document.index_html(request, response, None)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>import_file, error_report, translation_prefix, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CategoryTool_generateTranslationFile</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
