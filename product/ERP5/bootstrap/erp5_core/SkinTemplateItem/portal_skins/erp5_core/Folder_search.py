request = container.REQUEST

from Products.ZSQLCatalog.SQLCatalog import Query, NegatedQuery, ComplexQuery

# Convert mapping from request.form into something the catalog can understand
# This script uses ad-hoc values that are understood by
# Folder_viewSearchDialog: x_value_ and x_usage_ are used to remember what was
# the entered value, and what was the usage.

# Note that we don't use queries, because we want to let the catalog filter out
# ignored parameters by itself.

new_mapping = dict(ignore_hide_rows=1)
query_list = []
left_join_list = []
for key in sorted(request.form.keys()):
  # we use sorted to make sure x_search_key appears before x
  value = request.form[key]
  # to remove unnecessary None value
  if value is None:
    request.form.pop(key)
    continue
  
  # workaround the bogus case where a value is passed ?value=None
  if value == 'None':
    value = None

  # remove Formulator markers
  if key.startswith('default_field_') or key.startswith('field_'):
    request.form.pop(key)
    continue

  if key.endswith('_search_key') and value:
    real_key = key[:-11]
    new_mapping[real_key] = dict(query=new_mapping[real_key], key=value)

  elif key.endswith('_usage_') and value:
    request.form.pop(key)
    real_key = key[:-7]
    new_mapping['%s_value_' % real_key] = new_mapping[real_key]
    new_mapping['%s_usage_' % real_key] = value
    # TODO: this is a quick and dirty implementation of what should be done by
    # Query.asSearchTextExpression. Instead of keeping '%s_value_' and '%s_usage_',
    # we'll simply keep the query.
    new_mapping[real_key] = '%s %s' % (value, new_mapping[real_key])

  else:
    if request.form.get('%s_is_excluded_' % key):
      # Build a negated query
      nq_kw = {'strict_%s' % key : value}
      q_kw = {key : None}
      left_join_list.append(key) 
      left_join_list.append('strict_%s' % key)
      query_list.append(ComplexQuery(NegatedQuery(Query(**nq_kw)), Query(**q_kw), logical_operator="OR"))
      new_mapping[key] = ""
      new_mapping["dialog_%s" %(key,)] = value
      new_mapping["dialog_excluded_%s" %(key,)] = True
    else:
      if request.form.get('%s_is_strict_' % key):
        new_mapping['strict_%s' % key] = value
        new_mapping['dialog_strict_%s' % key] = value
      else:
        new_mapping[key] = value
        new_mapping['dialog_%s' % key] = value

      
new_mapping["query"] = ComplexQuery(query_list)
new_mapping['left_join_list'] = left_join_list

# set selection parameters
container.portal_selections.setSelectionParamsFor(selection_name, new_mapping)

request.form.update(new_mapping)
return getattr(context, form_id)(request)
