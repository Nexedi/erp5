#  - Years always starts at 0h of the current year's first day  and 
#    finish 0h of the next year's first day.

from Products.ERP5Type.Message import translateString
from Products.ERP5Type.Document import newTempBase
from Products.PythonScripts.standard import url_quote
from string import zfill

portal = context.getPortalObject()
request = context.REQUEST
domain_list = []
form_id=request.get('form_id')

selection_name = request.get('selection_name')
params = portal.portal_selections.getSelectionParamsFor(selection_name, request)

zoom_begin = DateTime(params.get('bound_start', DateTime()))
year = zoom_begin.year() + params.get('bound_variation', 0)
current_date = DateTime(year, 1, 1)

default_link_url ='setLanePath?form_id=%s&list_selection_name=%s' %(
                                 form_id, selection_name)

category_list = []
if depth == 0:
  # getting list of months
  count = 0
  while   count < 12:
    # Create one Temp Object
    o = newTempBase(portal, id='year' ,uid='new_%s' % zfill('year',4))
    # Seting delimiter 
    if current_date.month() in [1, 7]:
      o.setProperty('delimiter_type', 1)
    else:
      o.setProperty('delimiter_type', 0)
    
     # Setting Axis Dates start and stop
    o.setProperty('start',current_date)
    if current_date.month() != 12:
      stop_date = DateTime(current_date.year(),current_date.month() +1,1)
    else:
      stop_date = DateTime(year+1, 1, 1)
    o.setProperty('stop', stop_date)
    
    o.setProperty('relative_position', int(current_date))

    title = translateString('${month_name} ${year}',
                            mapping=dict(month_name=translateString(current_date.Month()),
                                         year=str(current_date.year())))
    o.setProperty('title', title)

    # Defining Link
    link = '%s&bound_start=%s&lane_path=base_month_domain' % ( default_link_url, url_quote(str(current_date)))
    o.setProperty('link', link)
    
    category_list.append(o)
    current_date = DateTime(str(current_date.year()) + '/' + str((current_date.month() +1)) + '/1')
    count += 1
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
