REQUEST = container.REQUEST
Base_translateString = context.Base_translateString

bt_id_list = getattr(REQUEST, 'bt_list', ())
if len(bt_id_list) == 0:
  bt_id_list = kw.get('bt_list', ())

if 'MultiInstallationDialog' in getattr(REQUEST, 'current_form_id', ''):
  check_dependencies = 0
else:
  check_dependencies = 1

from Products.ERP5Type.Document import newTempBase
from Products.ERP5Type.Cache import CachingMethod

def getModifiedObjectList(bt):
  return bt.preinstall(check_dependencies = check_dependencies)

getModifiedObjectList = CachingMethod(getModifiedObjectList, 
                                      id='BusinessTemplate_getModifiedObjectList',
                                      cache_factory='erp5_ui_medium')

bt_object_dict = {}

for bt_id in bt_id_list:
  bt = context.portal_templates[bt_id]
  bt_object_dict[bt.getId()] = [bt.getTitle(), getModifiedObjectList(bt)]

object_list = []
no_backup_list = ['Action', 'SiteProperty', 'Module', 'Document', 
                 'PropertySheet', 'Extension', 'Test', 'Product', 
                 'Role', 'CatalogResultKey', 'CatalogRelatedKey', 
                 'CatalogResultTable', 'MessageTranslation', 'LocalRoles', 
                 'PortalTypeAllowedContentType', 'PortalTypeHiddenContentType', 
                 'PortalTypePropertySheet', 'PortalTypeBaseCategory']
no_backup_dict = {}
for i in no_backup_list:
  no_backup_dict[i] = True

install_title = Base_translateString('Install')
upgrade_title = Base_translateString('Upgrade')
backup_title = Base_translateString('Backup And Upgrade')
remove_title = Base_translateString('Remove')
save_and_remove_title = Base_translateString('Backup And Remove')

for bt in bt_id_list:
  bt_title, modified_object_list = bt_object_dict[bt]
  keys = list(modified_object_list.keys())
  keys.sort()
  for i, object_id in enumerate(keys):    
    object_state, object_class = modified_object_list[object_id]
    object_id = bt+'|'+object_id
    line = newTempBase(context, 'tmp_install_%s' % i)

    if object_state.startswith('Modified'):
      if object_class in no_backup_dict:
        choice_item_list = [[upgrade_title, 'install']]
      else:
        choice_item_list = [[backup_title, 'backup']]
    elif object_state.startswith('Removed'):
      if object_class in no_backup_dict:
        choice_item_list = [[remove_title, 'remove']]
      else:
        choice_item_list = [[save_and_remove_title, 'save_and_remove']]
    else:
      choice_item_list = [[install_title, 'install']]

    line.edit(object_id=object_id,
              bt_title = bt_title, 
              object_state=object_state, 
              object_class=object_class, 
              choice_item_list=choice_item_list)
    line.setUid('new_%s' % object_id)
    object_list.append(line)

object_list.sort(key=lambda x:(x.bt_title, x.object_class, x.object_state))
return object_list
