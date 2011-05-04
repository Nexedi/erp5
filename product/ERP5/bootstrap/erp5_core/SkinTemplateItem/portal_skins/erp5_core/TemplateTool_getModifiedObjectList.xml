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
            <value> <string>REQUEST = container.REQUEST\n
Base_translateString = context.Base_translateString\n
\n
bt_id_list = getattr(REQUEST, \'bt_list\', ())\n
if len(bt_id_list) == 0:\n
  bt_id_list = kw.get(\'bt_list\', ())\n
\n
if \'MultiInstallationDialog\' in getattr(REQUEST, \'current_form_id\', \'\'):\n
  check_dependencies = 0\n
else:\n
  check_dependencies = 1\n
\n
from Products.ERP5Type.Document import newTempBase\n
from Products.ERP5Type.Cache import CachingMethod\n
\n
def getModifiedObjectList(bt):\n
  return bt.preinstall(check_dependencies = check_dependencies)\n
\n
getModifiedObjectList = CachingMethod(getModifiedObjectList, \n
                                      id=\'BusinessTemplate_getModifiedObjectList\',\n
                                      cache_factory=\'erp5_ui_medium\')\n
\n
bt_object_dict = {}\n
\n
for bt_id in bt_id_list:\n
  bt = context.portal_templates[bt_id]\n
  bt_object_dict[bt.getId()] = [bt.getTitle(), getModifiedObjectList(bt)]\n
\n
object_list = []\n
no_backup_list = [\'Action\', \'SiteProperty\', \'Module\', \'Document\', \n
                 \'PropertySheet\', \'Extension\', \'Test\', \'Product\', \n
                 \'Role\', \'CatalogResultKey\', \'CatalogRelatedKey\', \n
                 \'CatalogResultTable\', \'MessageTranslation\', \'LocalRoles\', \n
                 \'PortalTypeAllowedContentType\', \'PortalTypeHiddenContentType\', \n
                 \'PortalTypePropertySheet\', \'PortalTypeBaseCategory\']\n
no_backup_dict = {}\n
for i in no_backup_list:\n
  no_backup_dict[i] = True\n
\n
install_title = Base_translateString(\'Install\')\n
upgrade_title = Base_translateString(\'Upgrade\')\n
backup_title = Base_translateString(\'Backup And Upgrade\')\n
remove_title = Base_translateString(\'Remove\')\n
save_and_remove_title = Base_translateString(\'Backup And Remove\')\n
\n
for bt in bt_id_list:\n
  bt_title, modified_object_list = bt_object_dict[bt]\n
  keys = modified_object_list.keys()\n
  keys.sort()\n
  for i, object_id in enumerate(keys):    \n
    object_state, object_class = modified_object_list[object_id]\n
    object_id = bt+\'|\'+object_id\n
    line = newTempBase(context, \'tmp_install_%s\' % i)\n
\n
    if object_state.startswith(\'Modified\'):\n
      if object_class in no_backup_dict:\n
        choice_item_list = [[upgrade_title, \'install\']]\n
      else:\n
        choice_item_list = [[backup_title, \'backup\']]\n
    elif object_state.startswith(\'Removed\'):\n
      if object_class in no_backup_dict:\n
        choice_item_list = [[remove_title, \'remove\']]\n
      else:\n
        choice_item_list = [[save_and_remove_title, \'save_and_remove\']]\n
    else:\n
      choice_item_list = [[install_title, \'install\']]\n
\n
    line.edit(object_id=object_id,\n
              bt_title = bt_title, \n
              object_state=object_state, \n
              object_class=object_class, \n
              choice_item_list=choice_item_list)\n
    line.setUid(\'new_%s\' % object_id)\n
    object_list.append(line)\n
\n
object_list.sort(key=lambda x:(x.bt_title, x.object_class, x.object_state))\n
return object_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TemplateTool_getModifiedObjectList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
