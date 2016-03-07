# this script is used to display a small text in the main form corresponding to the composition
# it return something like "3.0 % Polyamide, 5.0 % Elasthanne"
translateString = context.Base_translateString

title_list = []
cell_list = []
poly_list = context.ApparelFabric_asCellRange(matrixbox=1)[0]
for cat, title in poly_list:
  cell = context.getCell(cat, base_id='composition')
  if cell is not None:
    cell_list.append({'quantity':cell.getQuantity(), 'title':translateString(catalog='content', msg=title)})

# sort by quantity
cell_list.sort(key=lambda x: x['quantity'], reverse=True)

for cell in cell_list:
    quantity = cell['quantity']
    text = '%s %% %s' % (quantity*100, cell['title'])
    title_list.append(text)
final_text = ', '.join(title_list)
return final_text
