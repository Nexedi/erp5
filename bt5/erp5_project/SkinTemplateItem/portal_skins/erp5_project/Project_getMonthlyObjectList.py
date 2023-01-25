# This script is called by each line of the domain in order to know if returned objects
#by the domain have the same property than returned objects

object_domain = selection_report.asDomainItemDict()['project_report_monthly_domain']
object_dict = context.object_dict
summary_dict = context.summary_dict

current_criterion = object_domain.getCriterionList()
date = current_criterion[0].identity
result_list = []
if len(object_domain.getMembershipCriterionBaseCategoryList())==0:
  # First level, so level of month, we display summary of total
  # quantity per worker for the full month
  returned_object = summary_dict.get(date, None)
  if returned_object is not None:
    result_list.append(returned_object)
else:
  returned_object = object_dict.get(date, None)
  if returned_object is not None:
    # optimisation, in this report we have exactly one temp object at most
    # matching our domain, and we have already a dict with nice keys, so
    # there is no need to parse all temp objects
    membership_criterion_category_list = object_domain.getMembershipCriterionCategoryList()
    assert len(membership_criterion_category_list) == 1
    membership_criterion_category = membership_criterion_category_list[0]
    assert membership_criterion_category.startswith('source_project/')
    project_relative_url = membership_criterion_category[len('source_project/'):]
    if project_relative_url in returned_object:
      result_list.append(returned_object[project_relative_url])
return result_list
