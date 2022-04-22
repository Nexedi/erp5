from Products.ERP5Type.Document import newTempBase
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5.Document.BusinessTemplate import TemplateConditionError

# get selected business templates
p = context.getPortalObject()
portal_selections = p.portal_selections
selection_name = 'business_template_selection' # harcoded because we can also get delete_selection
uids = portal_selections.getSelectionCheckedUidsFor(selection_name)

if len(uids) > 2:
  raise TemplateConditionError('Too many Business Templates selected')

bt1 = context.portal_catalog.getObject(uids[0])
if bt1.getBuildingState() != 'built':
  raise TemplateConditionError('Business Template must be built to make diff')

# check if there is a second bt or if we compare to installed one
if len(uids) == 2:
  bt2 = context.portal_catalog.getObject(uids[1])
  if bt2.getBuildingState() != 'built':
    raise TemplateConditionError('Business Template must be built to make diff')
else:
  # compare to objects in ZODB
  bt2 = bt1

def getModifiedObjectList(bt1, bt2):
  return bt1.preinstall(compare_to=bt2)

getModifiedObjectList = CachingMethod(getModifiedObjectList, id='BusinessTemplate_getModifiedObjectList', \
                        cache_factory='erp5_ui_medium')

if p.portal_templates.compareVersions(bt1.getVersion(), bt2.getVersion()) < 0:
  modified_object_list = getModifiedObjectList(bt2, bt1)
else:
  modified_object_list = getModifiedObjectList(bt1, bt2)

keys = list(modified_object_list.keys())
keys.sort()

i = 0
object_list = []
for object_id in keys:    
  object_state, object_class = modified_object_list[object_id]
  line = newTempBase(context, 'tmp_install_%s' %(str(i)))
  line.edit(object_id=object_id, object_state=object_state, object_class=object_class, bt1=bt1.getId(), bt2=bt2.getId())
  line.setUid('new_%s' % object_id)
  object_list.append(line)
  i += 1                                  

return object_list
