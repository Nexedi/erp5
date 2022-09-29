if clean:
  context.Zuite_tearDownSaleTradeConditionTest()

portal = context.getPortalObject()
howto_dict = context.Zuite_getHowToInfo()
isTransitionPossible = portal.portal_workflow.isTransitionPossible

# check if there is already the euro curency on the instance
currency = context.portal_catalog.getResultValue(portal_type='Currency',
                                                 title=howto_dict['sale_howto_currency_title'])

if currency is None:
  currency = portal.currency_module.newContent(portal_type='Currency',
                                               title=howto_dict['sale_howto_currency_title'],
                                               reference=howto_dict['sale_howto_currency_tag'],
                                               id=howto_dict['sale_howto_currency_tag'],
                                               base_unit_quantity=0.01)

if isTransitionPossible(currency, 'validate'):
  currency.validate()

my_organisation = portal.organisation_module.newContent(portal_type='Organisation',
                                                        title=howto_dict['sale_howto_organisation_title'],
                                                        corporate_name=howto_dict['sale_howto_organisation_title'])
my_organisation.setRole('supplier')
my_organisation.setGroup('my_group')
my_organisation.validate()

organisation = portal.organisation_module.newContent(portal_type='Organisation',
                                                     title=howto_dict['sale_howto_organisation2_title'],
                                                     corporate_name=howto_dict['sale_howto_organisation2_title'])
organisation.validate()

person = portal.person_module.newContent(portal_type='Person',
                                         title=howto_dict['sale_howto_person_title'],
                                         career_subordination_title=howto_dict['sale_howto_organisation_title'])
person.validate()

pref = getattr(context.portal_preferences, howto_dict['howto_preference_id'], None)
if pref is None:
  pref = context.portal_preferences.newContent(portal_type="Preference",
                                               id=howto_dict['howto_preference_id'])
  pref.setPreferredAccountingTransactionSectionCategory('group/my_group')
if isTransitionPossible(pref, 'enable'):
  pref.enable()

pref.setPreferredAccountingTransactionSourceSection(my_organisation.getRelativeUrl())

# Disabling save form warning
# this is bad but needed quickly to disable save form warning
pref.setPreferredHtmlStyleUnsavedFormWarning(False)

# Clear cache
portal.portal_caches.clearAllCache()

return "Init Ok"
