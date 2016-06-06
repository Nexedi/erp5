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

preferences = box.KnowledgeBox_getDefaultPreferencesDict()\n
h = str(preferences.get(\'preferred_height\'))\n
w = str(preferences.get(\'preferred_width\'))\n
t = str(preferences.get(\'preferred_title\'))\n
location = str(preferences.get(\'preferred_location\'))\n
language = str(preferences.get(\'preferred_language\'))\n
large_map = \'1\'\n
kml = \'0\'\n
\n
\n
s = """<script type="text/javascript" src="http://gmodules.com/ig/ifr?url=http://www.google.com/ig/modules/mapsearch.xml&amp;up_location=""" + location + """&amp;up_largeMapMode=""" + large_map + """&amp;up_kml=""" + kml + """&amp;up_traffic=&amp;up_locationCacheString=&amp;up_locationCacheLat=&amp;up_locationCacheLng=&amp;up_mapType=m&amp;up_idleZoom=11&amp;up_transitionQuery=&amp;up_rawquery=&amp;up_selectedtext=&amp;synd=open&amp;w=""" + w + """&amp;h=""" + h + """&amp;title=""" + t + """&amp;lang=""" + language +"""&amp;country=ALL&amp;border=%23ffffff%7C3px%2C1px+solid+%23999999&amp;output=js"></script>"""\n
\n
return s\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>box</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_viewGoogleMapsGadget</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
