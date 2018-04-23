"""
================================================================================
Create a source dict for filling templates
================================================================================
"""
# parameters:
# ------------------------------------------------------------------------------
# source:                                  Can be set if called from Event
# override_logo_reference                  Logo to use instead of organisation logo
# override_source_person_title:            Title of person to use
# override_source_organisation_title:      Title of organisation to use
# theme_logo_url                           Theme logo url to use if no logo found

blank = ''
from Products.PythonScripts.standard import html_quote

# -------------------------------  Set Source ----------------------------------
source_logo_url = None
default_bank_account_uid=context.Base_getTemplateParameter("default_bank_account_uid")
source_organisation = None

if source is None:
  default_company_title=context.Base_getTemplateParameter("default_company_title")
  contributor_title_string = blank
  source_person = None
  source_person_list = []
  source_organisation_list = []
  source_organisation_uid = None
  source_set = None

  # source person => override => contributor => source_decision
  if override_source_person_title is not None or override_source_person_title == blank:
    source_person_list = context.Base_getTemplateProxyParameter(parameter="override_person", source_data=override_source_person_title)
  if len(source_person_list) == 0:
    source_person_list = context.Base_getTemplateProxyParameter(parameter="author", source_data=None) or []
  if len(source_person_list) == 0 and getattr(context, 'getSourceDecisionValue', None) is not None:
    source_person_candidate = context.getSourceDecisionValue()
    if source_person_candidate and source_person_candidate.getPortalType() == "Person":
      source_person_list = [source_person_candidate]
  if len(source_person_list) > 0:
    source_person = source_person_list[0]
    contributor_title_string = ', '.join(x.get("name", blank) for x in source_person_list)

  # source organisation
  # order: override => follow-up => default_organisation_uid => default_company_title => source_person career subordinate => source decision
  if override_source_organisation_title is not None or override_source_organisation_title == blank:
    source_organisation_list = context.Base_getTemplateProxyParameter(parameter="override_organisation", source_data=override_source_organisation_title)
  if len(source_organisation_list) == 0:
    source_organisation_list = context.Base_getTemplateProxyParameter(parameter="organisation", source_data=None) or []
  if len(source_organisation_list) == 0:
    source_organisation_uid = context.Base_getTemplateParameter("default_source_organisation_uid")
  if source_organisation_uid:
    source_organisation_list = context.Base_getTemplateProxyParameter(parameter="sender", source_data=source_organisation_uid) or []
  if len(source_organisation_list) == 0 and default_company_title:
    source_organisation_list = context.Base_getTemplateProxyParameter(parameter="override_organisation", source_data=default_company_title) or []
  if len(source_organisation_list) == 0 and source_person is not None:
    for organisation_candidate in source_person_list:
      organisation_candidate_list = context.Base_getTemplateProxyParameter(parameter="source", source_data=organisation_candidate.get("uid")) or []
      if len(organisation_candidate_list) > 0:
        source_organisation_list = organisation_candidate_list
        break
  if len(source_organisation_list) == 0 and getattr(context, 'getSourceDecisionValue', None) is not None:
    source_organisation_candidate = context.getSourceDecisionValue()
    if source_organisation_candidate and source_organisation_candidate.getPortalType() == "Organisation":
      source_organisation_list = [source_organisation_candidate]
  if len(source_organisation_list) > 0:
    source_organisation = source_organisation_list[0]

  source = {}
  source.update(source_person or {})
  source.update(source_organisation or {})
  source["contributor_title_string"] = contributor_title_string

# source => event
else:
  source_uid = context.restrictedTraverse(source).getUid()
  source = context.Base_getTemplateProxyParameter(parameter="source", source_data=source_uid)[0]

# override specific bank account (no default to pick correct one if multiple exist)
if default_bank_account_uid is not None:
  override_bank_account_list = context.Base_getTemplateProxyParameter(parameter="bank", source_data=default_bank_account_uid) or []
  if len(override_bank_account_list) > 0:
    override_bank_account = override_bank_account_list[0]
    source["bank"] = override_bank_account.get("bank")
    source["bic"] = override_bank_account.get("bic")
    source["iban"] = override_bank_account.get("iban")

# social media
if source_organisation is not None:
  source["social_media_handle_facebook"] = context.Base_getTemplateParameter('social_media_handle_facebook')
  source["social_media_handle_twitter"] = context.Base_getTemplateParameter('social_media_handle_twitter')
  source["social_media_handle_google"] = context.Base_getTemplateParameter('social_media_handle_google')

# social capital currency and registered court fallbacks
if source.get("social_capital_currency") is blank:
  source["social_capital_currency"] = context.Base_getTemplateParameter("default_source_company_capital_currency")
if source.get("corporate_registration_code") is blank:
  source["corporate_registration_code"] = context.Base_getTemplateParameter("default_source_registered_court")

# XXX images stored on organisation (as do images in skin folders)
if override_logo_reference:
  source_logo_url = html_quote(override_logo_reference) + "?format=png"
  source_set = True
if source_logo_url is None:
  source_logo_url = source.get("logo_url", blank)
if source_logo_url != blank and source_set is None:
  # XXX: test environment fails if url with parameters are supplied
  source_logo_url = source_logo_url + "?format=png"
if source_logo_url == blank and theme_logo_url is not None:
  source_logo_url = theme_logo_url
source["enhanced_logo_url"] = source_logo_url

return source
