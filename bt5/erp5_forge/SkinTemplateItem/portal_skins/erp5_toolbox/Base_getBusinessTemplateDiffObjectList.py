"""
Return a list of diff objects between two business templates.
The building state of the business templates should be "built".

Arguments:

- ``bt1``: The first business template object to compare
- ``bt2``: The second business template object to compare
"""
from builtins import str
from Products.ERP5Type.Document import newTempBase
from ZODB.POSException import ConflictError

template_tool = context.getPortalObject().portal_templates

assert bt1.getBuildingState() == "built"
assert bt2.getBuildingState() == "built"

modified_object_list = bt2.preinstall(check_dependencies=0, compare_to=bt1)
keys = list(modified_object_list.keys())
#keys.sort() # XXX don't care ?
bt1_id = bt1.getId()
bt2_id = bt2.getId()
i = 0
object_list = []
for object_id in keys:
  object_state, object_class = modified_object_list[object_id]
  line = newTempBase(template_tool, 'tmp_install_%s' % str(i)) # template_tool or context?
  line.edit(object_id=object_id, object_state=object_state, object_class=object_class, bt1=bt1_id, bt2=bt2_id)
  line.setUid('new_%s' % object_id)
  if detailed and object_state == "Modified":
    try:
      line.edit(data=bt2.diffObject(line, compare_with=bt1_id))
    except ConflictError:
      raise
    except Exception as e:
      if raise_on_diff_error:
        raise
      line.edit(error=repr(e))
  object_list.append(line)
  i += 1
return object_list
