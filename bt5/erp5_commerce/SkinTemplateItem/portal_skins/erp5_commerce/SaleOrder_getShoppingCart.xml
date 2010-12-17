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
            <value> <string>""" \n
  Add resource to current (or to be created shopping cart). \n
"""\n
from DateTime import DateTime\n
\n
request = context.REQUEST\n
expire_timeout_days = 90\n
session_id = request.get(\'session_id\', None)\n
portal_sessions = context.portal_sessions\n
\n
if session_id is None:\n
  ## first call so generate session_id and send back via cookie\n
  now = DateTime()\n
  session_id = context.Base_generateSessionID(max_long=20)\n
  request.RESPONSE.setCookie(\'session_id\', session_id, expires=(now +expire_timeout_days).fCommon(), path=\'/\')\n
\n
if action==\'reset\':\n
  ## reset cart \n
  portal_sessions.manage_delObjects(session_id)\n
else:\n
  ## take shopping cart for this customer\n
  shopping_cart_id = \'shopping_cart\'\n
  session = portal_sessions[session_id]\n
  if not shopping_cart_id in session.keys():\n
    from Products.ERP5Type.Document import newTempOrder\n
    web_site = context.getWebSiteValue()\n
    shopping_cart = newTempOrder(portal_sessions, shopping_cart_id)\n
    shopping_cart.setPriceCurrency(web_site.WebSite_getShoppingCartDefaultCurrency().getRelativeUrl())\n
    session[shopping_cart_id] = shopping_cart\n
\n
  ## return just a part of session for shopping cart\n
  shopping_cart = session[shopping_cart_id]\n
  return shopping_cart\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>action=\'\', new_shopping_cart=None</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SaleOrder_getShoppingCart</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Get shopping cart for customer</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
