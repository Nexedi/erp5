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
            <value> <string>from ZODB.POSException import ConflictError\n
from Products.ERP5.Document.Document import ConversionError\n
from Products.ERP5Type.Log import log\n
\n
message = None\n
try:\n
  return context.updateBaseMetadata(**kw)\n
except ConflictError:\n
  raise\n
except ConversionError, e:\n
  message = \'Conversion Error: %s\' % (str(e) or \'undefined.\')\n
except Exception, e:\n
  message = \'Problem: %s\' % (repr(e) or \'undefined.\')\n
except:\n
  message = \'Problem: unknown\'\n
\n
# reach here, then exception was raised, message must be logged in workflow\n
# do not simply raise but rather change external processing state\n
# so user will see something is wrong. As usually updateBaseMetadata is called\n
# after convertToBaseFormat it\'s possible that object is in conversion failed state \n
isTransitionPossible = context.getPortalObject().portal_workflow.isTransitionPossible\n
if isTransitionPossible(context, \'conversion_failed\'):\n
  # mark document as conversion failed if not already done by convertToBaseFormat\n
  context.conversionFailed(comment=message)\n
else:\n
  # just save problem message in workflow history\n
  context.processConversionFailed(comment=message)\n
log(\'%s %s\' %(context.getRelativeUrl(), message))\n
return message\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Document_tryToUpdateBaseMetadata</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
