"""Collect all possible (sub contained) Ram Cache Plugins.
   This collection will be used in respective report form."""
from Products.ERP5Form.Report import ReportSection

result = []
for ram_cache_plugin in context.getPortalObject().portal_catalog(
                                             portal_type = 'Ram Cache',
                                             path ='%' + context.getRelativeUrl() +'%'):
  result.append(ReportSection(path = ram_cache_plugin.getRelativeUrl(),
                              form_id = 'RamCache_viewStatisticList',
                              title = '%s/%s' %(ram_cache_plugin.getParentValue().getTitle(),
                                                ram_cache_plugin.getTitle()),))
return result
