# Example code:

global object_list
object_list = []
portal = context.getPortalObject()

def failIfDifferent(id, a,b):
  if a != b:
    return "Error on %s: %s != %s" % (id, a, b)
  return None

def failIfDifferentSet(id, a,b):
  for i in a:
    if i not in b:
      return "Error on %s: %s != %s" % (id, a, b)
  for i in b:
    if i not in a:
      return "Error on %s: %s != %s" % (id, a, b)
  return None

def cleanUp(result):
  global object_list
  for o in object_list:
    o.aq_parent.manage_delObjects(ids=[o.getId()])
  return result

# Test single category on person
p = portal.person.newContent()
object_list.append(p)
base_category = 'region'
region = 'europe/west/france'
region_value = portal.portal_categories.resolveCategory('europe/west/france')
p.setRegion(region)
result = failIfDifferent('getRegion 1', p.getRegion(), region)
if result is not None: return cleanUp(result)
result = failIfDifferent('getDefaultRegion 1', p.getDefaultRegion(), region)
if result is not None: return cleanUp(result)
result = failIfDifferent('getRegionList 1', p.getRegionList(), [region])
if result is not None: return cleanUp(result)

# Test multiple category on person
region_list = ['europe/west/france', 'europe/west/germany']
region_value_list = [portal.portal_categories.resolveCategory('europe/west/france'),
                     portal.portal_categories.resolveCategory('europe/west/germany')]
p.setRegion(region_list)
result = failIfDifferent('getRegion 2', p.getRegion(), region)
if result is not None: return cleanUp(result)
result = failIfDifferent('getDefaultRegion 2', p.getDefaultRegion(), region)
if result is not None: return cleanUp(result)
result = failIfDifferent('getRegionList 2', p.getRegionList(), region_list)
if result is not None: return cleanUp(result)

# Test category values
result = failIfDifferent('getRegion 3', p.getRegionValue(), region_value)
if result is not None: return cleanUp(result)

# Test None and ''
p.setRegion(None)
result = failIfDifferent('getRegion 4', p.getRegion(), None)
if result is not None: return cleanUp(result)
p.setRegion('')
result = failIfDifferent('getRegion 5', p.getRegion(), None)
if result is not None: return cleanUp(result)

# Test category acquisition for single value
## XXX TODO: make sure acquisition is updated in Coramy
o = portal.organisation.newContent()
object_list.append(o)
o.setRegion(region)
p.setSubordinationValue(o)
result = failIfDifferent('getRegion 6', p.getRegion(), region)
if result is not None: return cleanUp(result)
result = failIfDifferent('getDefaultRegion 6', p.getDefaultRegion(), region)
if result is not None: return cleanUp(result)
result = failIfDifferent('getRegionList 6', p.getRegionList(), [region])
if result is not None: return cleanUp(result)

# Test category acquisition for list value
o.setRegion(region_list)
result = failIfDifferent('getRegion 7', p.getRegion(), region)
if result is not None: return cleanUp(result)
result = failIfDifferent('getDefaultRegion 7', p.getDefaultRegion(), region)
if result is not None: return cleanUp(result)
result = failIfDifferent('getRegionList 7', p.getRegionList(), region_list)
if result is not None: return cleanUp(result)

# Test Value
result = failIfDifferent('getSubordinationValue 1', p.getSubordinationValue(), o)
if result is not None: return cleanUp(result)
result = failIfDifferent('getDefaultSubordinationValue 1', p.getSubordinationValue(), o)
if result is not None: return cleanUp(result)
result = failIfDifferent('getSubordinationValueList 1', p.getSubordinationValueList(), [o])
if result is not None: return cleanUp(result)

# Test Multiple Value
o2 = portal.organisation.newContent()
object_list.append(o2)
subordination_value_list = [o, o2]
p.setSubordinationValueList(subordination_value_list)
result = failIfDifferent('getSubordinationValue 2', p.getSubordinationValue(), o)
if result is not None: return cleanUp(result)
result = failIfDifferent('getDefaultSubordinationValue 2', p.getSubordinationValue(), o)
if result is not None: return cleanUp(result)
result = failIfDifferent('getSubordinationValueList 2', p.getSubordinationValueList(), subordination_value_list)
if result is not None: return cleanUp(result)

# Test getCategoryParentUidList (ERP5)
portal.portal_categories.manage_addProduct['ERP5'].addBaseCategory('basecat')
basecat = portal.portal_categories.basecat
object_list.append(basecat)
portal.portal_categories.basecat.manage_addProduct['ERP5'].addCategory('cat1')
cat1 = portal.portal_categories.basecat.cat1
portal.portal_categories.basecat.cat1.manage_addProduct['ERP5'].addCategory('cat2')
cat2 = portal.portal_categories.basecat.cat1.cat2
parent_uid_list = [(cat2.getUid(), basecat.getUid(), 1),
                   (cat1.getUid(), basecat.getUid(), 0),
                   (basecat.getUid(), basecat.getUid(), 0)]
result = failIfDifferentSet('getCategoryParentUidList',
             cat2.getCategoryParentUidList(relative_url = cat2.getRelativeUrl()), parent_uid_list)
if result is not None: return cleanUp(result)

# Test getRelatedValueList (ERP5)
p.immediateReindexObject() # Make sure well indexed
p2 = o.getSubordinationRelatedValue()
result = failIfDifferent('getSubordinationRelatedValue', p2, p)
if result is not None: return cleanUp(result)

# Cleanup
cleanUp(None)