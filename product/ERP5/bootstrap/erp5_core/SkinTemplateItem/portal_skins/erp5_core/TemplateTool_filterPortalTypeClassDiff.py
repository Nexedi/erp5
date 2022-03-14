if len(old_line_list) !=1 or len(new_line_list) != 1:
  return False
new_line = new_line_list[0]

new_group_list = new_line.split('"')
if len(new_group_list) != 5:
  return False

before, _, module, erp5_portal_type, after = new_group_list
if before != '<global name=' or module != ' module=' or erp5_portal_type != 'erp5.portal_type' or after != '/>':
  return False

old_group_list = old_line_list[0].split('"')
if len(old_group_list) == 5:
  before2, _, module2, products_erp5type, after2 = old_group_list
  return before2 == before and module2 == module and products_erp5type.startswith("Products.ERP5Type.Document.") and after2 == after
return False
