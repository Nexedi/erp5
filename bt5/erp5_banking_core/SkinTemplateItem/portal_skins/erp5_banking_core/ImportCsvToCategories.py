def lowerCase(s):
  return s.replace(' ', '_').lower()

def upperCase(s):
  s = ' '.join([x.capitalize() for x in lowerCase(s).split('_') if len(x) > 0])
  s = '/'.join([x[0].upper() + x[1:] for x in s.split('/') if len(x) > 0])
  item_list = s.split(' ')
  if len(item_list) > 1:
    new_list = []
    for item in item_list :
      if item in ('A', 'Chez', 'De', 'Des', 'En', 'Et', 'La', 'Par', 'Pour') :
        item = item.lower()
      new_list.append(item)
    item_list = new_list
  return ' '.join(item_list)

def l_clean(line) :
  if line.endswith('\n') :
    line = line[:-1]
  return line

def l_split(line) :
  e_list = line.split(',')
  new_e_list = []
  for e in e_list :
    if len(e) > 0 :
      if e[0] == '"' and e[-1] == '"' :
        e = e[1:-1]
      new_e_list.append(e)
  return new_e_list

def create_category(cat, vault_type=None) :
  cat_list = lowerCase(cat).split('/')
  cat_len = len(cat_list)

  if cat_len == 1 :
    # base_category
    base_cat = [x.getObject() for x in context.portal_categories.searchFolder(id=lowerCase(cat_list[0]))]
    if not len(base_cat):
      return context.portal_categories.newContent(portal_type = 'Base Category',
                                                  id = lowerCase(cat_list[0]),
                                                  title = upperCase(cat_list[0]))
    else:
      return base_cat[0]

  elif cat_len > 1 :
    # sub_category
    relative_category = context.portal_categories.getCategoryValue(lowerCase('/'.join(cat_list[:-1])))

    if relative_category is None :
      relative_category = create_category(lowerCase('/'.join(cat_list[:-1])))
      if vault_type is not None:
        relative_category.setVaultType(vault_type)

    cat = relative_category.get(lowerCase(cat_list[-1]))
    if cat is not None :
      return cat
    else :
      new_cat = relative_category.newContent(portal_type = 'Category',
                                            id = lowerCase(cat_list[-1]),
                                            title = upperCase(cat_list[-1]))
      if vault_type is not None:
        new_cat.setVaultType(vault_type)
      return new_cat

def generate_vault_dict() :
  c_list = context.portal_categories.vault_type.getCategoryChildValueList()
  # function to sort category by title
  def sortCategory(a, b):
    return cmp(a.getRelativeUrl(), b.getRelativeUrl())
  vault_dict = {}
  c_list.sort(sortCategory)
  for c in c_list:
    code = c.getProperty('codification')
    if code is not None and not vault_dict.has_key(code):
      vault_dict[code]=c.getRelativeUrl()
  return vault_dict

##########################################
request  = context.REQUEST

import_type = getattr(request,'my_import_type',None) or getattr(request,'field_my_import_type',None)
line_list = import_file.readlines()

line_list = [l_clean(line) for line in line_list]
line_list = [l_split(line) for line in line_list]

#return '\n'.join([l for l in line_list])


if import_type == 'create_category' :
  if context.portal_categories.get(lowerCase(line_list[0][0])) :
    context.portal_categories.deleteContent(lowerCase(line_list[0][0]))
  for e_list in line_list :
    if len(e_list) > 0 :
      e = e_list[0]
      #try :
      print 'trying to create %s ...' % lowerCase(e),
      create_category(e)
      print 'done'
#       except AttributeError:
#         print 'Failed'
#         return printed


elif import_type == 'assign_codification' :
  for e_list in line_list :
    if len(e_list) == 2 :
      try :
        print 'trying to assign to %s ...' % lowerCase(e_list[0]) ,
        context.log('lowerCase(e_list[0])',lowerCase(e_list[0]))
        category = context.portal_categories.getCategoryValue(lowerCase(e_list[0]))
        category.setCodification(e_list[1])
        # Automatically assign code for some subcategories
        #context.log('e_list[0]',e_list[0])
        if e_list[0].startswith('site'):
          acquired_vault_code = {'banque_interne':'BI','operations_diverses':'OD','gros_paiement':'GP','gros_versement':'GV',
                        'guichet_1':'G1','guichet_2':'G2','guichet_3':'G3'}
          context.log('category',category.getPath())
          for sub_cat in category.getCategoryChildValueList(sort_id='path'):
            print "    %s" % sub_cat.getRelativeUrl()
            if sub_cat.getId() in acquired_vault_code.keys():
              parent_code = sub_cat.getParentValue().getCodification()
              code = parent_code + acquired_vault_code[sub_cat.getId()]
              sub_cat.setCodification(code)
        print 'done %s' % repr(e_list)
      except KeyError:
        print 'Failed'
        return printed


