#  - Weeks always starts at 0H of the last Sunday and finish at 0h of
#  the next sunday.

from Products.ERP5Type.Message import translateString
from Products.ERP5Type.Document import newTempBase
from Products.PythonScripts.standard import url_quote
from string import zfill

portal = context.getPortalObject()
request = context.REQUEST
domain_list = []
form_id=request.get('form_id')

selection_name = request.get('selection_name')
params = context.portal_selections.getSelectionParamsFor(selection_name, request)

bound_variation = params.get('bound_variation', 0)
bound_start = DateTime(params.get('bound_start', DateTime()))
bound_start = DateTime(bound_start.year() , bound_start.month() , bound_start.day())

# Normalize Week. XXX this should be in preferences as well
while bound_start.Day() is not 'Sunday':
  bound_start =  bound_start - 1
current_date =  bound_start + 7 * bound_variation
bound_stop  = current_date + 7
current_date =  DateTime(current_date.year() , current_date.month() , current_date.day())

default_link_url ='setLanePath?form_id=%s&list_selection_name=%s' %(
                                 form_id, selection_name)

# Define date format using user Preferences
date_order = portal.portal_preferences.getPreferredDateOrder()
date_format = dict(ymd='%Y/%m/%d',
                   dmy='%d/%m/%Y',
                   mdy='%m/%d/%Y').get(date_order, '%Y/%m/%d')

category_list = []
if depth == 0:
  # This case show Seven days
  while current_date < bound_stop:
    # Create one Temp Object
    o = newTempBase(portal, id='week', uid='new_%s' % zfill('week',4))
     # Setting Axis Dates start and stop
    o.setProperty('start',current_date)
    o.setProperty('stop', current_date+1)
    o.setProperty('relative_position', int(current_date))

    # Seting delimiter 
    if current_date.day() == 1:
      o.setProperty('delimiter_type', 2)
    elif current_date.day() == 15:
      o.setProperty('delimiter_type', 1)
    else:
      o.setProperty('delimiter_type', 0)

    title = translateString('${day_name} ${date}',
                            mapping=dict(day_name=translateString(current_date.Day()),
                                         date=current_date.strftime(date_format)))
    o.setProperty('title', title)

    # Defining ToolTip (Optional)
    tp = '%s %s' % (translateString(current_date.Day()), str(current_date))
    o.setProperty('tooltip', tp)

    # Defining Link (Optional)
    link = '%s&bound_start=%s&lane_path=base_day_domain' % ( default_link_url, url_quote(str(current_date)))
    o.setProperty('link', link)

    category_list.append(o)
    current_date = current_date + 1
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
