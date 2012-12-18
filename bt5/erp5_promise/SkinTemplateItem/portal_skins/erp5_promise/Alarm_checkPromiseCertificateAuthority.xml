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
            <value> <string>from Products.CMFActivity.ActiveResult import ActiveResult\n
\n
portal = context.getPortalObject()\n
\n
portal_certificate_authority = getattr(portal, \'portal_certificate_authority\', None)\n
promise_ca_path = portal.getPromiseParameter(\'portal_certificate_authority\', \'certificate_authority_path\')\n
if promise_ca_path is None:\n
  severity = 0\n
  summary = "Nothing to do."\n
  detail = ""\n
else:\n
  if portal_certificate_authority is None:\n
    severity = 1\n
    summary = "Certificate Authority Tool is not present"\n
    detail = ""\n
\n
  elif portal_certificate_authority.certificate_authority_path != promise_ca_path:\n
    severity = 1\n
    summary = "Certificate Authority Tool (OpenSSL)is not configured as Expected"\n
    detail = "Expect %s\\nGot %s" % (portal_certificate_authority.certificate_authority_path, promise_ca_path)\n
\n
  else:\n
    severity = 0\n
    summary = "Nothing to do."\n
    detail = ""\n
\n
active_result = ActiveResult()\n
active_result.edit(\n
  summary=summary, \n
  severity=severity,\n
  detail=detail)\n
\n
context.newActiveProcess().postResult(active_result)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>tag, fixit=False, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Alarm_checkPromiseCertificateAuthority</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
