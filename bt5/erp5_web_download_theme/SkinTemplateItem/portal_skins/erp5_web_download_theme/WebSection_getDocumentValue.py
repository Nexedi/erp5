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
            <value> <string>if portal is None: portal = context.getPortalObject()\n
portal_catalog = portal.portal_catalog\n
\n
# Find the applicable portal type\n
valid_portal_type_list = portal.getPortalDocumentTypeList()\n
\n
# Find the applicable state\n
if validation_state is None:\n
  validation_state = (\'released\', \'released_alive\', \'published\', \'published_alive\',\n
                      \'shared\', \'shared_alive\', \'public\', \'validated\')\n
\n
#set kw dict for all search\n
kw[\'portal_type\'] = valid_portal_type_list\n
kw[\'validation_state\'] = validation_state\n
\n
# packages are without language, and can look like:\n
#   package.name.with._dots.and.underscore-0.1.0dev-r1980.tar.gz\n
# where:\n
#  package.name.with._dots.and.underscore -- name\n
#  0.1.0dev-r1980 -- version\n
#  tar.gz -- extension\n
# or like:\n
#   package-name-with-dots-and-minus-some-version.extension.uuk\n
# or even:\n
#   package_name-with-minus-version-with_minus.extension.ops\n
# or even:\n
#   package_like-this.and-version_like-this.extension.ex2\n
# or even:\n
#   package-like_och-version.1.2-dev3_Q.ext.ext\n
# some repositories (like pypi) are assuming case insensitive packages\n
# other (tarballs) are case sensitive\n
reference, extension_part = name.split(\'-\', 1)\n
#Remove extension from last part only\n
if \'.tar.\' in extension_part:\n
  name_list = extension_part.rsplit(\'.\', 2)\n
  version = name_list[0]\n
  extension = \'.\'.join(name_list[1:])\n
else:\n
  version, extension = extension_part.rsplit(\'.\', 1)\n
\n
kw.update(\n
  reference=reference,\n
  version=version\n
)\n
document_list = portal_catalog(limit=1, **kw)\n
if len(document_list) == 1:\n
  return document_list[0].getObject()\n
return None\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>name, portal=None, language=None, validation_state=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSection_getDocumentValue</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
