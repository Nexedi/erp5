## Script (Python) "Organisation_importFile"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=import_file, **kw
##title=
##
# import des lieux fonctions depuis Cognis
# format de fichier attendu
# id, code tissu Cognis, coloris, no fournisseur, qté, laize, no bain, emplacement, commentaires

request  = context.REQUEST
file_line_list = import_file.readlines()
item_module = context.getPortalObject().organisation

for file_line in file_line_list :
  sub_line_list = file_line.split('\r')
  for sub_line in sub_line_list :
   if sub_line != '':
  
    # create a new item
    line_item_list = sub_line.split('\t')

    # recup Id
    if len(line_item_list) > 0 :
      my_id = line_item_list[0]
    else :
      my_id = str(item_module .generateNewId())

    # recup reference_fournisseur
    if len(line_item_list) > 3 :
      my_source_reference = line_item_list[3]
    else :
      my_source_reference = None

    # recup quantité
    if len(line_item_list) > 4 :
      my_quantity = float(line_item_list[4].replace(',','.'))
    else :
      my_quantity = None

    # recup laize utile
    if len(line_item_list) > 5 :
      my_laize_utile = float(line_item_list[5].replace(',','.'))
    else :
      my_laize_utile = None

    # recup no bain teinture
    if len(line_item_list) > 6 :
      my_bain_teinture = line_item_list[6]
    else :
      my_bain_teinture = None

    # recup emplacement
    if len(line_item_list) > 7 :
      my_location = line_item_list[7]
    else :
      my_location = None

    # recup commentaires
    if len(line_item_list) > 8 :
      my_comment =  'ancien code : '+line_item_list[1]+' '+line_item_list[2]+'\r'+''.join(line_item_list[7:])
    else :
      my_comment = None

#    print my_id, my_source_reference, my_quantity, my_laize_utile, my_location
    context.portal_types.constructContent(type_name = 'Piece Tissu',
        container = item_module,
        id = my_id,
        source_reference = my_source_reference,
        quantity = my_quantity,
        laize_utile = my_laize_utile,
        bain_teinture = my_bain_teinture,
        location = my_location,
        comment = my_comment )
    item_module[my_id].flushActivity(invoke=1)

#return printed

redirect_url = '%s?%s' % ( item_module.absolute_url()
                              , 'portal_status_message=%s+organisation+créées.' % len(sub_line_list)
                              )

request[ 'RESPONSE' ].redirect( redirect_url )
