from Products.ERP5Type import WITH_LEGACY_WORKFLOW
assert WITH_LEGACY_WORKFLOW

from Products.DCWorkflow.Worklists import Worklists
from Products.DCWorkflow.Worklists import WorklistDefinition
from Products.ERP5Type.Permissions import ManagePortal

# Allow manager to rename worklists
for meta_type in Worklists.all_meta_types:
  if meta_type['name'] == WorklistDefinition.meta_type:
    meta_type.setdefault('permission', ManagePortal)
