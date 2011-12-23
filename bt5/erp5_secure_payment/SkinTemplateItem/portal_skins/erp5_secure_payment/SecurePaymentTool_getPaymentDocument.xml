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
            <value> <string>"""Central place to get document used to do the payment.\n
By default, use payment transaction. You can change this by override this script"""\n
\n
return context.getPortalObject()\\\n
      .SecurePaymentTool_createPaymentDocument(**kw)\n
\n
# XXX DO WE NEED ANY COOKIE ?\n
# I (Seb) removed it, I don\'t understand why this is needed. Also\n
# because of this cookie, if there is any issue with the payment,\n
# it is totally impossible to do another payment without resetting cookies !\n
# most users don\'t even know that cookies exists, so this is really bad.\n
\n
#request = context.REQUEST\n
#expire_timeout_days = 90\n
#session_id = request.get(\'session_id\', None)\n
#portal_sessions = context.portal_sessions\n
\n
#if session_id is None:\n
  ### first call so generate session_id and send back via cookie\n
  #now = DateTime()\n
  #session_id = context.Base_generateSessionID(max_long=20)\n
  #request.RESPONSE.setCookie(\'session_id\', session_id, expires=(now +expire_timeout_days).fCommon(), path=\'/\')\n
\n
#if action==\'reset\':\n
  ### reset cart \n
  #portal_sessions.manage_delObjects(session_id)\n
#else:\n
  ### take payment transaction for this customer\n
  #session = portal_sessions[session_id]\n
  #payment_document_key = \'payment_document\'\n
  #if not payment_document_key in session:\n
    #payment_document = context.getPortalObject()\\\n
      #.SecurePaymentTool_createPaymentDocument(**kw)\n
    #session[payment_document_key] = payment_document.getRelativeUrl()\n
\n
  ### return just a part of session for payment transaction\n
  #payment_document = context.restrictedTraverse(session[payment_document_key])\n
  #return payment_document\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>action=\'\', **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SecurePaymentTool_getPaymentDocument</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
