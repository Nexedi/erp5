if clean:
  context.Zuite_tearDownIncomingEventTest()

portal = context.getPortalObject()
howto_dict = context.Zuite_getHowToInfo()
isTransitionPossible = portal.portal_workflow.isTransitionPossible

# in testExpressUserDocumentationIncomingEvent we relly that loged in user is an ERP5 Person
logged_in_user = str(context.portal_membership.getAuthenticatedMember())
current_person = context.portal_catalog.getResultValue(portal_type='Person',
                                                       reference=logged_in_user)
if current_person is None:
  pass
  #return 'You need to be logged with an ERP5User for this test %s' %logged_in_user

# check if there is already the euro curency on the instance
currency = context.portal_catalog.getResultValue(portal_type='Currency',
                                                 title=howto_dict['incoming_event_howto_currency_title'])
if currency is None:
  currency = portal.currency_module.newContent(portal_type='Currency',
                                               title=howto_dict['incoming_event_howto_currency_title'],
                                               reference=howto_dict['incoming_event_howto_currency_tag'],
                                               id=howto_dict['incoming_event_howto_currency_tag'],
                                               base_unit_quantity=0.01)

if isTransitionPossible(currency, 'validate'):
  currency.validate()

organisation = portal.organisation_module.newContent(portal_type='Organisation',
                                                     title=howto_dict['incoming_event_howto_organisation_title'],
                                                     corporate_name=howto_dict['incoming_event_howto_organisation_title'],
                                                    )
organisation.validate()

person = portal.person_module.newContent(portal_type='Person',
                                         title=howto_dict['incoming_event_howto_person_title'],
                                         career_subordination_title=howto_dict['incoming_event_howto_organisation_title'],
                                         default_email_text=howto_dict['incoming_event_howto_person_email'])
person.validate()

person2 = portal.person_module.newContent(portal_type='Person',
                                          title=howto_dict['incoming_event_howto_person2_title'],
                                          career_subordination_title=howto_dict['incoming_event_howto_organisation_title'],
                                          default_email_text=howto_dict['incoming_event_howto_person2_email'])
person2.validate()

campaign = portal.campaign_module.newContent(portal_type='Campaign',
                                             title=howto_dict['incoming_event_howto_campaign_title'],
                                             reference=howto_dict['incoming_event_howto_campaign_reference'],
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

service = getattr(portal.service_module, howto_dict['incoming_event_howto_service_id'], None)
if service is None:
  service = portal.service_module.newContent(portal_type='Service',
                                             id=howto_dict['incoming_event_howto_service_id'],
                                             title=howto_dict['incoming_event_howto_service_title'])
  service.setUseValue(getattr(portal.portal_categories.use, howto_dict['incoming_event_howto_service_id']))
  service.validate()

system_preference_id = 'test_functional_system_preference'
system_preference = getattr(portal.portal_preferences, system_preference_id, None)
if system_preference is None:
  system_preference = portal.portal_preferences.newContent(portal_type='System Preference',
                                                           id=system_preference_id)

if isTransitionPossible(system_preference, 'enable'):
  system_preference.enable()

system_preference.setPreferredEventResourceList([service.getRelativeUrl()])
system_preference.setPreferredEventUseList([howto_dict['incoming_event_howto_service_id']])

pref = getattr(context.portal_preferences, howto_dict['howto_preference_id'], None)
if pref is None:
  pref = context.portal_preferences.newContent(portal_type="Preference",
                                               id=howto_dict['howto_preference_id'])

if isTransitionPossible(pref, 'enable'):
  pref.enable()

pref.setPriority(3)
pref.setPreferredTextEditor('text_area')

context.portal_caches.clearAllCache()

return "Init Ok"
