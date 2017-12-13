"""
================================================================================
Create a source dict for filling templates
================================================================================
"""
blank = ''
from Products.PythonScripts.standard import html_quote

# --------------------------  External parameters ------------------------------

# eg "Nexedi" specific parameters
customHandler = getattr(context, "WebPage_getCustomParameter", None)

# parameters common to all templates
commonHandler = getattr(context, "WebPage_getCommonParameter", None)
commonProxyHandler = getattr(context, "WebPage_getCommonProxyParameter", None)

def getCustomParameter(my_parameter, my_override_data):
  if customHandler is not None:
    source_data = my_override_data or context.getUid()
    return customHandler(parameter=my_parameter, source_data=source_data)

def getCommonParameter(my_parameter, my_override_data):
  if commonHandler is not None:
    source_data = my_override_data or context.getUid()
    return commonHandler(parameter=my_parameter, source_data=source_data)

def getCommonProxyParameter(my_parameter, my_override_data):
  if commonProxyHandler is not None:
    source_data = my_override_data or context.getUid()
    return commonProxyHandler(parameter=my_parameter, source_data=source_data)

# -------------------------------  Set Source ----------------------------------
source_logo_url = None
if source is None:
  contributor_title_string = blank
  source_person = None
  source_person_list = []
  source_organisation = None
  source_organisation_list = []
  source_organisation_uid = None
  source_set = None

  # source person
  if override_source_person_title is not None or override_source_person_title is blank:
    source_person_list = getCommonProxyParameter("override_person", override_source_person_title)
  if len(source_person_list) == 0:
    source_person_list = getCommonProxyParameter("author", None) or []
  if len(source_person_list) > 0:
    source_person = source_person_list[0]
    contributor_title_string = ', '.join(x.get("name", blank) for x in source_person_list)

  # source organisation
  if override_source_organisation_title is not None or override_source_organisation_title is blank:
    source_organisation_list = getCommonProxyParameter("override_organisation", override_source_organisation_title)
  if len(source_organisation_list) == 0:
    source_organisation_uid = getCustomParameter("source_organisation_uid", None)
  if source_organisation_uid:
    source_organisation_list = getCommonProxyParameter("sender", source_organisation_uid) or []
  if len(source_organisation_list) == 0 and default_company_title:
    source_organisation_list = getCommonProxyParameter("override_organisation", default_company_title) or []
  if len(source_organisation_list) == 0 and source_person is not None:
    for organisation_candidate in source_person_list:
      organisation_candidate_list = getCommonProxyParameter("source", organisation_candidate.get("uid")) or []
      if len(organisation_candidate_list) > 0:
        source_organisation_list = organisation_candidate_list
        break
    #source_organisation_list = getCommonProxyParameter("source", source_person.get("uid")) or []
  if len(source_organisation_list) > 0:
    source_organisation = source_organisation_list[0]

  source = {}
  source.update(source_person or {})
  source.update(source_organisation or {})
  source["contributor_title_string"] = contributor_title_string

# source => event
else:
  source_uid =context.restrictedTraverse(source).getUid()
  source = getCommonProxyParameter("source", source_uid)[0]

# override specific bank account (no default to pick correct one if multiple exist)
if default_bank_account_uid is not None:
  override_bank_account_list = getCommonProxyParameter("bank", default_bank_account_uid) or []
  if len(override_bank_account_list) > 0:
    override_bank_account = override_bank_account_list[0]
    source["bank"] = override_bank_account.get("bank")
    source["bic"] = override_bank_account.get("bic")
    source["iban"] = override_bank_account.get("iban")

# XXX images stored on organisation (as do images in skin folders)
if override_logo_reference:
  source_logo_url = html_quote(override_logo_reference) + "?format=png&display=small"
  source_set = True
if source_logo_url is None:
  source_logo_url = source.get("logo_url", blank)
if source_logo_url is not blank and source_set is None:
  source_logo_url = source_logo_url + "?format=png"
if source_logo_url is blank and theme_logo_url is not None:
  source_logo_url = theme_logo_url
source["enhanced_logo_url"] = source_logo_url

return source
