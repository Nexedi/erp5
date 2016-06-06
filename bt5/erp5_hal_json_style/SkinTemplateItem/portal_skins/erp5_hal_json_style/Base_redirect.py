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

"""\n
   This script factorises code required to redirect to the appropriate\n
   page from a script. It should probably be extended, reviewed and documented\n
   so that less code is copied and pasted in dialog scripts.\n
\n
   TODO: improve API and extensively document. ERP5Site_redirect may \n
   be redundant.\n
"""\n
from ZTUtils import make_query\n
request_form = context.REQUEST.form\n
request_form.update(kw)\n
request_form = context.ERP5Site_filterParameterList(request_form)\n
request_form.update(keep_items)\n
\n
if form_id == \'view\':\n
  redirect_url = "%s/ERP5Document_getHateoas" % context.absolute_url()\n
else:\n
  redirect_url = \'%s/%s\' % (context.absolute_url(), form_id)\n
\n
parameters = make_query(dict([(k, v) for k, v in request_form.items() if k and v is not None]))\n
if len(parameters):\n
  if \'?\' in redirect_url:\n
    separator = \'&\'\n
  else:\n
    separator = \'?\'\n
  redirect_url = \'%s%s%s\' % (redirect_url, separator, parameters)\n
\n
\n
# XXX Allow CORS\n
response = context.REQUEST.RESPONSE\n
context.Base_prepareCorsResponse(RESPONSE=response)\n
# http://en.wikipedia.org/wiki/Post/Redirect/Get\n
response.setStatus(201)\n
response.setHeader("X-Location", "urn:jio:get:%s" % context.getRelativeUrl())\n
return\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'view\', keep_items={}, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_redirect</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
