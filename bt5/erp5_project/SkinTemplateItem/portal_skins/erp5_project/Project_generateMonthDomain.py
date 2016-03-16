request = context.REQUEST

project_line_portal_type = 'Project Line'

domain_list = []

here = context.REQUEST['here']
portal = context.getPortalObject()
form_id=request.get('form_id')
selection_name = request.get('selection_name')
params = portal.portal_selections.getSelectionParamsFor(selection_name, request)
object_path = request.get('object_path')
if object_path is None:
  object_path = context.REQUEST.get('URL1').split('/')[-1]
search_path = 'project_module/%s/%%' % object_path
category_list = []

if depth == 0:
  # Get start date and stop date from document
  from_date = request.get('from_date')
  at_date = request.get('at_date')
  current_month = None
  # We must initialize from_date at the beginning of the month
  current_date = from_date
  is_total = here.is_total
  if is_total:
    category_list.append(here.getObject().asContext(title=here.full_date_string,
                                                    string_index=here.full_date_string,
                                                    ))
  else:
    month_dict = request.form.get('month_dict', None)
    if month_dict is None:
      month_dict = {}
      current_date_year = current_date.year()
      current_date_month = current_date.month()
      at_date_year = at_date.year()
      at_date_month = at_date.month()
      while True:
        month_dict[(current_date_year, current_date_month)] = 1
        if current_date_year == at_date_year and current_date_month == at_date_month:
          break
        current_date_month += 1
        if current_date_month == 13:
          current_date_month = 0
          current_date_year += 1
      request.form['month_dict'] = month_dict

    category_list = []
    #i = 1
    month_dict_list = month_dict.keys()
    month_dict_list.sort()
    for year, month in month_dict_list:
      category_list.append(here.getObject().asContext(title="%s - %s" % (year, month),
                                                      string_index="%s-%s" % (year, month),
                                                      ))
      #i += 1

else:
  object_dict = here.object_dict
  string_index = getattr(parent, 'string_index')
  object_sub_dict = object_dict.get(string_index, {})
  object_url_dict = {}
  project_to_display_dict = here.monthly_project_to_display_dict.get(string_index, {})
  if depth == 1:
    category_list = [here.project_dict[x] for x in project_to_display_dict.keys() if
                        here.project_dict.has_key(x)]
  else:
    parent_category_list = parent.getMembershipCriterionCategoryList()
    category_list = []
    # Very specific to the monthly report, if no data, we do not display the current tree part
    # sor first, for performance, build a dict with all relative urls of project line that will
    # need to be displayed for this month
    object_dict = here.object_dict

    object_sub_dict = object_dict.get(getattr(parent, 'string_index'), {})
    object_url_dict = {}
    for parent_category in parent_category_list:
      parent_category = '/'.join(parent_category.split('/')[1:])
      if project_to_display_dict.has_key(parent_category):
	parent_category_object = context.restrictedTraverse(parent_category)
	category_child_list = parent_category_object.contentValues(portal_type=project_line_portal_type)
	#category_list.append(parent_category_object)
	for category_child in category_child_list:
	  if project_to_display_dict.has_key(category_child.getRelativeUrl()):
	    category_list.append(category_child)


i = 0
for category in category_list:
  string_index = getattr(category, 'string_index', None)
  if string_index is None:
    string_index = getattr(parent, 'string_index')
  domain_kw = {}
  if depth >= 1:
    domain_kw['membership_criterion_base_category'] = ('source_project', )
    domain_kw['membership_criterion_category'] = ('source_project/' + category.getRelativeUrl(),)
  domain = parent.generateTempDomain(id = '%s_%s' % (depth, i))
  domain.edit(title = category.getTitle(),
              domain_generator_method_id = script.id,
              criterion_property_list = ['string_index'] ,
              string_index = string_index,
              uid = category.getUid(),
              **domain_kw)
  domain.setCriterion('string_index', identity=string_index)
  domain_list.append(domain)
  i += 1

return domain_list
