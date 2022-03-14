from builtins import range
if REQUEST is not None:
  raise ValueError("This script cannot be called from the web")

import string
import random

installed_bt_for_diff = context.Base_createCloneDocument(clone=1, batch_mode=1)

random_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
installed_bt_for_diff.setId("installed_bt_for_diff_%s" % random_str)
installed_bt_for_diff.build()
diff_object_list = context.Base_getBusinessTemplateDiffObjectList(context, installed_bt_for_diff, detailed=detailed)
# XXX replace context.getPortalObject().portal_templates by something like context.getParentObject
context.getPortalObject().portal_templates.manage_delObjects(ids=[installed_bt_for_diff.getId()])
return diff_object_list
