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
# format de fichier attendu :
# Organigramme, Role, Metier, Fonction, Raison sociale, Adresse, CodePostal, Ville
# Ville, Pays, Code Ean, Code TVA, Code compta, Tél, Fax, email

request  = context.REQUEST
file_line_list = import_file.readlines()
organisation_module = context.getPortalObject().organisation
compteur = 0

for file_line in file_line_list :
  sub_line_list = file_line.split('\r')
  for sub_line in sub_line_list :
   if sub_line != '':
  
    # create a new item
    line_item_list = sub_line.split('\t')

    # génération Id
    my_id = str(organisation_module.generateNewId())

    # recup categorie Organigramme
    if len(line_item_list) > 0 :
      my_organigramme = line_item_list[0]
    else :
      my_organigramme = None

    # recup catégorie Role
    if len(line_item_list) > 1 :
      my_role = line_item_list[1]
    else :
      my_role = None

    # recup categorie Métier
    if len(line_item_list) > 2 :
      my_metier = line_item_list[2]
    else :
      my_metier = None

    # recup categorie Fonction
    if len(line_item_list) > 3 :
      my_fonction = line_item_list[3]
    else :
      my_fonction = None

    # recup raison sociale
    if len(line_item_list) > 4 :
      my_name = line_item_list[4]
    else :
      my_name = None

    # recup Adresse
    if len(line_item_list) > 5 :
      my_street1 = line_item_list[5]
    else :
      my_street1 = None
    if len(line_item_list) > 6 :
      my_street2 = line_item_list[6]
    else :
      my_street2 = None
    if len(line_item_list) > 7 :
      my_street3 = line_item_list[7]
    else :
      my_street3 = None

    # recup Code Postal
    if len(line_item_list) > 8 :
      my_cp = line_item_list[8]
    else :
      my_cp = None

    # recup Ville
    if len(line_item_list) > 9 :
      my_city = line_item_list[9]
    else :
      my_city = None

    # recup catégorie Pays
    if len(line_item_list) > 10 :
      if line_item_list[10] == "France" :
        my_country = "Europe/Nord/France"
      else :
        my_country = None
    else :
      my_country = None

    # recup Code EAN
    if len(line_item_list) > 11 :
      my_ean_code = line_item_list[11]
    else :
      my_ean_code = None

    # recup Code TVA
    if len(line_item_list) > 12 :
      my_tva_code = line_item_list[12]
    else :
      my_tva_code = None

    # recup Code comptable
    if len(line_item_list) > 13 :
      my_compta_code = line_item_list[13]
    else :
      my_compta_code = None

    # recup Téléphone
    if len(line_item_list) > 14 :
      my_tel = line_item_list[14]
    else :
      my_tel = None

    # recup Fax
    if len(line_item_list) > 15 :
      my_fax = line_item_list[15]
    else :
      my_fax = None

    # recup Email
    if len(line_item_list) > 16 :
      my_email = line_item_list[16]
    else :
      my_email = None

    my_address = ''
    if my_street1 != '' :
      my_address += my_street1
    if my_street2 != '' :
      my_address += '\n'+my_street2
    if my_street3 != '' :
      my_address += '\n'+my_street3

    # print my_id,my_name,my_address,my_tel,my_fax,my_email,my_role,my_organigramme,my_fonction,my_metier,my_country,my_city,my_cp,my_name,my_ean_code,my_tva_code,my_compta_code
    # print len(line_item_list), len(file_line_list)

    context.portal_types.constructContent(type_name = 'Organisation',
        container = organisation_module,
        id = my_id,
        title = my_name,
        default_address_street_address = my_address,
        default_telephone_text = my_tel,
        default_fax_text = my_fax,
        default_email_text = my_email,
        role = my_role,
        group = my_organigramme,
        function = my_fonction,
        activity = my_metier,
        default_address_region = my_country,
        default_address_city = my_city,
        default_address_zip_code = my_cp,
        corporate_name = my_name,
        ean13_code = my_ean_code,
        eu_vat_code = my_tva_code,
        code_comptable = my_compta_code)
    compteur += 1
    organisation_module[my_id].flushActivity(invoke=1)

# return printed

redirect_url = '%s?%s' % ( organisation_module.absolute_url()
                              , 'portal_status_message=%s+organisations+créées.' % compteur
                              )

request[ 'RESPONSE' ].redirect( redirect_url )
