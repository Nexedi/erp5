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
            <value> <string>request = context.REQUEST\n
request_form = context.REQUEST.form\n
from ZTUtils import make_query\n
portal = context.getPortalObject()\n
title = context.getTitle(\'Unknown\')\n
translateString = context.Base_translateString\n
web_page_module = context.web_page_module\n
\n
# Find the applicable language\n
language = portal.Localizer.get_selected_language()\n
\n
# Create a new empty page\n
web_page = web_page_module.newContent(portal_type = \'Web Page\', \n
                                      title="New Page of Section %s" % title,\n
                                      version="1", language=language)\n
\n
\n
# Copy categories into new Web Page\n
category_list = context.getMembershipCriterionCategoryList()\n
web_page.setCategoryList(web_page.getCategoryList() + category_list)\n
\n
\n
# Return the new page in the section context\n
keep_items = dict(editable_mode=1,\n
              portal_status_message=translateString("New Web Page of section ${web_section}.",\n
              mapping = dict(web_section=title)))\n
\n
request_form.update(keep_items)\n
message = make_query(dict([(k, v) for k, v in request_form.items() if k and v is not None]))\n
\n
redirect_url = \'%s/%s/view?%s\' % (\n
            context.absolute_url(), web_page.getRelativeUrl(),message)\n
\n
# return to the new page in the section context\n
return context.REQUEST.RESPONSE.redirect(redirect_url)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSection_createNewWebPage</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
