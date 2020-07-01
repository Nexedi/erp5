from erp5.component.module.Log import log
log('DepracationWarning: Please use ContributionTool_getPropertyDictFromFilename')
return context.ContributionTool_getPropertyDictFromFilename(file_name, property_dict)
