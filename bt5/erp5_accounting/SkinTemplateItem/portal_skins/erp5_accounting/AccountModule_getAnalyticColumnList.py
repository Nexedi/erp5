"""Returns the list of columns to use in accounting reports (GL, account statement, journal)
"""
from Products.ZSQLCatalog.SQLCatalog import BaseQuery
portal = context.getPortalObject()
request = portal.REQUEST

# cache the title in the request, it will be used by Movement_getProjectTitle
# and Movement_getFunctionTitle scripts
request.other['Movement_getProjectTitle.project_title_dict'
    ] = project_title_dict = {}
request.other['Movement_getFunctionTitle.function_title_dict'
    ] = function_title_dict = {}
request.other['Movement_getFundingTitle.funding_title_dict'
    ] = funding_title_dict = {}

analytic_column_list = ()
funding_item_list = context.AccountingTransactionLine_getFundingItemList()
if funding_item_list:
  analytic_column_list += (('funding', context.AccountingTransactionLine_getFundingBaseCategoryTitle()),)
for v, k in funding_item_list:
  if k:
    if k == 'None' or isinstance(k, BaseQuery):
      funding_title_dict[None] = ''
    else:
      funding_title_dict[portal.portal_categories.restrictedTraverse(k).getUid()] = v

function_item_list = context.AccountingTransactionLine_getFunctionItemList()
if function_item_list:
  analytic_column_list += (('function', context.AccountingTransactionLine_getFunctionBaseCategoryTitle()),)
for v, k in function_item_list:
  if k:
    if k == 'None' or isinstance(k, BaseQuery):
      function_title_dict[None] = ''
    else:
      function_title_dict[portal.portal_categories.restrictedTraverse(k).getUid()] = v

project_item_list = context.AccountingTransactionLine_getProjectItemList()
if project_item_list:
  analytic_column_list += (('project', 'Project'),)
for v, k in project_item_list:
  if k:
    if k == 'None' or isinstance(k, BaseQuery):
      project_title_dict[None] = ''
    else:
      project_title_dict[portal.portal_categories.restrictedTraverse(k).getUid()] = v

for base_category in \
    portal.portal_preferences.getPreferredAccountingTransactionLineAnalyticBaseCategoryList() or []:
  title = portal.portal_categories.restrictedTraverse(base_category).getTitle()
  analytic_column_list += (('%s_translated_title' % base_category, title),)

return analytic_column_list