elif import_type == 'assign_vault_type' :
  vault_type_dict = generate_vault_dict()
  context.log('vault_type_dict', vault_type_dict)
  vault_type_list = vault_type_dict.keys()
  for e_list in line_list :
    if len(e_list) == 2 and e_list[1] in vault_type_list :
      category = context.portal_categories.getCategoryValue(lowerCase(e_list[0]))
      category.setCategoryList([vault_type_dict[e_list[1]]])
      print 'set %s to %s for e_list %s' % ([vault_type_dict[e_list[1]]], category, e_list)


elif import_type == 'create_subvaults' :
#Encaisse des Billets Restitues par Tiers a Detruire# seulemnt sur sites disposant de tri tiers
#Encaisse des Billets Recus pour Ventilation# seulement sur sites principaux
  subvault_dict = {}
  for e_list in line_list :
    #context.log('e_list', e_list)
    if len(e_list) in (2,3) :
      vault = lowerCase(e_list[0]) # ex : Vault_Type/Site/caveau/Auxiliaire
      subvault = upperCase(e_list[1]) # ex : Encaisse des Devises
      subvault_code=None
      if len(e_list)==3:
        subvault_code = e_list[2] # ex : D
      counter_string_list = [] # the list of counters, like ['guichet_1,entrant',...]
      #one_way_counter_list = ('gros_paiement','gros_versement')
      one_way_counter_list = ()
      two_way_counter_list = ('banque_interne','operations_diverses','gros_paiement','gros_versement')
      counter_list = one_way_counter_list + two_way_counter_list
      max_counter = 3 # we may not have always the same number of counters
      counter_name = vault.split('/')[-1]
      # add as many counters as required
      if counter_name in counter_list:
        if counter_name in one_way_counter_list:
          max_counter=2
        for i in range(1,max_counter+1):
