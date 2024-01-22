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
from base64 import b64encode
portal_type_valid_template_list = ["Web Site", "Web Section", "Web Page", "Letter", "Test Page"]
portal_type_valid_report_list = ["Project", "Sale Order", "Sale Opportunity", "Requirement Document", "Person"]
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
    result_list.append({
      "title": product.getTitle() or err("product software")
    })
  return result_list

def populateImageDict(my_image_list):
  result_list = []
  for image in my_image_list:
    result_list.append({
      "relative_url": image.getRelativeUrl(),
      "reference": image.getReference() or err("reference"),
      "description": image.getDescription() or err("description")
    })
  return result_list

def populateBankDict(my_bank_list):
  result_list = []
  for bank in my_bank_list:
    result_list.append({
      "bank": bank.getTitle() or err("bank account title"),
      "iban": bank.getIban() or err("iban"),
      "bic":  bank.getBicCode() or err("bic")
    })
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
    if person_address:
      output_dict["address"] = person_address.getStreetAddress() or err("street address")
      output_dict["postal_code"] = person_address.getZipCode() or err("postal code")
      output_dict["city"] = person_address.getCity() or err("city")
    else:
      output_dict["address"] = err("street_adress")
      output_dict["postal_code"] = err("postal_code")
      output_dict["city"] = err("city")
    if person_region:
      output_dict["country"] = person_region.getTitle() or err("country")
      output_dict["codification"] = person_region.getCodification() or err("country code")
    else:
      output_dict["country"] = err("country")
      output_dict["codification"] = err("country code")
    if person_default_telephone:
      output_dict["phone"] = person_default_telephone.getCoordinateText() or err("phone")
    else:
      output_dict["phone"] = err("phone")
    if person_default_mail:
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
    organisation_link_list = [x for x in organisation.objectValues(portal_type="Link") if x.getTitle()=="Corporate Web Site"]
    organisation_bank_list = [x for x in organisation.objectValues(portal_type="Bank Account") if x.getValidationState()=='validated' and x.getTitle()=="Default Bank Account"]
    organisation_default_image = organisation.getDefaultImage()

    output_dict["organisation_title"] = organisation.getTitle()
    output_dict["corporate_name"] = organisation.getCorporateName() or err("corporate name")
    output_dict["description"] = organisation.getDescription() or err("description")
    output_dict["social_capital"] = organisation.getSocialCapital() or err("social capital")
    output_dict["activity_code"] = organisation.getActivityCode() or err("activitiy code")

    #output_dict["logo_url"] = organisation.getDefaultImageAbsoluteUrl() or err("logo_url")
    if organisation_default_image:
      output_dict["logo_url"] = organisation_default_image.getRelativeUrl()
      output_dict["logo_data_url"] = 'data:image/png;;base64,%s' % (
        b64encode(organisation_default_image.convert(format="png", display="thumbnail")[1]).decode()
      )
    else:
      output_dict["logo_url"] = err("logo_url")

    # XXX we should have social_capital_currency and corporate_registration_court
    output_dict["social_capital_currency"] = err("social capital")
    output_dict["corporate_registration_code"] = err("corporate_registration_code")

    output_dict["vat"] = organisation.getVatCode() or err("vat")
    output_dict["corporate_registration"] = organisation.getCorporateRegistrationCode() or err("corporate_registration")
    output_dict["email"] = organisation.getDefaultEmailText() or err("email")
    if organisation_address:
      output_dict["address"] = organisation_address.getStreetAddress() or err("street address")
      output_dict["postal_code"] = organisation_address.getZipCode() or err("postal code")
      output_dict["city"] = organisation_address.getCity() or err("city")
    else:
      output_dict["address"] = err("street address")
      output_dict["postal_code"] = err("postal code")
      output_dict["city"] = err("city")
    if organisation_region:
      output_dict["country"] = organisation_region.getTitle() or err("country")
      output_dict["codification"] = organisation_region.getCodification() or err("country code")
    else:
      output_dict["country"] = err("country")
      output_dict["codification"] = err("country code")
    if organisation_phone:
      output_dict["phone"] = organisation_phone.getCoordinateText() or err("phone")
    else:
      output_dict["phone"] = err("phone")
    if organisation_fax:
      output_dict["fax"] = organisation_fax.getCoordinateText() or err("fax")
    else:
      output_dict["fax"] = err("fax")
    if len(organisation_link_list) == 1:
      #XXXX only 1 ?
      output_dict["website"] = organisation_link_list[0].getUrlString() or err("Website")
    else:
      output_dict["website"] = err("web site")
    if organisation_bank_list:
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
    person_list = portal_object.portal_catalog(
      portal_type="Person",
      title=pass_source_data
    )
    person_list = [x for x in person_list if x.getTitle() == pass_source_data]
    return populatePersonDict(person_list)

  # -------------------------- Contributor -------------------------------------
  # returns [{person_dict}, {person_dict...}]
  if pass_parameter == "author" and getattr(context, 'getContributorValueList', None):
    if portal_type != "Web Section" and portal_type != "Web Site":
      return populatePersonDict(context.getContributorValueList(*args, **kw))
    return []

  # --------- Override Sender/Recipient Organisation (TITLE) ---------------------
  # XXX remove, too much ambiguity if multiple results
  # returns [{organisation_dict}]
  if pass_parameter == "override_organisation":
    organisation_list = portal_object.portal_catalog(
      portal_type="Organisation",
      title = '="%s"' % pass_source_data,
    )
    return populateOrganisationDict(organisation_list)

  # ------------ Override Sender/Recipient Organisation (URL) --------------------
  # returns [{organisation_dict}]
  if pass_parameter == "override_organisation_relative_url":
    return populateOrganisationDict([context.restrictedTraverse(pass_source_data)])

  # -------------- Source/Destination (Person => Organisation) -----------------
  # returns [{organisation_dict}]
  if pass_parameter == "source" or pass_parameter == "destination":
    candidate = portal_object.portal_catalog.getResultValue(
      portal_type=('Person', 'Organisation'),
      uid=pass_source_data)

    if candidate:
      if candidate.getPortalType() == 'Person':
        organisation = candidate.getCareerSubordinationValue()
        if organisation is not None:
          return populateOrganisationDict([organisation])
        else:
          return populatePersonDict([candidate])
      # events might pass organisation as sender/recipient
      return populateOrganisationDict([candidate])

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
    return populateBankDict([context.restrictedTraverse(pass_source_data)])

  # ------------------ Theme Logo (Prefix + Theme) -----------------------------
  # returns [{logo_dict}] used in themes, needs to be language-agnostic, but not
  # all contexts (eg sale-order) have language
  # XXX improve
  if pass_parameter == "logo":

    try:
      use_language = context.getLanguage() or "en"
    except AttributeError:
      use_language = "en"
    logo_list = portal_object.portal_catalog(
      portal_type="Image",
      language=use_language,
      validation_state=validation_state,
      reference=pass_source_data
    )
    if not logo_list and use_language != "en":
      logo_list = portal_object.portal_catalog(
        portal_type="Image",
        language="en",
        validation_state=validation_state,
        reference=pass_source_data
      )
    return populateImageDict(logo_list)

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
    tmp = context
    #check if web page is inside web site or web section
    while portal_type in ('Web Page', 'Test Page'):
      tmp = tmp.aq_parent
      portal_type = tmp.getPortalType()

    if portal_type == "Web Site" or portal_type == "Web Section":
      pass_flag_site = True
    product_candidate_list = callSelf("product", pass_source_data, pass_flag_site)

    if product_candidate_list is not None:
      if len(product_candidate_list) > 0:
        theme = getSubstringFromProduct(product_candidate_list[0], None)

    return theme
