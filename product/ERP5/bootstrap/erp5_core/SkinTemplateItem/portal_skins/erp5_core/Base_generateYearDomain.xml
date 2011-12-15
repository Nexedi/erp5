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

#  - Years always starts at 0h of the current year\'s first day  and \n
#    finish 0h of the next year\'s first day.\n
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
params = portal.portal_selections.getSelectionParamsFor(selection_name, request)\n
\n
zoom_begin = DateTime(params.get(\'bound_start\', DateTime()))\n
year = zoom_begin.year() + params.get(\'bound_variation\', 0)\n
current_date = DateTime(year, 1, 1)\n
\n
default_link_url =\'setLanePath?form_id=%s&list_selection_name=%s\' %(\n
                                 form_id, selection_name)\n
\n
# Define date format using user Preferences\n
date_order = portal.portal_preferences.getPreferredDateOrder()\n
date_format = dict(ymd=\'%m/%d\',\n
                   dmy=\'%d/%m\',\n
                   mdy=\'%m/%d\').get(date_order, \'%m/%d\')\n
\n
category_list = []\n
if depth == 0:\n
  # getting list of months\n
  count = 0\n
  while   count < 12:\n
    # Create one Temp Object\n
    o = newTempBase(portal, id=\'year\' ,uid=\'new_%s\' % zfill(\'year\',4))\n
    # Seting delimiter \n
    if current_date.month() in [1, 7]:\n
      o.setProperty(\'delimiter_type\', 1)\n
    else:\n
      o.setProperty(\'delimiter_type\', 0)\n
    \n
     # Setting Axis Dates start and stop\n
    o.setProperty(\'start\',current_date)\n
    if current_date.month() != 12:\n
      stop_date = DateTime(current_date.year(),current_date.month() +1,1)\n
    else:\n
       stop_date = DateTime(year+1, 1, 1)\n
    o.setProperty(\'stop\', stop_date)\n
    \n
    o.setProperty(\'relative_position\', int(current_date))\n
\n
    title = translateString(\'${month_name} ${year}\',\n
                            mapping=dict(month_name=translateString(current_date.Month()),\n
                                         year=str(current_date.year())))\n
    o.setProperty(\'title\', title)\n
\n
    # Defining Link\n
    link = \'%s&bound_start=%s&lane_path=base_month_domain\' % ( default_link_url, url_quote(str(current_date)))\n
    o.setProperty(\'link\', link)\n
    \n
    category_list.append(o)\n
    current_date = DateTime(str(current_date.year()) + \'/\' + str((current_date.month() +1)) + \'/1\')\n
    count += 1\n
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
            <value> <string>Base_generateYearDomain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
