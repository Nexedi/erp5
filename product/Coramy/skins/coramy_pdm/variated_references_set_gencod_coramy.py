## Script (Python) "variated_references_set_gencod_coramy"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form_id=''
##title=
##
request = context.REQUEST

# mise à jour du range de la matrice

line = map((lambda x:x[0]),context.variated_reference_matrix_item_list(base_category_list = ('coloris','variante'), base=1))
column = map((lambda x:x[0]),context.variated_reference_matrix_item_list(base_category_list = ('taille',), base=1))
tab = map((lambda x:x[0]),context.variated_reference_matrix_item_list(base_category_list = ('taille','coloris','variante'), base=1, include=0))

if line <> [None] :
  if column <> [None] :
    if tab <> [None] :
      context.setCellRange(line,column,tab,base_id="cell")
    else :
      context.setCellRange(line,column,base_id="cell")
  else :
    if tab <> [None] :
      context.setCellRange(line,tab,base_id="cell")
    else :
      context.setCellRange(line,base_id="cell")
elif column <> [None] :
  if tab <> [None] :
    context.setCellRange(column,tab,base_id="cell")
  else :
    context.setCellRange(column,base_id="cell")
elif tab <> [None] :
  context.setCellRange(tab,base_id="cell")

# boucle sur les cellules de matrice pour les remplir
cell_keys = context.getCellKeys(base_id="cell")
for keys_item in cell_keys :
  cancel = 0
  if len(keys_item) == 3 :
    cell = context.newCell(keys_item[0],keys_item[1],keys_item[2], base_id='cell')
  elif len(keys_item) == 2 :
    cell = context.newCell(keys_item[0],keys_item[1], base_id='cell')
  elif len(keys_item) == 1 :
    cell = context.newCell(keys_item[0], base_id='cell')
  else :
    cancel = 1

  if cancel == 0:
    cell.edit(mapped_value_property_list = 'code_ean13',
              domain_base_category_list = context.getVariationBaseCategoryList(),
              predicate_operator = 'SUPERSET_OF',
              predicate_value_list = keys_item)
    societe = context.portal_categories.group.Coramy
    country = societe.country
    CNUF = societe.CNUF
    CIP = societe.CIP
    cell.edit(code_ean13 = context.new_ean13_code(country,CNUF,CIP))
    societe.edit(CIP = CIP+1)

redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Gencods+mis+a+jour.'
                              )

request[ 'RESPONSE' ].redirect( redirect_url )
