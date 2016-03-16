from Products.ERP5Type.Log import log
log('DepracationWarning: Please use ContributionTool_getPropertyDictFromFilename')
return context.ContributionTool_getPropertyDictFromFilename(file_name, property_dict)
