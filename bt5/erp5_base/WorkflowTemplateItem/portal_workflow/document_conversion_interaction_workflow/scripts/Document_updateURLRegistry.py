document = state_change['object']
portal = document.getPortalObject()
portal_url_registry = portal.portal_url_registry
portal_url_registry.registerURL(document.asNormalisedURL(), document.getReference(), context=document)
