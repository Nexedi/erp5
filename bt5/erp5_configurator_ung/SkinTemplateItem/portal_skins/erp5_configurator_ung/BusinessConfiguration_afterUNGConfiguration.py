""" This script will be called to apply the customization. """
from AccessControl import getSecurityManager

portal = context.getPortalObject()
portal_preferences = portal.portal_preferences
business_template = context.getSpecialiseValue()
isTransitionPossible = portal.portal_workflow.isTransitionPossible

# enable ung preference
ung_preference = getattr(portal.portal_preferences, 'ung_preference', None)
if ung_preference is not None and isTransitionPossible(ung_preference, 'enable'):
  ung_preference.enable()

# publish the ung web site
ung_web_site = getattr(portal.web_site_module, 'ung', None)
if ung_web_site is not None and isTransitionPossible(ung_web_site, 'publish', None):
    ung_web_site.publish()

language = context.getGlobalConfigurationAttr("default_available_language")

ung_web_site.setDefaultAvailableLanguage(language)
for web_section in ung_web_site.contentValues(portal_types='Web Section'):
  if isTransitionPossible(web_section, 'publish', None):
    web_section.publish()

bt5 = portal.portal_catalog.getResultValue(portal_type="Business Template",
                                           title="erp5_web_ung_role")

if bt5 is not None:
  for portal_type in bt5.getTemplatePortalTypeRoleList():
    module_list = portal.contentValues(filter=dict(portal_type=portal_type))
    portal_type_object = portal.portal_catalog.getResultValue(portal_type="Base Type",
                                                              id=portal_type)
    portal_type_object.updateRoleMapping()
    context.log("Updated Role Mappings for: %s " % (portal_type_object.getId()))
    for module in module_list:
      module.updateLocalRolesOnSecurityGroups()
      context.log("Updated Role Mappings for: %s(%s) " % (module.getTitle(), module.getPortalType()))

if business_template is not None:
  # update path items. FIXME: local roles should be exported by business template instead
  for path in business_template.getTemplatePathList():
    obj = portal.restrictedTraverse(path, None)
    # no need to update security on categories
    if obj is not None and obj.getPortalType() not in ('Category', 'Base Category',):
      obj.updateLocalRolesOnSecurityGroups()
      context.log("Updated Role Mappings for: ", path, obj.getPortalType())

  # validate and open all objects
  for path in business_template.getTemplatePathList():
    obj = context.getPortalObject().restrictedTraverse(path, None)
    if obj is not None and hasattr(obj, 'getPortalType'):
      # XXX This hardcoded list is a bit inconvinient.
      if obj.getPortalType() in ('Person', 
                                 'Organisation'):
        if isTransitionPossible(obj, 'validate'):
          obj.validate()
          context.log("Validated: ", obj.getRelativeUrl())

        for assignment in obj.contentValues(filter={'portal_type':'Assignment'}):
          if isTransitionPossible(assignment, 'open'):
            assignment.open()
            assignment.updateLocalRolesOnSecurityGroups()
            context.log("\tOpen (assignment): ", assignment.getRelativeUrl())

for gadget in context.portal_gadgets.objectValues():
  if gadget.getValidationState() == 'invisible':
    gadget.visible()
    gadget.public()

# XXX - check if is possible add this configuration in bt5
portal.knowledge_pad_module.manage_permission('Add portal content',
                                              roles=['Assignor', "Manager", "Authenticated", "Author"],
                                              acquire=0)
context.log("Indexing translations")
portal.ERP5Site_updateTranslationTable()

# clear cache so user security is recalculated
portal.portal_caches.clearAllCache()
context.log("Clear cache.")
