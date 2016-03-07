if clean:
  context.Zuite_tearDownCampaignTest()

portal = context.getPortalObject()
isTransitionPossible = portal.portal_workflow.isTransitionPossible
howto_dict = context.Zuite_getHowToInfo()

# check if there is already the euro curency on the instance
currency = context.portal_catalog.getResultValue(portal_type='Currency',
                                                 title=howto_dict['campaign_howto_currency_title'])
if currency is None:
  currency = portal.currency_module.newContent(portal_type='Currency',
                                               title=howto_dict['campaign_howto_currency_title'],
                                               reference=howto_dict['campaign_howto_currency_tag'],
                                               id=howto_dict['campaign_howto_currency_tag'],
                                               base_unit_quantity=0.01)

if isTransitionPossible(currency, 'validate'):
  currency.validate()

organisation = portal.organisation_module.newContent(portal_type='Organisation',
                                                     title=howto_dict['campaign_howto_organisation_title'],
                                                     corporate_name=howto_dict['campaign_howto_organisation_title'])
organisation.validate()

person = portal.person_module.newContent(portal_type='Person',
                                         title=howto_dict['campaign_howto_person_title'],
                                         career_subordination_title=howto_dict['campaign_howto_organisation_title'])
person.validate()

person2 = portal.person_module.newContent(portal_type='Person',
                                         title=howto_dict['campaign_howto_person2_title'],
                                         career_subordination_title=howto_dict['campaign_howto_organisation_title'])
person2.validate()

pref = getattr(portal.portal_preferences, howto_dict['howto_preference_id'], None)
if pref is None:
  pref = context.portal_preferences.newContent(portal_type="Preference",
                                               id=howto_dict['howto_preference_id'])

if isTransitionPossible(pref, 'enable'):
  pref.enable()

pref.setPreferredTextEditor('text_area')

portal.portal_caches.clearAllCache()

return "Init Ok"
