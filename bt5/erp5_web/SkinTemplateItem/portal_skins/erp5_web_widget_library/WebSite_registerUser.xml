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
  Script called by user registration form; checks if all required parameters\n
  are supplied, handles errors, calls WebSite_createUser to actually\n
  create Person.\n
  Will send email with password info.\n
\n
  XXX - redirect, translation of dialogs\n
"""\n
from Products.ERP5Type.Log import log\n
req = context.REQUEST\n
\n
# check if everything was filled\n
fields = (\'email\', \'email_repeated\', \'group\', \'function\', \'site\', \'first_name\', \'last_name\')\n
missing_string = \'\'\n
kwargs = {}\n
for f in fields:\n
  value = req.get(\'your_\' + f)\n
  if not value:\n
    missing_string += \'&missing:list=\' + f\n
  else:\n
    kwargs[f] = value\n
returned_params = \'&\'.join([f+\'=\'+kwargs[f] for f in kwargs])\n
log(returned_params)\n
if missing_string:\n
  params = returned_params + \'&\' + missing_string + \'&portal_status_message=You did not fill all the required fields. See below to find out which fields still have to be filled.\'\n
  log(params)\n
  return req.RESPONSE.redirect(context.absolute_url()+\'?\'+params)\n
if req.get(\'your_email\') != req.get(\'your_email_repeated\'):\n
  missing_string += \'&missing:list=email&missing:list=email_repeated\'\n
  params = returned_params + \'&\' + missing_string + \'&portal_status_message=You entered two different email addresses. Please make sure to enter the same email address in the fields Email Address and Repeat Email Address.\'\n
  return req.RESPONSE.redirect(context.absolute_url()+\'?\'+params)\n
\n
# create a user\n
log(kwargs)\n
try:\n
  user = context.WebSite_createUser(**kwargs)\n
  log(user)\n
  msg = \'Thank you for registering. Your password will be sent to the email address that you provided once your account has been validated by the appropriate department.\'\n
except Exception, e:\n
  msg = str(e)\n
\n
return req.RESPONSE.redirect(context.absolute_url() + \'?portal_status_message=\'+msg)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*a, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSite_registerUser</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
