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

#  - Weeks always starts at 0H of the last Sunday and finish at 0h of\n
#  the next sunday.\n
\n
from Products.ERP5Type.Message import translateString\n
from Products.ERP5Type.Document import newTempBase\n
from Products.PythonScripts.standard import url_quote\n
from string import zfill\n
\n
portal = context.getPortalObject()\n
request = context.REQUEST\n
domain_list = []\n
form_id=request.get(\'form_id\')\n
\n
selection_name = request.get(\'selection_name\')\n
params = context.portal_selections.getSelectionParamsFor(selection_name, request)\n
\n
bound_variation = params.get(\'bound_variation\', 0)\n
bound_start = DateTime(params.get(\'bound_start\', DateTime()))\n
bound_start = DateTime(bound_start.year() , bound_start.month() , bound_start.day())\n
\n
# Normalize Week. XXX this should be in preferences as well\n
while bound_start.Day() is not \'Sunday\':\n
   bound_start =  bound_start - 1\n
current_date =  bound_start + 7 * bound_variation\n
bound_stop  = current_date + 7\n
current_date =  DateTime(current_date.year() , current_date.month() , current_date.day())\n
\n
default_link_url =\'setLanePath?form_id=%s&list_selection_name=%s\' %(\n
                                 form_id, selection_name)\n
\n
# Define date format using user Preferences\n
date_order = portal.portal_preferences.getPreferredDateOrder()\n
date_format = dict(ymd=\'%Y/%m/%d\',\n
                   dmy=\'%d/%m/%Y\',\n
                   mdy=\'%m/%d/%Y\').get(date_order, \'%Y/%m/%d\')\n
\n
category_list = []\n
if depth == 0:\n
  # This case show Seven days\n
  while current_date < bound_stop:\n
    # Create one Temp Object\n
    o = newTempBase(portal, id=\'week\', uid=\'new_%s\' % zfill(\'week\',4))\n
     # Setting Axis Dates start and stop\n
    o.setProperty(\'start\',current_date)\n
    o.setProperty(\'stop\', current_date+1)\n
    o.setProperty(\'relative_position\', int(current_date))\n
\n
    # Seting delimiter \n
    if current_date.day() == 1:\n
      o.setProperty(\'delimiter_type\', 2)\n
    elif current_date.day() == 15:\n
      o.setProperty(\'delimiter_type\', 1)\n
    else:\n
      o.setProperty(\'delimiter_type\', 0)\n
\n
    title = translateString(\'${day_name} ${date}\',\n
                            mapping=dict(day_name=translateString(current_date.Day()),\n
                                         date=current_date.strftime(date_format)))\n
    o.setProperty(\'title\', title)\n
\n
    # Defining ToolTip (Optional)\n
    tp = \'%s %s\' % (translateString(current_date.Day()), str(current_date))\n
    o.setProperty(\'tooltip\', tp)\n
\n
    # Defining Link (Optional)\n
    link = \'%s&bound_start=%s&lane_path=base_day_domain\' % ( default_link_url, url_quote(str(current_date)))\n
    o.setProperty(\'link\', link)\n
\n
    category_list.append(o)\n
    current_date = current_date + 1\n
    current_date =  DateTime(current_date.year() , current_date.month() , current_date.day())\n
else:\n
  return domain_list\n
\n
for category in category_list:\n
  domain = parent.generateTempDomain(id = \'sub\' + category.getProperty(\'id\'))\n
  domain.edit(title = category.getTitle(),\n
              membership_criterion_base_category = (\'parent\', ), \n
              membership_criterion_category = (category,),\n
              domain_generator_method_id = script.id,\n
              uid = category.getUid())\n
                \n
  domain_list.append(domain)\n
\n
return domain_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>depth, parent, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_generateWeekDomain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
