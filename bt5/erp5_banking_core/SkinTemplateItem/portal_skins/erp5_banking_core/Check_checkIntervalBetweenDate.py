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

from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
from Products.ERP5Type.Message import Message\n
from Products.ERP5Type.DateUtils import getIntervalBetweenDates\n
\n
if stop_date is None:\n
  from DateTime import DateTime\n
  stop_date = DateTime().Date()\n
\n
resource_title = resource.getTitle()\n
#context.log("date %s %s" %(start_date, stop_date), "title = %s" %resource_title)\n
\n
if \'compte\' in resource_title:\n
  interval = getIntervalBetweenDates(start_date,stop_date)\n
  #context.log("interval", interval)\n
  if interval[\'year\'] == 3:\n
    if interval[\'month\'] > 0 or interval["day"] > 0:\n
      msg = Message(domain=\'ui\', message="Check $check is more than 3 years old.",\n
                    mapping={"check" : check_nb})\n
      raise ValidationFailed, (msg,)\n
  elif interval[\'year\'] > 3:\n
    msg = Message(domain=\'ui\', message="Check $check is more than 3 years old.",\n
                  mapping={"check" : check_nb})\n
    raise ValidationFailed, (msg,)\n
\n
elif \'virement\' in resource_title:\n
  interval = getIntervalBetweenDates(start_date, stop_date)\n
  #context.log("interval", interval)\n
  if interval[\'month\'] == 3:\n
    if interval["day"] > 0:\n
      msg = Message(domain=\'ui\', message="Check $check is more than 3 month old.",\n
                    mapping={"check" : check_nb})\n
      raise ValidationFailed, (msg,)\n
  elif interval[\'month\'] > 3 or interval[\'year\'] > 0:\n
    msg = Message(domain=\'ui\', message="Check $check is more than 3 month old.",\n
                  mapping={"check" : check_nb})\n
    raise ValidationFailed, (msg,)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>resource, start_date, stop_date, check_nb</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Check_checkIntervalBetweenDate</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
