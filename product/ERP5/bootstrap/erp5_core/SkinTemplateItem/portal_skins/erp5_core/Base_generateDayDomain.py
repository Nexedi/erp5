from Products.ERP5Type.Message import translateString
from Products.ERP5Type.Document import newTempBase
portal = context.getPortalObject()
request = context.REQUEST
domain_list = []

selection_name = request.get('selection_name')
params = portal.portal_selections.getSelectionParamsFor(selection_name, request)

bound_start = DateTime(params.get('bound_start', DateTime()))
bound_start = DateTime(bound_start.year() , bound_start.month() , bound_start.day()) 

bound_start = bound_start + params.get('bound_variation', 0)
bound_stop = bound_start + 1


# Define date format using user Preferences
date_order = portal.portal_preferences.getPreferredDateOrder()
date_format = dict(ymd='%m/%d %H:00',
                   dmy='%d/%m %H:00',
                   mdy='%m/%d %H:00').get(date_order, '%m/%d %H:00')

category_list = []
if depth == 0:
  current_date = bound_start
 # This zoom will show one day divided in columns that represents 3 hours.
 # 0.125 means 3 hours in DateTime float format
  while current_date < bound_stop:
    # Create one Temp Object
    o = newTempBase(portal, id='year', uid='new_year')
    # Setting Axis Dates start and stop
    o.setProperty('start',current_date)
    o.setProperty('stop', current_date + 0.125)
    o.setProperty('relative_position', int(current_date))

    # Seting delimiter
    if current_date.hour() == 12:
      o.setProperty('delimiter_type', 1)
    else:
      o.setProperty('delimiter_type', 0)

    title = translateString('${day_name} ${date}',
               mapping=dict(day_name=translateString(current_date.Day()),
                            date=current_date.strftime(date_format)))
    o.setProperty('title', title)
    tp = '%s %s' % (translateString(current_date.Day()), str(current_date))
    o.setProperty('tooltip', tp)

    category_list.append(o)
    
    current_date  = current_date + 0.125

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
