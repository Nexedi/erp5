## Script (Python) "PaySheetTransaction_getDetails_BACKUP"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# this dict contain all paysheet details
paysheet_details = {}

# initialize the salary and employer share total
total_salary_share          = 0.0
total_employer_share        = 0.0
total_taxable_salary_share  = 0.0

# get the gross salary
gross_salary = context.getGrossSalary()

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
              pay_sheet_dict['base']= - cell.getQuantity()
              pay_sheet_dict['salary_share'] = cell.getTotalPrice()
              pay_sheet_dict['salary_share_rate'] = cell.getPrice() * 100
              total_salary_share += float(-pay_sheet_dict['salary_share'])
              # here we decide if a resource is taxable or not
              if str(pay_sheet_line.getResource())[-14:] == 'non_deductible' or str(pay_sheet_line.getResource())[-4:] == 'crds' or str(pay_sheet_line.getResource())[-7:] == 'taxable':
                pay_sheet_dict['taxable']='yes'
              elif str(pay_sheet_line.getResource())[-10:] == 'deductible':
                pay_sheet_dict['taxable']='no'
              else:
                pay_sheet_dict['taxable']='no'
              if pay_sheet_dict['taxable'] == 'yes':
                total_taxable_salary_share += float(-pay_sheet_dict['salary_share'])
            elif predicate.find('employer_share')>=0:
              pay_sheet_dict['base'] = - cell.getQuantity()
              pay_sheet_dict['employer_share'] = cell.getTotalPrice()
              pay_sheet_dict['employer_share_rate'] = cell.getPrice() * 100
              total_employer_share += float(-pay_sheet_dict['employer_share'])
    for key in ('salary_share','salary_share_rate','employer_share','employer_share_rate'):
      if not (pay_sheet_dict.has_key(key)):
        pay_sheet_dict[key]='' # so that we can display nothing
    pay_sheet_lines += (pay_sheet_dict,)

# get all paysheet transaction to calculate the sum of different value in a year
accounting_folder = context.aq_parent
paysheet_transactions = accounting_folder.contentValues(filter={'portal_type':'Pay Sheet Transaction'})

# initialize every yearly variable
yearly_net_salary           = 0.0
yearly_gross_salary         = 0.0
yearly_salary_share         = 0.0
yearly_employer_share       = 0.0
yearly_taxable_net_salary   = 0.0

# get the current paysheet start date and employee
start_date  = context.getStartDate()
employee    = context.restrictedTraverse(context.getDestinationSectionRelativeUrl())

# browse through paysheet transaction
for paysheet_obj in paysheet_transactions:
  # ignore the current paysheet
  if paysheet_obj.getId() != context.getId():
    # the paysheet must have the same employee
    if (employee==None) or (employee!=None and context.restrictedTraverse(paysheet_obj.getDestinationSectionRelativeUrl())==employee):
      # check the date
      if (start_date==None) or (start_date!=None and paysheet_obj.getStartDate()!=None and start_date.year()==paysheet_obj.getStartDate().year() and paysheet_obj.getStartDate()<= start_date):
        # get all detailed values of the paysheet
        ps_details = paysheet_obj.PaySheetTransaction_getDetails()
        # sum of yearly values
        yearly_net_salary           += float(ps_details['net_salary'])
        yearly_gross_salary         += float(ps_details['gross_salary'])
        yearly_salary_share         += float(ps_details['total_salary_share'])
        yearly_employer_share       += float(ps_details['total_employer_share'])
        yearly_taxable_net_salary   += float(ps_details['taxable_net_salary'])

# save the total share values in the exported dict
paysheet_details['net_salary']                  = gross_salary - total_salary_share
paysheet_details['gross_salary']                = gross_salary
paysheet_details['paysheet_lines']              = pay_sheet_lines
paysheet_details['total_salary_share']          = total_salary_share
paysheet_details['taxable_net_salary']          = paysheet_details['net_salary'] + total_taxable_salary_share
paysheet_details['total_employer_share']        = total_employer_share
paysheet_details['total_taxable_salary_share']  = total_taxable_salary_share

# don't forget to add the current values to the yearly sum
paysheet_details['yearly_net_salary']           = yearly_net_salary + paysheet_details['net_salary']
paysheet_details['yearly_gross_salary']         = yearly_gross_salary + paysheet_details['gross_salary']
paysheet_details['yearly_salary_share']         = yearly_salary_share + paysheet_details['total_salary_share']
paysheet_details['yearly_employer_share']       = yearly_employer_share + paysheet_details['total_employer_share']
paysheet_details['yearly_taxable_net_salary']   = yearly_taxable_net_salary + paysheet_details['taxable_net_salary']

return paysheet_details
