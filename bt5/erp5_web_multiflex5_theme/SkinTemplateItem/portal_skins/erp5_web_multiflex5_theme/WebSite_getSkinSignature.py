"""
  This scripts must be created for every site. It is used
  to test that nobody changes the order of skin selection.
  Zabbix must call this script on a web site to make sure
  that nothing wrong happens.
"""
skin_constraint = []
required_skin_folder_id_list = ['erp5_web_multiflex5_theme',
                                'erp5_xhtml_style',
                                'erp5_web']
# No method available to retrieve selected skin (it will be needed some day)
default_skin = context.getSkinSelectionName()

skin_selection = context.portal_skins.getSkinPath(default_skin).split(',')

# Add here a line each an order error happens
skin_constraint.append(skin_selection.index('erp5_web_multiflex5_theme') < \
                         skin_selection.index('erp5_web'))
skin_constraint.append(skin_selection.index('erp5_web_multiflex5_theme') < \
                         skin_selection.index('erp5_xhtml_style'))

for required_skin_folder_id in required_skin_folder_id_list:
  skin_constraint.append(required_skin_folder_id in skin_selection)

# make sure no cache server in front will cache script
context.REQUEST.RESPONSE.setHeader('Cache-Control', 'no-cache')

# Return signature
return "%s %s" % (default_skin, not False in skin_constraint)
