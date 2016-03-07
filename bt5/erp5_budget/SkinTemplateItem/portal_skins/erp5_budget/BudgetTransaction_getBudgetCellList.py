from Products.CMFCore.utils import getToolByName
domain_tool = getToolByName(context, 'portal_domains')
budget_cell_list = [x.getObject() for x in \
                    domain_tool.searchPredicateList(
                      context, portal_type=['Budget Cell'],
                      tested_base_category_list=['resource'])]
return [('','')]+[(x.getTitle(), x.getRelativeUrl()) for x in budget_cell_list]
