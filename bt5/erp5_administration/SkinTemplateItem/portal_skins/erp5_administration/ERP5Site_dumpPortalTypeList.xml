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
            <value> <string>for ti in sorted(context.getPortalObject().portal_types.contentValues(), key=lambda x:x.getId()):\n
  print ti.getId()\n
  print " ", "\\n  ".join([x for x in (\n
    "Short Title: %s" % ti.getShortTitle(),\n
    "Class: %s" % ti.getTypeClass(),\n
    "Init Script: %s" % ti.getTypeInitScriptId(),\n
    "Add Permission: %s" % ti.getTypeAddPermission(),\n
    "Acquire Local Roles: %s" % ti.getTypeAcquireLocalRole(),\n
    "Property Sheets: %r" % sorted(ti.getTypePropertySheetList()),\n
    "Base Categories: %r" % sorted(ti.getTypeBaseCategoryList()),\n
    "Allowed Content Types: %r" % sorted(ti.getTypeAllowedContentTypeList()),\n
    "Hidden Content Types: %r" % sorted(ti.getTypeHiddenContentTypeList()),\n
    "Searchable Property: %r" % sorted(ti.getSearchableTextPropertyIdList()),\n
    "Searchable Method: %r" % sorted(ti.getSearchableTextMethodIdList()),\n
    )])\n
  print\n
\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_dumpPortalTypeList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
