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
            <value> <string>request = container.REQUEST\n
RESPONSE =  request.RESPONSE\n
\n
stat_line = request.get(\'stat_line\', None)\n
\n
return stat_line\n
\n
\n
# XXX example of another way to get the stat line but this is slower\n
from Products.ERP5Type.Log import log\n
from Products.PythonScripts.standard import Object\n
from Products.ZSQLCatalog.SQLCatalog import Query\n
request = container.REQUEST\n
from_date = request.get(\'from_date\', None)\n
to_date = request.get(\'at_date\', None)\n
aggregation_level = request.get(\'aggregation_level\', None)\n
log("in stat method", "")\n
# build document portal type list\n
portal_type_list = []\n
extend = portal_type_list.extend\n
for title, path in context.ERP5Site_getModuleItemList():\n
  document_type_list = context.restrictedTraverse(path).allowedContentTypes()\n
  extend([x.id for x in document_type_list])\n
\n
# compute sql params, we group and order by date and portal type\n
if aggregation_level == "year":\n
  sql_format = "%Y"\n
elif aggregation_level == "month":\n
  sql_format = "%Y-%m"\n
elif aggregation_level == "week":\n
  sql_format = "%Y-%u"\n
elif aggregation_level == "day":\n
  sql_format = "%Y-%m-%d"\n
params = {"creation_date":(from_date, to_date)}\n
query=None\n
if from_date is not None and to_date is not None:  \n
  params = {"creation_date":(from_date, to_date)}\n
  query = Query(range="minngt", **params)\n
elif from_date is not None:\n
  params = {"creation_date":from_date}\n
  query = Query(range="min", **params)\n
elif to_date is not None:\n
  params = {"creation_date":to_date}\n
  query = Query(range="ngt", **params)\n
select_expression = {\'date\' : \'DATE_FORMAT(creation_date, "%s")\'%sql_format}\n
group_by = [\'DATE_FORMAT(creation_date, "%s")\' % sql_format,]\n
\n
# count number of object created by the user for each type of document\n
result_list = context.portal_catalog.countResults(select_expression=select_expression,\n
                                                  portal_type=portal_type_list,limit=None,\n
                                                  owner=context.getReference(),query=query,\n
                                                  group_by_expression=group_by)\n
\n
# build result dict per portal_type then period\n
period_count_dict = {}\n
for result in result_list:\n
  period_count_dict[result[1]] = result[0]\n
\n
# build line\n
obj = Object(uid="new_")\n
obj["document_type"] = \'Total\'\n
line_counter = 0\n
for period in period_list:\n
  if period_count_dict.has_key(period):\n
    obj[period] = period_count_dict[period]\n
    line_counter += period_count_dict[period]\n
  else:\n
    obj[period] = 0\n
obj[\'total\'] = line_counter\n
\n
return [obj,]\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>period_list, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Person_statPersonDetailedContributionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