#           if counter_name in two_way_counter_list:
#             counter_string_list.append('guichet_%s/entrante' % i)
#             counter_string_list.append('guichet_%s/sortante' % i)
#           else:
          counter_string_list.append('guichet_%s' % i)
      else:
        counter_string_list = ['']

      #context.log('counter_string_list',counter_string_list)
      if not subvault_dict.has_key(vault) :
        subvault_dict[vault] = []
      for counter_string in counter_string_list:
        #context.log('counter_string', counter_string)
        if counter_string != '':
          counter_subvault = '%s/%s' % (counter_string,subvault)
        else:
           counter_subvault = subvault
        #context.log('counter_subvault', counter_subvault)
        subvault_dict[vault].append([counter_subvault, subvault_code])
        if subvault == 'Encaisse des Billets et Monnaies' :
          if counter_name in two_way_counter_list:
            if counter_name != 'gros_paiement':
              subvault_dict[vault].append(['%s/%s' % (counter_subvault, "entrante"), None])
            if counter_name != 'gros_versement':
              subvault_dict[vault].append(['%s/%s' % (counter_subvault, "sortante"), None])
        elif subvault == 'Encaisse des Externes' :
          subvault_dict[vault].append(['%s/%s' % (counter_subvault, "transit"), 'TRA'])
        elif subvault == 'Encaisse des Devises' :
          for c in context.currency_module.objectValues() :
            if c.getId() != context.Baobab_getPortalReferenceCurrencyID():
              if counter_name in two_way_counter_list:
                #context.log('add encaisse des billets et monnaies E/S',counter_subvault)
                # Do not create "entrante" vault for currency subvaults, we only use sortante
                #subvault_dict[vault].append(['%s/%s/%s' % (counter_subvault, c.getTitle(), "entrante"), None])
                subvault_dict[vault].append(['%s/%s/%s' % (counter_subvault, c.getTitle(), "sortante"), None])
              else:
                #context.log('add encaisse des billets et monnaies',counter_subvault)
                subvault_dict[vault].append(['%s/%s' % (counter_subvault, c.getTitle()), None])
        elif subvault in ('Encaisse des Billets Recus pour Ventilation Venant de','Encaisse des Billets en Transit Allant a',
                        'Encaisse des Billets Neufs Non Emis en Transit Allant a') :
          for c in context.portal_categories.site.agence.principale.objectIds() :
            if counter_name in two_way_counter_list:
              #context.log('add ventilation E/S', counter_subvault)
              subvault_dict[vault].append(['%s/%s/%s' % (counter_subvault, upperCase(c), "entrante"), None])
              subvault_dict[vault].append(['%s/%s/%s' % (counter_subvault, upperCase(c), "sortante"), None])
            else:
              #context.log('add ventilation', counter_subvault)
              subvault_dict[vault].append(['%s/%s' % (counter_subvault, upperCase(c)), None])

  # subvault_dict looks like this :
  #subvault_dict : {'vault_type/site/surface/operations_diverses': [['Encaisse des Devises', 'D'], ['Encaisse des Devises/Francs Suisses', None],
  #                          ['Encaisse des Billets et Monnaies', 'A']]}



  vault_type_list = subvault_dict.keys()
  context.log("vault_type_list", vault_type_list)
  context.log("vault_type_dict :",subvault_dict)

  # parse the for site category tree and add sub categories if required
  #for c in context.portal_categories.site.getCategoryChildValueList() :
  #for c in context.portal_categories.site.agence.principale.lome.getCategoryChildValueList() :
  #for c in context.portal_categories.site.getCategoryChildValueList() :
  #for c in context.portal_categories.site.agence.principale.cotonou.getCategoryChildValueList() :
  #for c in context.portal_categories.site.getCategoryChildValueList() :
  #for c in context.portal_categories.site.agence.principale.abidjan.getCategoryChildValueList() :
  #for c in context.portal_categories.site.agence.principale.bissau.getCategoryChildValueList() :
  for c in context.portal_categories.site.getCategoryChildValueList() :
    context.log('c.getPath()',c.getPath())
    for vault_type in vault_type_list :
      context.log("c = %s, vault_type = %s" %(c, vault_type), "c.getvaultType = %s" %(c.getVaultType()))
      if context.portal_categories.isMemberOf(c, vault_type, strict=1) :
        print c.getRelativeUrl(), 'is', vault_type
        context.log("subvault_data",subvault_dict[vault_type])
        for subvault_data in subvault_dict[vault_type] :
          subvault_path = subvault_data[0]
          subvault_code = subvault_data[1]
          if 'Encaisse des Billets Recus pour Ventilation Venant de' in subvault_path or 'Encaisse des Billets Restitues par Tiers a Detruire' in subvault_path \
                or 'Encaisse des Billets en Transit Allant a' in subvault_path or 'Encaisse des Billets Neufs Non Emis en Transit Allant a' in subvault_path:
            if not context.portal_categories.isMemberOf(c, 'site/agence/principale', strict=0) :
              print 'XXXXXXXX is not principale, not creating', subvault_path
              pass
            elif subvault_path.find('/') > 0 and lowerCase(subvault_path).split('/')[1] in c.getRelativeUrl() :
              print 'XXXXXXXX is itself, not creating', subvault_path
              pass
            else :
              print '  creating (case1) ', subvault_path
              if 'guichet' in subvault_path:
                subcat_vault_type = '%s/guichet' %('/'.join(vault_type.split('/')[1:]),)
              elif 'transit' in subvault_path.lower():
                subcat_vault_type = '%s/transit' %('/'.join(vault_type.split('/')[1:]),)
              else:
                subcat_vault_type = '/'.join(vault_type.split('/')[1:])
              new_category_obj = create_category(cat = '%s/%s' % (c.getRelativeUrl(), subvault_path), vault_type = subcat_vault_type)
          else :
            print '  creating (case2)', subvault_path
            if 'guichet' in subvault_path:
              subcat_vault_type = '%s/guichet' %('/'.join(vault_type.split('/')[1:]),)
            elif 'retire' in subvault_path.lower():
              subcat_vault_type = '%s/retire' %('/'.join(vault_type.split('/')[1:]),)
            elif subvault_path.lower().endswith('externes'):
              subcat_vault_type = '%s/encaisse_des_externes' %('/'.join(vault_type.split('/')[1:]),)
            elif subvault_path.lower().endswith('transit'):
              subcat_vault_type = '%s/encaisse_des_externes/transit' %('/'.join(vault_type.split('/')[1:]),)
            elif 'devises' in subvault_path.lower():
              subcat_vault_type = '%s/encaisse_des_devises' %('/'.join(vault_type.split('/')[1:]),)
            elif 'differences' in subvault_path.lower():
              subcat_vault_type = '%s/encaisse_des_differences' %('/'.join(vault_type.split('/')[1:]),)
            elif 'mutiles' in subvault_path.lower():
              subcat_vault_type = '%s/billets_mutiles' %('/'.join(vault_type.split('/')[1:]),)
            elif 'macules' in subvault_path.lower():
              subcat_vault_type = '%s/billets_macules' %('/'.join(vault_type.split('/')[1:]),)
            else:
              subcat_vault_type = '/'.join(vault_type.split('/')[1:])
            new_category_obj = create_category(cat = '%s/%s' % (c.getRelativeUrl(), subvault_path), vault_type = subcat_vault_type)
          # set codification
          if subvault_code not in (None, ''):
            new_category_obj.setCodification(subvault_code)

        print
        break
    else : print c.getRelativeUrl(), 'not here'







print 'ok'
return printed
