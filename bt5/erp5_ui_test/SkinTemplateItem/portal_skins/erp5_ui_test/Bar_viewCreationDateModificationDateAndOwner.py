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

portal = context.getPortalObject()\n
#default_time_zone = portal.portal_preferences.getPreferredTimeZone()\n
preferred_date_order = portal.portal_preferences.getPreferredDateOrder()\n
\n
def format_date(date):\n
  # XXX modification date & creation date are still in server timezone.\n
  #   See merge request !17\n
  #\n
  # if default_time_zone:\n
  #   date = date.toZone(default_time_zone)\n
  if preferred_date_order == \'dmy\':\n
    return "%s/%s/%s&nbsp;&nbsp;&nbsp;%s" % (date.dd(), date.mm(), date.year(), date.TimeMinutes())\n
  if preferred_date_order == \'mdy\':\n
    return "%s/%s/%s&nbsp;&nbsp;&nbsp;%s" % (date.mm(), date.dd(), date.year(), date.TimeMinutes())\n
  # ymd\n
  return "%s/%s/%s&nbsp;&nbsp;&nbsp;%s" % (date.year(), date.mm(), date.dd(), date.TimeMinutes())\n
\n
creation_date = format_date(context.getCreationDate())\n
modification_date = format_date(context.getModificationDate())\n
owner = context.Base_getOwnerTitle()\n
return """\n
<html>\n
  <body>\n
    <div id="creation_date">{creation_date}</div>\n
    <div id="modification_date">{modification_date}</div>\n
    <div id="owner">{owner}</div>\n
  </body>\n
</html>\n
""".format(\n
  creation_date=creation_date,\n
  modification_date=modification_date,\n
  owner=owner)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Bar_viewCreationDateModificationDateAndOwner</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
