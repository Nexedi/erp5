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
            <value> <string>if scope_type==\'until_the_next_period\':\n
  return context.getNextPeriodicalDate(start_date)\n
elif scope_type==\'until_the_end_of_month\':\n
  def getNextMonth(year, month):\n
    """\n
    Returns year and month integer values of next month.\n
    """\n
    if month==12:\n
      return year+1, 1\n
    else:\n
      return year, month+1\n
\n
  def getLastDayOfMonth(year, month):\n
    """\n
    Returns last day of month.\n
    """\n
    next_month_year, next_month_month = getNextMonth(year, month)\n
    datetime = DateTime(next_month_year, next_month_month, 1)-1\n
    return datetime.day()\n
\n
  def getEndOfMonth(date):\n
    """\n
    Returns the end of month.\n
    """\n
    year = date.year()\n
    month = date.month()\n
    day = getLastDayOfMonth(year, month)\n
    return DateTime(year, month, day)\n
  return getEndOfMonth(start_date)\n
\n
raise ValueError, \'Unknown scope type: %s\' % scope_type\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>scope_type, start_date</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PeriodicityLine_calculateScopeTypeStopDate</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
