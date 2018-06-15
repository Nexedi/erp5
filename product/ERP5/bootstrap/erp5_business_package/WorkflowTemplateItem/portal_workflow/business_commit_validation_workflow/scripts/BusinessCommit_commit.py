context.BusinessCommit_validateItemsOnCommitCommit(state_change)
context.BusinessCommit_updateUuidOnCommitCommit(state_change)

#"""
#Validate Business Commit and checks if it has atleast one item
#"""
#
#from Products.DCWorkflow.DCWorkflow import ValidationFailed
#from Products.ERP5Type.Message import translateString
#
#business_commit = state_change['object']
#
#business_commit.Base_checkConsistency()
#business_item_list = business_commit.objectValues()
#
#commit_path_list = business_commit.getItemPathList()
## Raise error in case the commit have 2 items which has same path
#if len(commit_path_list) != len(set(commit_path_list)):
#  raise ValidationFailed(translateString('Multiple items have same path !'))
#
## Raise error in case there is no Business Item or Business Property Item added
## in the Business Commit
#if not business_item_list:
#  raise ValidationFailed(translateString('Please add item(s) in commit before committing'))
