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
            <value> <string>from Products.ERP5Type.Message import Message\n
from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
\n
object = state_change[\'object\']\n
\n
# use of the constraint\n
vliste = object.checkConsistency()\n
object.log(\'vliste\', vliste)\n
if len(vliste) != 0:\n
  raise ValidationFailed, (vliste[0].getMessage(),)\n
\n
\n
# first check if we have line defined\n
if len(object.objectValues(portal_type=\'Cash Delivery Line\')) == 0:\n
  msg = Message(domain="ui", message="No line defined on document.")\n
  raise ValidationFailed, (msg,)\n
       \n
dest = object.getDestinationValue()\n
if dest is None or \'encaisse_des_billets_retires_de_la_circulation\' in dest.getRelativeUrl():\n
  msg = Message(domain="ui", message="Wrong Destination Selected.")\n
  raise ValidationFailed, (msg,)\n
\n
# check again that we are in the good accounting date\n
object.Baobab_checkCounterDateOpen(site=dest, date=object.getStartDate())\n
\n
\n
# check between letter and destination site codification\n
# Make sure objects are Banknotes\n
if \'transit\' not in dest.getRelativeUrl():\n
  first_movement = object.Delivery_getMovementList(portal_type=[\'Cash Delivery Line\',\'Cash Delivery Cell\'])[0]\n
  if first_movement.getResourceValue().getPortalType()==\'Banknote\':\n
    line_letter = first_movement.getEmissionLetter()\n
    if line_letter.lower() != dest.getCodification()[0].lower():\n
      msg = Message(domain="ui", message="Letter defined on line do not correspond to destination site.")\n
      raise ValidationFailed, (msg,)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>checkDestination</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
