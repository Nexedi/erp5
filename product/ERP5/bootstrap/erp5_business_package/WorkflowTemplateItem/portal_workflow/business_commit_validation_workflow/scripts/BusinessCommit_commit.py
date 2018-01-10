"""
Validate Business Commit and checks if it has atleast one item
"""

from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import translateString

business_commit = state_change['object']
listbox = state_change.kwargs.get('listbox')

business_commit.Base_checkConsistency()

business_item_list = business_commit.objectValues()

# Raise error in case there is no Business Item or Business Property Item added
# in the Business Commit
if not business_item_list:
  raise ValidationFailed(translateString('Please add item in commit before committing'))
