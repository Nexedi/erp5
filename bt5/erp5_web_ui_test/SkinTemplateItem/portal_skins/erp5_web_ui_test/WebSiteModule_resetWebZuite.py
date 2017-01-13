# Reset everything for the test.
portal = context.getPortalObject()

# Clean up the contents.
if portal.web_site_module.has_key('test_web_site'):
  portal.web_site_module.manage_delObjects('test_web_site')

if portal.web_site_module.has_key('web_site_test'):
  portal.web_site_module.manage_delObjects('web_site_test')

if portal.web_site_module.has_key('test_web_site_2'):
  portal.web_site_module.manage_delObjects('test_web_site_2')

if portal.web_site_module.has_key('test_web_site'):
  portal.web_site_module.manage_delObjects('test_web_site')

if portal.person_module.has_key('test_website_predicate'):
  portal.person_module.manage_delObjects('test_website_predicate')

portal.web_page_module.manage_delObjects(
  [x.getId() for x in portal.web_page_module.objectValues() \
   if x.getTitle().startswith('test_')])

# Create new users
if not portal.person_module.has_key('test_webmaster'):
  person = portal.person_module.newContent(id='test_webmaster', portal_type='Person')
else:
  person = portal.person_module.test_webmaster
person.edit(first_name='Test', last_name='Webmaster',
            reference='test_webmaster')
person.setRole('internal')
if not len(person.objectValues(portal_type='Assignment')):
  assignment = person.newContent(portal_type='Assignment')
  assignment.edit(group='web',
                  start_date=DateTime('2000/01/01'),
                  stop_date=DateTime('2990/12/31'))
  if assignment.getValidationState() != 'open':
    assignment.open()
if not len(person.objectValues(portal_type='ERP5 Login')):
  login = person.newContent(
    portal_type='ERP5 Login',
    reference='test_webmaster',
    password='test_webmaster',
  )
  login.validate()
if person.getValidationState() != 'validated':
  person.validate()

# Create region category
if not portal.portal_categories.region.has_key('test_web_region'):
  portal.portal_categories.region.newContent(id='test_web_region', portal_type='Category', title='test_web_region')
return 'Reset Successfully.'
