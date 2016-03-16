from Products.CMFCore.utils import getToolByName

tool = getToolByName(context, 'portal_skins')
skin_folders = tool.objectValues()

fiscal_report_list = []

for folder in skin_folders:
  folder_id = folder.id
  if folder_id.startswith('erp5_accounting_l10n_') or folder_id.startswith('custom'):
    # Assume all PDFForm in the folder are Fiscal Reports
    for object in folder.objectValues():
      if object.meta_type == 'ERP5 PDF Form':
        fiscal_report_list.append((object.title, object.getId()))

# Sort by title
fiscal_report_list.sort(lambda x,y: cmp(x[0], y[0]))

return fiscal_report_list
