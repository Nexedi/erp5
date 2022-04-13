from Products.ERP5Type.Document import newTempBase
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.Utils import ensure_list
Base_translateString = context.Base_translateString

def getModifiedObjectList(context):
  result = context.preinstall(check_dependencies=check_dependencies)
  return result

def cacheIdGenerator(method_id, *args, **kw):
  context = args[0]
  return '%s%s%s' % (method_id,
                     context.getUid(),
                     context.getModificationDate().timeTime())

cache_id_generator = cacheIdGenerator

getModifiedObjectList = CachingMethod(getModifiedObjectList,
                              id='BusinessTemplate_getModifiedObjectList',
                              cache_factory='erp5_ui_medium',
                              cache_id_generator=cache_id_generator)

modified_object_list = getModifiedObjectList(context)
keys = ensure_list(modified_object_list.keys())
keys.sort()

no_backup_list = ['Action', 'SiteProperty', 'Module', 'Document',
                  'PropertySheet', 'Extension', 'Test', 'Product', 'Role',
                  'CatalogResultKey', 'CatalogRelatedKey',
                  'CatalogResultTable', 'MessageTranslation', 'LocalRoles',
                  'PortalTypeAllowedContentType',
                  'PortalTypeHiddenContentType', 'PortalTypePropertySheet',
                  'PortalTypeBaseCategory', 'Tool', ]
no_backup_dict = {}
for k in no_backup_list:
  no_backup_dict[k] = 1

install_title = Base_translateString('Install')
upgrade_title = Base_translateString('Upgrade')
backup_title = Base_translateString('Backup And Upgrade')
remove_title = Base_translateString('Remove')
save_and_remove_title = Base_translateString('Backup And Remove')

i = 0
object_list = []
for object_id in keys:
  object_state, object_class = modified_object_list[object_id]
  line = newTempBase(context, 'tmp_install_%s' %(str(i)))
  if object_state == 'New':
    choice_item_list=[[install_title, 'install']]
  elif object_state.startswith('Modified'):
    if object_class in no_backup_dict:
      choice_item_list=[[upgrade_title, 'install']]
    else:
      choice_item_list=[[backup_title, 'backup']]
  elif object_state.startswith('Removed'):
    if object_class in no_backup_dict:
      choice_item_list=[[remove_title, 'remove']]
    else:
      choice_item_list=[[save_and_remove_title, 'save_and_remove']]
  else:
    choice_item_list = [[install_title, 'install']]

  line.edit(object_id=object_id,
                object_state=object_state,
                object_class=object_class,
                choice_item_list=choice_item_list)
  line.setUid('new_%s' % str(object_id))
  object_list.append(line)
  i += 1                                  

object_list.sort(key=lambda x:(x.object_class, x.object_state))
return object_list
