## Script (Python) "PaySheetTransaction_getFormattedLines_OLD"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# Example code:

pay_sheet_lines=tuple()
object_list = []
for object in context.objectValues():
  object_list += [object]
# Sort the list by id since lines are already ordered by id.
object_list.sort(lambda x, y: cmp(int(x.getId()), int(y.getId())))
for pay_sheet_line in object_list:
  variation_list =  pay_sheet_line.getVariationCategoryList()
  range_variation = []
  for variation in variation_list:
    if variation.find('salary_range')==0:
      if not variation in range_variation: # Extra checking because
                                           # get VariationCategoryList returns
                                           # the same 1 items 2 times
        range_variation += [variation]
  for range in range_variation:
    pay_sheet_dict = {}
    #pay_sheet_dict['range']=range[range.rfind('/')+1:]
    pay_sheet_dict['id'] = pay_sheet_line.getId()
    pay_sheet_dict['title'] = pay_sheet_line.getResourceTitle()
    for cell in pay_sheet_line.objectValues():
      predicate_list = cell.getPredicateValueList()
      if range in predicate_list:
        for predicate in predicate_list:
          if cell.getTotalPrice() != 0:
            if predicate.find('salary_share')>=0:
              pay_sheet_dict['range']= - cell.getQuantity()
              pay_sheet_dict['salary_share']='%.2f' % cell.getTotalPrice()
              pay_sheet_dict['salary_share_rate']='%.3f %%' % (cell.getPrice()*100)
              if str(pay_sheet_line.getResource())[-14:] == 'non_deductible' or str(pay_sheet_line.getResource())[-4:] == 'crds' or str(pay_sheet_line.getResource())[-7:] == 'taxable':
                pay_sheet_dict['taxable']='yes'
              elif str(pay_sheet_line.getResource())[-10:] == 'deductible':
                pay_sheet_dict['taxable']='no'
              else:
                pay_sheet_dict['taxable']='no'
            elif predicate.find('employer_share')>=0:
              pay_sheet_dict['range']= - cell.getQuantity()
              pay_sheet_dict['employer_share']='%.2f' % cell.getTotalPrice()
              pay_sheet_dict['employer_share_rate']='%.3f %%' % (cell.getPrice()*100)
    for key in ('salary_share','salary_share_rate','employer_share','employer_share_rate'):
      if not (pay_sheet_dict.has_key(key)):
        pay_sheet_dict[key]='' # so that we can display nothing
    pay_sheet_lines += (pay_sheet_dict,)


return pay_sheet_lines
