"""
================================================================================
Return local parameters that require proxy role to access
================================================================================
"""

portal_type_valid_list = ["Web Site", "Web Section", "Web Page"]
portal_type = context.getPortalType()
portal_object = context.getPortalObject()

if REQUEST is not None:
  return None

if portal_type not in portal_type_valid_list:
  return None

def err(my_value):
  #return "XXX No " + my_value + " defined."
  return ""

def populateProductDictFromCategoryList(my_category_list):
  result_list = []
  for category in my_cateogry_list:
    if category.find("follow_up/") > -1:
      output_dict = {}
      stripped_category_url = category.replace("follow_up/", "")
      stripped_category_url_title = portal_object.restrictedTraverse(
        stripped_category_url
      ).getTitle()
      output_dict["title"] = stripped_category_url_title or err("product software")
      result_list.append(output_dict)
  return result_list

def populateOrganisationDict(my_organisation_list):
  result_list = []
  for organisation in my_organisation_list:
    output_dict = {}
    output_dict["title"] = organisation.getTitle() or err("title")
    output_dict["organisation"] = organisation.getCorporateName() or err("corporate_name")
    result_list.append(output_dict)
  return result_list

def populateProductDict(my_product_list):
  result_list = []
  for product in my_product_list:
    output_dict = {}
    output_dict["title"] = product.getTitle() or err("product software")
    result_list.append(output_dict)
  return result_list

def populatePersonDict(my_person_list):
  result_list = []
  for person in my_person_list:
    output_dict = {}

    person_default_telephone = person.getDefaultTelephoneValue()
    person_default_mail = person.getDefaultEmail()

    output_dict["name"] = person.getTitle() or err("title")
    output_dict["title"] = person.getFunctionTitle() or err("function title")
    output_dict["uid"] = person.getUid() or err("uid")
    if person_default_telephone is not None:
      output_dict["phone"] = person_default_telephone.getCoordinateText() or err("phone")
    else:
      output_dict["phone"] = err("phone")
    if person_default_mail is not None:
      output_dict["email"] = person_default_mail.getUrlString() or err("email")
    else:
      output_dict["email"] = err("email")
    result_list.append(output_dict)
  return result_list

# "ERP5 Software" => erp5
def getSubstringFromProduct(my_candidate, my_as_is):
  software_match_string = " Software"
  software_title = my_candidate.get("title") or ""
  if software_title.find(software_match_string) > 1:
    if my_as_is is True:
      return software_title.split(software_match_string)[0]
    return software_title.split(software_match_string)[0].lower()

def callSelf(my_parameter, my_source_id, my_flag_site):
  return context.WebPage_getLocalProxyParameter(
    parameter=my_parameter,
    source_uid=my_source_id,
    flag_site=my_flag_site
  )

pass_parameter = kw.get("parameter", None)
pass_source_data = kw.get("source_data", None)
pass_flag_site = kw.get("flag_site", None)

if pass_parameter is not None and pass_source_data is not None:
  # ---------------------- Author (Contributors) -------------------------------
  if pass_parameter == "author":
    return populatePersonDict(context.getContributorValueList(*args, **kw))

  # ----------------- Publisher (Follow-Up Organisation) -----------------------
  if pass_parameter == "publisher":
    return populateOrganisationDict(context.getFollowUpValueList(
      portal_type="Organisation",
      checked_permission='View',
      follow_up_related_uid=pass_source_data
    ))

  # ------------------------- Product (Website) --------------------------------
  if pass_parameter == "product":
    if pass_flag_site == True:
      return populateProductDictFromCategoryList(
        context.getWebSiteValue().getMembershipCriterionCategoryList() or []
      )
    elif pass_source_data is not None:
      return populateProductDict(context.getFollowUpValueList(
        portal_type=pass_parameter,
        checked_permission='View',
        follow_up_related_uid=pass_source_data
      ))

  # --------------------------- Theme (Website) --------------------------------
  if pass_parameter == "theme":
    theme = None
    product_candidate_list = callSelf("product", pass_source_data, pass_flag_site)

    if product_candidate_list is not None:
      if len(product_candidate_list) > 0:
        theme = getSubstringFromProduct(product_candidate_list[0], None)

    # XXX no more overrides here, use override parameters on slideshow
    # OSOE Sonderlocke
    #if theme is None:
    #  osoe_match_string = "osoe"
    #  category_candidate_list = context.getCategoryList() or []
    #  for category in category_candidate_list:
    #    if category.find(osoe_match_string) > 1:
    #      theme = osoe_match_string

    # MyNij Sonderlocke
    #if theme is None:
    #  organisation_candidate_list = callSelf("Organisation", source_uid, None)
    #  if len(organisation_candidate_list) > 0:
    #    theme = organisation_candidate_list[0].get('title').lower()

    return theme
