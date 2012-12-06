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
            <value> <string>for rule in sorted(context.getPortalObject().portal_rules.contentValues(),\n
                  key=lambda x:x.getTitle()):\n
  if rule.getValidationState() != \'validated\':\n
    continue\n
  print rule.getId()\n
  print "  Title: %s" % (rule.getTitle())\n
  print "  Trade Phases: %r" % (rule.getTradePhaseList())\n
  print "  Test Method Id: %s" % (rule.getTestMethodId())\n
  print "  Membership Criteria: %r" % (rule.getMembershipCriterionBaseCategoryList())\n
  print "  Membership Criterion Category: %r" % (rule.getMembershipCriterionCategoryList())\n
  print\n
\n
  for tester in sorted(rule.contentValues(), key=lambda x:x.getTitle()):\n
    print rule.getId()\n
    print " ", "\\n  ".join([x for x in (\n
      "Id: %s" % tester.getId(),\n
      "Title: %s" % tester.getTitle(),\n
      "Type: %s" % tester.getPortalType(),\n
      "Updating: %s" % tester.isUpdatingProvider(),\n
      "Divergence: %s" % tester.isDivergenceProvider(),\n
      "Matching: %s" % tester.isMatchingProvider(),\n
\n
      "Test Method Id: %s" % tester.getTestMethodId(),\n
      "Membership Criteria: %r" %\n
        (tester.getMembershipCriterionBaseCategoryList()),\n
      "Membership Criterion Category: %r" %\n
        (tester.getMembershipCriterionCategoryList()),\n
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
            <value> <string>ERP5Site_dumpRuleTesterList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
