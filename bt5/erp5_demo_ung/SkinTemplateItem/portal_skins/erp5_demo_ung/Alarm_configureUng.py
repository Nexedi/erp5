"""
 Applies all the configuration necessary to have UNG working.
"""
portal = context.getPortalObject()
isTransitionPossible = portal.portal_workflow.isTransitionPossible

# enable the ung_preference
ung_preference = getattr(portal.portal_preferences, 'ung_preference', None)
if ung_preference is not None:
 if  isTransitionPossible(ung_preference, 'enable'):
   ung_preference.enable()

# publish the ung web site
ung_web_site = getattr(portal.web_site_module, 'ung', None)
if ung_web_site is not None:
  if isTransitionPossible(ung_web_site, 'publish', None):
    ung_web_site.publish()
    for web_section in ung_web_site.contentValues(portal_types='Web Section'):
      if isTransitionPossible(web_section, 'publish', None):
        web_section.publish()

# configure system preference
ung_system_preference = getattr(portal.portal_preferences, 'ung_system_preference', None)
if ung_system_preference is None:
  ung_system_preference = portal.portal_preferences.newContent(portal_type='System Preference',
                                                               id='ung_system_preference',
                                                               title='UNG System Preference')
  ung_system_preference.setPreferredOoodocServerAddress('localhost')
  ung_system_preference.setPreferredOoodocServerPortNumber('8008')
  ung_system_preference.enable()
