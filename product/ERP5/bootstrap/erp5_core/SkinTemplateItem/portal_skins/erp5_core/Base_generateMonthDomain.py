#  - Months always starts at 0h of the current month's first day  and
#  finish 0h of the next month's first day.

from Products.ERP5Type.Message import Message
from Products.ERP5Type.Document import newTempBase
from Products.PythonScripts.standard import url_quote
portal = context.getPortalObject()
request = context.REQUEST
domain_list = []

form_id=request.get('form_id')
selection_name = request.get('selection_name')
params = portal.portal_selections.getSelectionParamsFor(selection_name, request)

zoom_variation = params.get('bound_variation', 0)
bound_start = DateTime(params.get('bound_start', DateTime()))
zoom_begin = DateTime(bound_start.year(), bound_start.month(), bound_start.day())

# Normalize Month.
month = zoom_begin.month() + zoom_variation
year = zoom_begin.year() + (month - 1) // 12
month = month % 12
if month == 0:
  month = 12
current_date = DateTime(year, month, 1)
if month >= 12:
  year = year + 1
  month = 1
else:
  month = month + 1
axis_stop = DateTime(year, month, 1)


default_link_url ='setLanePath?form_id=%s&list_selection_name=%s' %(
                                 form_id, selection_name)

# Define date format using user Preferences
date_order = portal.portal_preferences.getPreferredDateOrder()
date_format = dict(ymd='%Y/%m/%d',
                   dmy='%d/%m/%Y',
                   mdy='%m/%d/%Y').get(date_order, '%Y/%m/%d')

category_list = []
if depth == 0:
  # recovering first date displayed, without time:
  while current_date < axis_stop:
    # Create one Temp Object
    o = newTempBase(portal, id=str(current_date.Day()),
                    uid='new_year')

     # Setting Axis Dates start and stop
    o.setProperty('start',current_date)
    o.setProperty('stop',current_date+3)
    o.setProperty('relative_position', int(current_date))

    # Seting delimiter
    if current_date.day() == 15:
      o.setProperty('delimiter_type', 1)
    else:
      o.setProperty('delimiter_type', 0)

    o.setProperty('title', current_date.strftime(date_format))
    tp = '%s %s' % (Message(domain='erp5_ui', message=current_date.Day(), mapping=None), str(current_date))
    o.setProperty('tooltip', tp)
    context.log(current_date)
    link = '%s&bound_start=%s&lane_path=base_week_domain' % ( default_link_url, url_quote(str(current_date)))
    o.setProperty('link', link)

    category_list.append(o)

    # go to next date
    current_date = current_date + 3
    current_date =  DateTime(current_date.year() , current_date.month() , current_date.day())
else:
  return domain_list

for category in category_list:
  domain = parent.generateTempDomain(id = 'sub' + category.getProperty('id'))
  domain.edit(title = category.getTitle(),
              membership_criterion_base_category = ('parent', ),
              membership_criterion_category = (category,),
              domain_generator_method_id = script.id,
              uid = category.getUid())

  domain_list.append(domain)

return domain_list
