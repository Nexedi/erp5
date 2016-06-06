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

#TODO : USE CACHE\n
# The goal of this script is to get all the products from all the visible Web Sections\n
# and it must select randomly which product must be displayed for a given context.\n
from random import choice\n
\n
web_site = context.getWebSiteValue() or context.REQUEST.get(\'current_web_site\')\n
\n
if not kw.has_key(\'portal_type\'):\t \t \n
  kw[\'portal_type\'] = \'Product\'\n
\n
# Getting all the products from all the visible Web Section.\n
product_dict = {}\n
for web_section in web_site.WebSite_getMainSectionList():\n
  for product in web_section.getDocumentValueList(all_versions=1, all_languages=1, **kw):\n
    product_dict[product.uid] = product\n
\n
if len(product_dict) > limit:\n
  random_uid_list = []\n
  key_list = product_dict.keys()\n
  while len(random_uid_list) < limit:\n
    random_uid = choice(key_list)\n
    key_list.remove(random_uid)\n
    random_uid_list.append(random_uid)\n
  product_list = [product_dict.get(uid) for uid in random_uid_list]\n
else:\n
  product_list = product_dict.values()\n
\n
return product_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>limit=5, **kw</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Assignee</string>
                <string>Assignor</string>
                <string>Associate</string>
                <string>Auditor</string>
                <string>Authenticated</string>
                <string>Author</string>
                <string>Manager</string>
                <string>Member</string>
                <string>Owner</string>
                <string>Reviewer</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSite_getProductList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
