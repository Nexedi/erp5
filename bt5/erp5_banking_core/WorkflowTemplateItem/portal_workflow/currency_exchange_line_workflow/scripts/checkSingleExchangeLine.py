from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message
from DateTime import DateTime


exchange_line = state_change['object']

# In this script, we will make sure it is impossible to get two 
# exchange lines opened in the same time.

if exchange_line.getBasePrice() in (None, 0, 0.0):
  msg = Message(domain = 'ui', message = 'Sorry, you must define a fixing price.')
  raise ValidationFailed, (msg,)


# We have to looking for other currency exchanges lines
# Note: SupplyCell is the class of Currency Exchange Line portal type objects
# But in reality, anything should do.
temp_object = context.getPortalObject().newContent(temp_object=True,
  portal_type='Supply Cell', id='temp_object')
start_date = exchange_line.getStartDate()
temp_kw = {'category_list':['resource/%s' % exchange_line.getParentValue().getRelativeUrl(),
                            'price_currency/%s' % exchange_line.getPriceCurrency()],
           'start_date':start_date
          }
temp_object.edit(**temp_kw)
line_list = [x for x in exchange_line.portal_domains.searchPredicateList(temp_object,
                                            portal_type='Currency Exchange Line',
                                            validation_state='validated',
                                            test=1)
             if x.getUid()!=exchange_line.getUid()]


start_date = exchange_line.getStartDate()
if start_date is None:
  msg = Message(domain = 'ui', message = 'Sorry, you must define a start date.')
  raise ValidationFailed, (msg,)

# Make sure there is not two exchange lines wich defines the same dates
# for this particular ressource and price_currency
for line in line_list:
  if line.getStopDate() is None or line.getStopDate()>line.getStartDate():
    line.setStopDate(start_date)
