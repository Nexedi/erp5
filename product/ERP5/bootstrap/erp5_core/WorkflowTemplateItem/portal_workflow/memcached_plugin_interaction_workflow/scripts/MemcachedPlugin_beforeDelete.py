document = state_change['object']
cache_plugin_list = document.getSpecialiseRelatedValueList(portal_type='Distributed Ram Cache')
from Products.CMFCore.utils import getToolByName
if cache_plugin_list:
  cache_tool = getToolByName(document.getPortalObject(), 'portal_caches')
  if cache_tool is not None:
    cache_tool.activate().updateCache()

selection_tool = document.getPortalObject().portal_selections
if selection_tool.getStorage() == document.getRelativeUrl():
  selection_tool.activate().clearCachedContainer()
if selection_tool.getAnonymousStorage() == document.getRelativeUrl():
  selection_tool.activate().clearCachedContainer(is_anonymous=True)
