if clean:
  context.Zuite_tearDownCreateEventTest()
portal = context.getPortalObject()
isTransitionPossible = portal.portal_workflow.isTransitionPossible
howto_dict = context.Zuite_getHowToInfo()

# check if there is already the euro curency on the instance
currency = context.portal_catalog.getResultValue(portal_type='Currency',
                                                 title=howto_dict['create_event_howto_currency_title'])
if currency is None:
  currency = portal.currency_module.newContent(portal_type='Currency',
                                               title=howto_dict['create_event_howto_currency_title'],
                                               reference=howto_dict['create_event_howto_currency_tag'],
                                               id=howto_dict['create_event_howto_currency_tag'],
                                               base_unit_quantity=0.01)

if isTransitionPossible(currency, 'validate'):
  currency.validate()

organisation = portal.organisation_module.newContent(portal_type='Organisation',
                                                     title=howto_dict['create_event_howto_organisation_title'],
                                                     corporate_name=howto_dict['create_event_howto_organisation_title'])
organisation.validate()

person = portal.person_module.newContent(portal_type='Person',
                                         title=howto_dict['create_event_howto_person_title'],
                                         default_email_text=howto_dict['create_event_howto_person_email'],
                                         career_subordination_title=howto_dict['create_event_howto_organisation_title'])
person.validate()

person2 = portal.person_module.newContent(portal_type='Person',
                                          title=howto_dict['create_event_howto_person2_title'],
                                          default_email_text=howto_dict['create_event_howto_person2_email'],
                                          career_subordination_title=howto_dict['create_event_howto_organisation_title'])
person2.validate()

campaign = portal.campaign_module.newContent(portal_type='Campaign',
                                             title=howto_dict['create_event_howto_campaign_title'],
                                             reference=howto_dict['create_event_howto_campaign_reference'],
                                             resource='service_module/marketing_sales',
                                             source_section=organisation.getRelativeUrl(),
                                             source_decision=person.getRelativeUrl(),
                                             source=person2.getRelativeUrl(),
                                             destination=organisation.getRelativeUrl(),
                                             source_trade_list=[person.getRelativeUrl()],
                                             quantity_unit='time/day',
                                             start_date='2000/10/10',
                                             stop_date='3000/10/10',
                                             quantity=9,
                                             price=20,
                                             price_currency=currency.getRelativeUrl())
campaign.validate()

pref = getattr(context.portal_preferences, howto_dict['howto_preference_id'], None)
if pref is None:
  pref = context.portal_preferences.newContent(portal_type="Preference",
                                               id=howto_dict['howto_preference_id'])

if isTransitionPossible(pref, 'enable'):
  pref.enable()

pref.setPreferredTextEditor('text_area')

sys_pref = getattr(context.portal_preferences, howto_dict['howto_preference_id'], None)
if pref is None:
  sys_pref = context.portal_preferences.newContent(portal_type="System Preference",
                       preferred_event_sender_email=("test@nexedi.com",),
                       id=howto_dict['howto_sys_preference_id'])

sys_pref.setPreferredEventSenderEmail("test@nexedi.com",)
if isTransitionPossible(sys_pref, 'enable'):
  sys_pref.enable()

context.portal_caches.clearAllCache()

return "Init Ok"
