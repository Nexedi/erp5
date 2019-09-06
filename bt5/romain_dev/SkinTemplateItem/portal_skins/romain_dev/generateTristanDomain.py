domain_list = []  # [<Temporary Domain at /erp5/portal_domains/my_module_domain/sub_domain>, ...]

##### Get parents' criterions ######

parents_criterion_dict = {}  # {"portal_type": {"identity": ["Task Report"]}), ...}
parents_membership_criterion_category_set = set()  # ["follow_up/project_module/xxx", ...]

sub_parent = parent
while depth > 0:
  for criterion in sub_parent.getCriterionList():
    property_id = criterion.property
    if property_id not in parents_criterion_dict:
      parents_criterion_dict[property_id] = {"min": criterion.min, "max": criterion.max, "identity": criterion.identity}
  sub_parent_membership_criterion_category_list = sub_parent.getMembershipCriterionCategoryList()
  # sub_parent.getMultimembershipCriterionBaseCategoryList() seems to return empty list...
  parents_membership_criterion_category_set.update(sub_parent_membership_criterion_category_list)
  depth -= 1
  sub_parent = sub_parent.getParentValue()

##### Define domain_list.append helper #####

def appendNewTempDomain(id, criterion_dict=None, membership_criterion_category_list=None, **kw):
  if criterion_dict is None:
    criterion_dict = parents_criterion_dict
  else:
    criterion_dict.update(parents_criterion_dict)
  if membership_criterion_category_list is None:
    membership_criterion_category_list = list(parents_membership_criterion_category_set)
  else:
    membership_criterion_category_list = list(parents_membership_criterion_category_set.union(membership_criterion_category_list))
  multimembership_criterion_base_category_list = list(set([c[:c.index("/")] for c in membership_criterion_category_list]))
  domain = parent.generateTempDomain(id=id)
  domain.edit(
    criterion_property_list=criterion_dict.keys(),
    multimembership_criterion_base_category_list=multimembership_criterion_base_category_list,
    membership_criterion_category_list=membership_criterion_category_list,
    domain_generator_method_id=script.id,
    **kw
  )
  for property_id, criterion_kw in criterion_dict.items():
    domain.setCriterion(property_id, **criterion_kw)
  domain_list.append(domain)

##### Provide sub domains #####
# Don't define domain that provides criterions already used by parents

if "delivery.start_date" not in parents_criterion_dict:
  now = DateTime()
  for time_frame in (1, 7, 30, 365):
    appendNewTempDomain(
      id="sub_time_frame_{}".format(time_frame),
      title="Last {} days".format(time_frame),
      criterion_dict={"delivery.start_date": {"min": now - time_frame}},
    )

person = context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()
if person is not None:
  category_relative_url = "source/" + person.getRelativeUrl()
  if category_relative_url not in parents_membership_criterion_category_set:
    appendNewTempDomain(
      id="sub_assigned_to_me_1",
      title="Assigned to me",
      membership_criterion_category_list=(category_relative_url,),
    )

return domain_list
