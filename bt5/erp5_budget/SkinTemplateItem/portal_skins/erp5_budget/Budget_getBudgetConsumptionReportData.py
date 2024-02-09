import six
from pprint import pformat
portal = context.getPortalObject()
request= portal.REQUEST
from_date = request.get('from_date')
at_date = request.get('at_date')

# this report can be called on a budget ...
if context.getPortalType() == 'Budget':
  defined_group = 'group'
  if 'group' in context.getVariationBaseCategoryList():
    for category in context.getVariationCategoryList():
      if category.startswith('group/'):
        defined_group = category
  budget_list = (context,)
else:
  # ... or on the budget module, and in this case, all budgets are used
  defined_group = request['section_category']
  validation_state = request.get('validation_state', [])
  strict_section_membership = request.get('section_category_strict', False)
  search_kw = dict(portal_type='Budget',
                   validation_state=validation_state)
  budget_type = request.get('budget_type')
  if budget_type:
    search_kw['default_budget_type_uid'] = [portal.portal_categories.budget_type.restrictedTraverse(x).getUid() for x in budget_type if x]
  specialise = request.get('specialise')
  if specialise:
    search_kw['default_specialise_uid'] = [portal.restrictedTraverse(x).getUid() for x in specialise if x]

  budget_list = portal.portal_catalog.searchResults(**search_kw)
  group_filtered_budget_list = []
  filtered_budget_list = []
  for budget in budget_list:
    budget = budget.getObject()
    if budget.isMemberOf(defined_group, strict_membership=strict_section_membership):
      group_filtered_budget_list.append(budget)

  if from_date or at_date:
    for budget in group_filtered_budget_list:
      if from_date and budget.getStartDateRangeMax() < from_date:
        continue
      if at_date and budget.getStartDateRangeMin() > at_date:
        continue
      filtered_budget_list.append(budget)
    group_filtered_budget_list = filtered_budget_list

  budget_list = group_filtered_budget_list

line_list = []

target_currency_title = None
target_currency = None
conversion_ratio = None
if request.get('price_currency'):
  target_currency = portal.restrictedTraverse(request['price_currency'])
  target_currency_title = target_currency.getReference()


def isVisibleCell(cell_key):
  # can this cell be viewed by this user ?
  for category in cell_key:
    if category.startswith('group/'):
      # strict group membership seems useless at cell level
      if not category.startswith(defined_group):
        return False
  return True





