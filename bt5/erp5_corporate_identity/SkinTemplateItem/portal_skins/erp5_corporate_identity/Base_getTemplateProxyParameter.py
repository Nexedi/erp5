"""
================================================================================
Return local parameters that require proxy role to access
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
# pass_parameter             (portal-) type of data to fetch
# pass_source_data           followup uid or context for retrieving info
# pass_flag_site             whether called from a web site (no follow-up)

portal_type_valid_template_list = ["Web Site", "Web Section", "Web Page", "Letter"]
portal_type_valid_report_list = ["Project", "Sale Order", "Sale Opportunity", "Requirement Document"]
portal_type = context.getPortalType()
portal_object = context.getPortalObject()
validation_state = ('released', 'released_alive', 'published', 'published_alive',
            'shared', 'shared_alive', 'public', 'validated')

if REQUEST is not None:
  return None

if portal_type not in portal_type_valid_template_list and portal_type not in portal_type_valid_report_list:
  return None

def err(my_value):
  #return "XXX No " + my_value + " defined."
  return ""

def populateProductDictFromCategoryList(my_category_list):
  result_list = []
  for category in my_category_list:
    if category.find("follow_up/") > -1:
      output_dict = {}
      stripped_category_url = category.replace("follow_up/", "")
      stripped_category_url_title = portal_object.restrictedTraverse(
        stripped_category_url
      ).getTitle()
      output_dict["title"] = stripped_category_url_title or err("product software")
      result_list.append(output_dict)
  return result_list

def populateProductDict(my_product_list):
  result_list = []
  for product in my_product_list:
    output_dict = {}
    output_dict["title"] = product.getTitle() or err("product software")
    result_list.append(output_dict)
  return result_list

def populateImageDict(my_image_list):
  result_list = []
  for image in my_image_list:
    output_dict = {}
    output_dict["relative_url"] = image.getRelativeUrl()
    output_dict["reference"] = image.getReference() or err("reference")
    output_dict["description"] = image.getDescription() or err("description")
    result_list.append(output_dict)
  return result_list

def populateBankDict(my_bank_list):
  result_list = []
  for bank in my_bank_list:
    output_dict = {}
    output_dict["bank"] = bank.getTitle() or err("bank account title")
    output_dict["iban"] = bank.getIban() or err("iban")
    output_dict["bic"] =  bank.getBicCode() or err("bic")
    result_list.append(output_dict)
  return result_list

def populatePersonDict(my_person_list):
  result_list = []
  for person in my_person_list:
    output_dict = {}

    person_default_telephone = person.getDefaultTelephoneValue()
    person_default_mail = person.getDefaultEmail()
    person_address = person.getDefaultAddress()
    person_region = person.getRegionValue()

    output_dict["name"] = person.getTitle() or err("title")
    output_dict["title"] = person.getFunctionTitle() or err("function title")
    output_dict["uid"] = person.getUid() or err("uid")
    if person.getDefaultAddress() is not None:
      output_dict["address"] = person_address.getStreetAddress() or err("street address")
      output_dict["postal_code"] = person_address.getZipCode() or err("postal code")
      output_dict["city"] = person_address.getCity() or err("city")
    else:
      output_dict["address"] = err("street_adress")
      output_dict["postal_code"] = err("postal_code")
      output_dict["city"] = err("city")
    if person_region is not None:
      output_dict["country"] = person_region.getTitle() or err("country")
      output_dict["codification"] = person_region.getCodification() or err("country code")
    else:
      output_dict["country"] = err("country")
      output_dict["codification"] = err("country code")
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

def populateOrganisationDict(my_organisation_list):
  result_list = []
  for organisation in my_organisation_list:
    output_dict = {}

    organisation_address = organisation.getDefaultAddress()
    organisation_region = organisation.getRegionValue()
    organisation_phone = organisation.getDefaultTelephoneValue()
    organisation_fax = organisation.getDefaultFax()
    organisation_link_list = organisation.objectValues(portal_type="Link",title="Corporate Web Site")
    organisation_bank_list = organisation.objectValues(portal_type="Bank Account",title="Default Bank Account")
    organisation_default_image = organisation.getDefaultImage()

    output_dict["organisation_title"] = organisation.getTitle()
    output_dict["corporate_name"] = organisation.getCorporateName() or err("corporate name")
    output_dict["description"] = organisation.getDescription() or err("description")
    output_dict["social_capital"] = organisation.getSocialCapital() or err("social capital")
    output_dict["activity_code"] = organisation.getActivityCode() or err("activitiy code")

    #output_dict["logo_url"] = organisation.getDefaultImageAbsoluteUrl() or err("logo_url")
    if organisation_default_image is not None:
      output_dict["logo_url"] = organisation_default_image.getRelativeUrl()
    else:
      output_dict["logo_url"] = err("logo_url")

    # XXX we should have social_capital_currency and corporate_registration_court
    output_dict["social_capital_currency"] = err("social capital")
    output_dict["corporate_registration_code"] = err("corporate_registration_code")

    output_dict["vat"] = organisation.getVatCode() or err("vat")
    output_dict["corporate_registration"] = organisation.getCorporateRegistrationCode() or err("corporate_registration")
    output_dict["email"] = organisation.getDefaultEmailText() or err("email")
    if organisation.getDefaultAddress() is not None:
      output_dict["address"] = organisation_address.getStreetAddress() or err("street address")
      output_dict["postal_code"] = organisation_address.getZipCode() or err("postal code")
      output_dict["city"] = organisation_address.getCity() or err("city")
    else:
      output_dict["address"] = err("street address")
      output_dict["postal_code"] = err("postal code")
      output_dict["city"] = err("city")
    if organisation_region is not None:
      output_dict["country"] = organisation_region.getTitle() or err("country")
      output_dict["codification"] = organisation_region.getCodification() or err("country code")
    else:
      output_dict["country"] = err("country")
      output_dict["codification"] = err("country code")
    if organisation_phone is not None:
      output_dict["phone"] = organisation_phone.getDefaultTelephoneCoordinateText() or err("phone")
    else:
      output_dict["phone"] = err("phone")
    if organisation_fax is not None:
      output_dict["fax"] = organisation_fax.getCoordinateText() or err("fax")
    else:
      output_dict["fax"] = err("fax")
    if len(organisation_link_list) == 1:
      output_dict["website"] = organisation_link_list[0].getUrlString() or err("Website")
    else:
      output_dict["website"] = err("web site")
    if len(organisation_bank_list) > 0:
      output_dict["bank"] = organisation_bank_list[0].getTitle() or err("bank account title")
      output_dict["iban"] = organisation_bank_list[0].getIban() or err("iban")
      output_dict["bic"] =  organisation_bank_list[0].getBicCode() or err("bic")
    else:
      output_dict["bank"] = err("bank")
      output_dict["iban"] = err("iban")
      output_dict["bic"] = err("bic")

    # XXX representatives - bad call
    output_dict["representative_list"] = context.Base_getTemplateProxyParameter(parameter="representative", source_data=organisation.getUid())
    result_list.append(output_dict)
  return result_list

# XXX "ERP5 Software" => erp5, this is by no means generic and should not be here
def getSubstringFromProduct(my_candidate, my_as_is):
  software_match_string = " Software"
  software_title = my_candidate.get("title") or ""
  if software_title.find(software_match_string) > 1:
    if my_as_is == True:
      return software_title.split(software_match_string)[0]
    return software_title.split(software_match_string)[0].lower()

def callSelf(my_parameter, my_source_id, my_flag_site):
  return context.Base_getTemplateProxyParameter(
    parameter=my_parameter,
    source_uid=my_source_id,
    flag_site=my_flag_site
  )

pass_parameter = kw.get("parameter", None)
pass_source_data = kw.get("source_data", None) or context.getUid()
pass_flag_site = kw.get("flag_site", None)

if pass_parameter is not None and pass_source_data is not None:

  # ---------------------- Representative --------------------------------------
  # returns [{person_dict}, {person_dict}] - used in press release
  if pass_parameter == "representative":
    # XXX very arbitrary and hard-coded
    try:
      function_category = portal_object.portal_categories.function.company.executive
      return populatePersonDict(portal_object.portal_catalog(
        portal_type="Person",
        strict_subordination_uid=pass_source_data,
        strict_function_uid=function_category.getUid()
      ))
    except AttributeError:
      pass
    return []
  # ---------------------- Override Person -------------------------------------
  # returns [{person_dict}]
  if pass_parameter == "override_person":
    return populatePersonDict(portal_object.portal_catalog(
      portal_type="Person",
      title=pass_source_data
    ))

  # -------------------------- Contributor -------------------------------------
  # returns [{person_dict}, {person_dict...}]
  if pass_parameter == "author" and getattr(context, 'getContributorValueList', None):
    if portal_type != "Web Section" and portal_type != "Web Site":
      return populatePersonDict(context.getContributorValueList(*args, **kw))
    return []

  # ------------- Override Sender/Recipient Organisation -----------------------
  # returns [{organisation_dict}]
  if pass_parameter == "override_organisation":
    return populateOrganisationDict(portal_object.portal_catalog(
      portal_type="Organisation",
      title=(''.join(["=", str(pass_source_data)]))
    ))

  # ----------------------- Sender (Override) ----------------------------------
  # returns [{organisation_dict}]
  if pass_parameter == "sender":
    return populateOrganisationDict(portal_object.portal_catalog(
      portal_type="Organisation",
      uid=pass_source_data
    ))

  # -------------- Source/Destination (Person => Organisation) -----------------
  # returns [{organisation_dict}]
  if pass_parameter == "source" or pass_parameter == "destination":
    person_candidate_list = portal_object.person_module.searchFolder(uid=pass_source_data)
    organisation_candidate_list = portal_object.organisation_module.searchFolder(uid=pass_source_data)

    if len(person_candidate_list) > 0:
      for c in person_candidate_list:
        organisation = c.getCareerSubordinationValue()
        if organisation is not None:
          return populateOrganisationDict([organisation])
        else:
          return populatePersonDict([c])

    # events might pass organisation as sender/recipient
    if len(organisation_candidate_list) > 0:
      organisation_candidate_list = portal_object.organisation_module.searchFolder(uid=pass_source_data)
      for o in organisation_candidate_list:
        return populateOrganisationDict([o])

    return []

  # -------------------- Organisation (Follow-Up) ------------------------------
  # returns [{organisation_dict}, {organisation_dict}, ...] used in leaflet, letter, relrase
  if pass_parameter == "organisation" and getattr(context, 'getFollowUpValueList', None):
    if portal_type != "Web Site" and portal_type != "Web Section":
      return populateOrganisationDict(context.getFollowUpValueList(
        portal_type=pass_parameter.title(),
        checked_permission='View',
        follow_up_related_uid=pass_source_data
      ))
    return []

  # ---------------------- Person (Follow-Up) ----------------------------------
  # returns [{person_dict} used in letter
  if pass_parameter == "person":
    return populatePersonDict(context.getFollowUpValueList(
      portal_type=pass_parameter.title(),
      checked_permission='View'
    ))

  # --------------------- Bank (Default Bank Account) --------------------------
  # returns [{bank_account_dict}] used in letter
  if pass_parameter == "bank":
    return populateBankDict(portal_object.portal_catalog(
      portal_type="Bank Account",
      uid=pass_source_data
    ))

  # ------------------ Theme Logo (Prefix + Theme) -----------------------------
  # returns [{logo_dict}] used in themes
  if pass_parameter == "logo":
    return populateImageDict(portal_object.portal_catalog(
      portal_type="Image",
      validation_state=validation_state,
      reference=pass_source_data
    ))

  # ------------------------- Product (Website) --------------------------------
  if pass_parameter == "product":
    if pass_flag_site == True:
      return populateProductDictFromCategoryList(
        context.getWebSiteValue().getMembershipCriterionCategoryList() or []
      ) or []
    elif pass_source_data is not None:
      if getattr(context, 'getFollowUpValueList', None):
        return populateProductDict(context.getFollowUpValueList(
          portal_type=pass_parameter.title(),
          checked_permission='View',
          follow_up_related_uid=pass_source_data
        )) or []
      return []

  # --------------------------- Theme (Website) --------------------------------
  # XXX custom?
  if pass_parameter == "theme":
    theme = None
    if portal_type == "Web Site" or portal_type == "Web Section":
      pass_flag_site = True
    product_candidate_list = callSelf("product", pass_source_data, pass_flag_site)

    if product_candidate_list is not None:
      if len(product_candidate_list) > 0:
        theme = getSubstringFromProduct(product_candidate_list[0], None)

    return theme
