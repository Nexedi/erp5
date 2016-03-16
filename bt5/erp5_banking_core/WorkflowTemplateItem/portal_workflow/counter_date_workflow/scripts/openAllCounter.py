from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message
counter_date = state_change['object']

# First make sure that the site is defined
site_value = counter_date.getSiteValue()
if site_value is None:
  msg = Message(domain='ui',message="Sorry, the site is not defined")
  raise ValidationFailed (msg,)

# Then, make sure there is not any counter date open for this site
site_value.serialize()
site_uid = site_value.getUid()
activity_tag = '%s_CounterDay' % (site_uid, )
if context.getPortalObject().portal_activities.countMessageWithTag(activity_tag) != 0:
  msg = Message(domain='ui',message="Sorry, there is a pending counter date opening, please retry later")
  raise ValidationFailed (msg,)
counter_date.setDefaultActivateParameterDict({"tag": activity_tag})
counter_date_list = [x.getObject() for x in counter_date.portal_catalog(portal_type='Counter Date',site_uid=site_uid,simulation_state='open')]
for other_counter in counter_date_list:
  if other_counter.getUid()!=counter_date.getUid():
    counter_date.log("opened counter date is", other_counter.getPath())
    msg = Message(domain='ui',message="Sorry, there is already a counter date opened")
    raise ValidationFailed (msg,)
    
listbox = state_change.kwargs.get('listbox',None)

# First make sure we can open a counter date only
# if the date defined on the document is the current date
start_date = counter_date.getStartDate()
from DateTime import DateTime
now = DateTime()

# Check it is a working day
if len(getattr(context.getPortalObject(), 'not_working_days', "")) == 0:
  pass
else:
  not_working_day_list = getattr(context.getPortalObject(), 'not_working_days').split(" ")
  if start_date.Day().lower() in not_working_day_list:
    msg = Message(domain='ui',message="Sorry, you cannot open the date on not working days")
    raise ValidationFailed (msg,)


# Check it is today
check_date_is_today = state_change.kwargs.get('check_date_is_today', 1)
if check_date_is_today and now.Date() != start_date.Date():
  msg = Message(domain='ui',message="Sorry, the date is not today")
  raise ValidationFailed (msg,)




if listbox is not None:
  for line in listbox:
    if line["choice"] == "open":
      counter = context.restrictedTraverse("%s" %(line['listbox_key'],))
      counter.open()


# Set a reference
first_day_of_year = DateTime(start_date.year(), 1, 1)
counter_date_list = [x.getObject() for x  in context.portal_catalog(
                                           portal_type='Counter Date',site_uid=site_uid,
                                           start_date={'query': first_day_of_year, 'range': 'min'},
                                           sort_on=[('start_date','descending')],limit=1,
                                           simulation_state=('open','closed'))]
previous_reference = None
if len(counter_date_list)>0:
  previous_counter_date = counter_date_list[0]
  previous_reference = previous_counter_date.getReference()
if previous_reference not in ('',None):
  reference = '%i' % (int(previous_reference)+1)
else:
  reference = '1'
counter_date.setReference(reference)