# in this report, level 1 is the budget line structure,
# level 2 is the first variation category
# level 3 is the second variation category
# level 4 is the third variation category, or nothing
for budget in budget_list:

  if target_currency is not None:
    # FIXME: this target currency support is not supported and have to be
    # rewritten / removed
    conversion_ratio = target_currency.getPrice(
         context=budget.asContext(
                categories=[
                  'resource/%s' % budget.getResourceRelativeUrl(),
                  'price_currency/%s' %
                    target_currency.getRelativeUrl()],
               start_date=request.get('conversion_date') or
               budget.getStartDateRangeMin()))
    if not conversion_ratio:
      conversion_ratio = 1

  line_list.append(dict(is_budget=True,
                        title=six.text_type(budget.getTitle()),
                        target_currency_title=target_currency_title,
                        conversion_ratio=conversion_ratio,
                        resource_title=budget.getResource() and
                                 budget.getResourceReference()))

  # To get the count of lines correct (for the print range)
  if target_currency_title:
    line_list.append({})

  for budget_line in budget.contentValues(sort_on=(('int_index', 'asc'),)):
    total_level_1_initial_budget = 0
    total_level_1_current_budget = 0
    total_level_1_engaged_budget = 0
    total_level_1_consumed_budget = 0
    total_level_1_available_budget = 0

    level_1_line_list = []

    if at_date and from_date:
      consumed_budget_dict = budget_line.getConsumedBudgetDict(
                                    from_date=from_date, at_date=at_date)
      engaged_budget_dict = budget_line.getEngagedBudgetDict(
                                    from_date=from_date, at_date=at_date)
    elif at_date:
      consumed_budget_dict = budget_line.getConsumedBudgetDict(at_date=at_date)
      engaged_budget_dict = budget_line.getEngagedBudgetDict(at_date=at_date)
    elif from_date:
      consumed_budget_dict = budget_line.getConsumedBudgetDict(from_date=from_date)
      engaged_budget_dict = budget_line.getEngagedBudgetDict(from_date=from_date)
    else:
      consumed_budget_dict = budget_line.getConsumedBudgetDict()
      engaged_budget_dict = budget_line.getEngagedBudgetDict()

    # We use 'engaged' cell_id because we are supposed to have more engagements than consumptions
    budget_line_cell_range = budget_line.BudgetLine_asCellRange('engaged')
    budget_line_as_cell_range_matrixbox =\
          budget_line.BudgetLine_asCellRange('engaged', matrixbox=1)

    dependant_dimension_dict = budget_line.BudgetLine_getSummaryDimensionKeyDict()

    if len(budget_line_cell_range) == 0:
      continue
    if len(budget_line_cell_range) == 1:
      # if there's only one dimension, we add a virtual level 2, to keep the
      # same structure
      level_2_variation_category_list = [budget_line.getResource(base=1)]
      level_3_variation_category_list = budget_line_cell_range[0]
      level_4_variation_category_list = [None]
    elif len(budget_line_cell_range) == 2:
      level_2_variation_category_list = budget_line_cell_range[1]
      level_3_variation_category_list = budget_line_cell_range[0]
      level_4_variation_category_list = [None]
    else:
      level_2_variation_category_list = budget_line_cell_range[2]
      level_3_variation_category_list = budget_line_cell_range[1]
      level_4_variation_category_list = budget_line_cell_range[0]

    # we use BudgetLine_asCellRange to get cell names, and have a default value
    # for "virtual level 2"
    title = six.text_type(budget_line.getTitle())
    cell_name_dict = {budget_line.getResource(base=1):
                          six.text_type(budget_line.getTitle())}
    cell_style_dict = {budget_line.getResource(base=1): 'Level2'}
    cell_depth_dict = {budget_line.getResource(base=1): 0}

    # calculate the depth for styling
    min_depth = 100
    for cell_range_list in budget_line_as_cell_range_matrixbox:
      for category, title in cell_range_list:
        if category in level_2_variation_category_list:
          min_depth = min((title.count('\xA0') / 4) or title.count('/'),
                          min_depth)

    if min_depth == 100:
      min_depth = 0

    for cell_range_list in budget_line_as_cell_range_matrixbox:
      for category, title in cell_range_list:
        cell_name_dict[category] = six.text_type(title).replace(u'\xA0', '')
        if category in level_2_variation_category_list:
          depth = -min_depth + (title.count('\xA0') / 4) or title.count('/')
          cell_depth_dict[category] = depth
          if depth == 1:
            cell_style_dict[category] = 'Level2.1'
          elif depth == 2:
            cell_style_dict[category] = 'Level2.2'
          elif depth == 3:
            cell_style_dict[category] = 'Level2.3'
          else:
            cell_style_dict[category] = 'Level2'

    sign = budget_line.BudgetLine_getConsumptionSign()

    for level_2_category in level_2_variation_category_list:

      total_level_2_initial_budget = 0
      total_level_2_current_budget = 0
      total_level_2_engaged_budget = 0
      total_level_2_consumed_budget = 0
      total_level_2_available_budget = 0
      level_2_line_list = [dict(is_level_2=True,
                                title=cell_name_dict[level_2_category],
                                style=cell_style_dict[level_2_category])]

      is_higher_level2 = level_2_category not in dependant_dimension_dict

      for level_3_category in level_3_variation_category_list:
        total_level_3_initial_budget = 0
        total_level_3_current_budget = 0
        total_level_3_engaged_budget = 0
        total_level_3_consumed_budget = 0
        total_level_3_available_budget = 0

        level_3_line_list = [dict(is_level_3=True,
                                  title=cell_name_dict[level_3_category],)]

        is_higher_level3 = level_3_category not in dependant_dimension_dict

        for level_4_category in level_4_variation_category_list:
          # TODO: maybe fail if only 1 dimension ...
          if level_4_category is None:
            cell_key = (level_3_category, level_2_category)
          else:
            cell_key = (level_4_category, level_3_category, level_2_category)

          if not isVisibleCell(cell_key):
            continue

          consumed_budget = consumed_budget_dict.get(cell_key, None)
          engaged_budget = engaged_budget_dict.get(cell_key, None)
          cell = budget_line.getCell(*cell_key)
          if cell is None \
              and consumed_budget is None \
              and engaged_budget is None:
            continue

          if not consumed_budget:
            consumed_budget = 0
          if not engaged_budget:
            engaged_budget = 0

          initial_budget = 0
          if cell is not None:
            initial_budget = cell.getQuantity() * sign

          # XXX don't calculate current balance unless we use budget
          # transactions
          current_budget = initial_budget #cell.getCurrentBalance() * sign


          # XXX stupid optimisation that may not always be true:
          # if there's no engaged budget, there's no consumed budget
          if engaged_budget:
            # XXX calculate manually getAvailableBudget, because it calls
            # getEngagedBudget again
            # available_budget = cell.getAvailableBudget()
            available_budget = (current_budget or 0) - engaged_budget
          else:
            available_budget = current_budget

          if initial_budget:
            total_level_3_initial_budget += initial_budget
          if current_budget:
            total_level_3_current_budget += current_budget
          total_level_3_engaged_budget += engaged_budget
          total_level_3_consumed_budget += consumed_budget
          if available_budget:
            total_level_3_available_budget += available_budget

          consumed_ratio = 0
          if current_budget:
            consumed_ratio = consumed_budget / current_budget

          if level_4_category is not None:
            level_3_line_list.append(dict(title=cell_name_dict[level_4_category],
                                          is_level_4=True,
                                          initial_budget=initial_budget,
                                          current_budget=current_budget,
                                          engaged_budget=engaged_budget,
                                          consumed_budget=consumed_budget,
                                          available_budget=available_budget,
                                          consumed_ratio=consumed_ratio))


        if is_higher_level3:
          total_level_2_initial_budget += total_level_3_initial_budget
          total_level_2_current_budget += total_level_3_current_budget
          total_level_2_engaged_budget += total_level_3_engaged_budget
          total_level_2_consumed_budget += total_level_3_consumed_budget
          total_level_2_available_budget += total_level_3_available_budget

        if len(level_3_line_list) > 1 or level_4_category is None:
          consumed_ratio = 0
          if total_level_3_current_budget:
            consumed_ratio = total_level_3_consumed_budget / total_level_3_current_budget
          level_2_line_list.append(dict(title=cell_name_dict[level_3_category],
                                        is_level_3=True,
                                        initial_budget=total_level_3_initial_budget,
                                        current_budget=total_level_3_current_budget,
                                        engaged_budget=total_level_3_engaged_budget,
                                        consumed_budget=total_level_3_consumed_budget,
                                        available_budget=total_level_3_available_budget,
                                        consumed_ratio=consumed_ratio))
          if level_4_category is not None:
            level_2_line_list.append(level_3_line_list)

      if len(level_2_line_list) > 1:
        consumed_ratio = 0
        if total_level_2_current_budget:
          consumed_ratio = total_level_2_consumed_budget / total_level_2_current_budget
        level_1_line_list.append(dict(is_level_2=True,
                                      title=cell_name_dict[level_2_category],
                                      style=cell_style_dict[level_2_category],
                                      initial_budget=total_level_2_initial_budget,
                                      current_budget=total_level_2_current_budget,
                                      engaged_budget=total_level_2_engaged_budget,
                                      consumed_budget=total_level_2_consumed_budget,
                                      available_budget=total_level_2_available_budget,
                                      consumed_ratio=consumed_ratio))
        level_1_line_list.append(level_2_line_list)

      if is_higher_level2:
        total_level_1_initial_budget += total_level_2_initial_budget
        total_level_1_current_budget += total_level_2_current_budget
        total_level_1_engaged_budget += total_level_2_engaged_budget
        total_level_1_consumed_budget += total_level_2_consumed_budget
        total_level_1_available_budget += total_level_2_available_budget

    if len(level_1_line_list) > 1:
      consumed_ratio = 0
      if total_level_1_current_budget:
        consumed_ratio = total_level_1_consumed_budget / total_level_1_current_budget
      line_list.append(dict(is_level_1=True,
                            title=six.text_type(budget_line.getTitle()),
                            initial_budget=total_level_1_initial_budget,
                            current_budget=total_level_1_current_budget,
                            engaged_budget=total_level_1_engaged_budget,
                            consumed_budget=total_level_1_consumed_budget,
                            available_budget=total_level_1_available_budget,
                            consumed_ratio=consumed_ratio))
      line_list.extend(level_1_line_list)

line_count = 0
for line in line_list:
  if same_type(line, []):
    line_count += len(line)
  else:
    line_count += 1

if not REQUEST:
  return line_list, line_count

return pformat(line_list)
