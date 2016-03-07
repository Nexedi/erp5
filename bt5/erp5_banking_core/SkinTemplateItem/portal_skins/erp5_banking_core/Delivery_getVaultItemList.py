# vault_type = None : Définit les vaut_types à afficher,
#                     si valeur est None on récupère vault_type
#                     depuis les sites auxquels est assigné l'user
# exclude_vault_type = None : Définit les vaut_types à exclure,
#                             on veut par exemple les encaisses du Caveau, sauf celles du Tri tiers
# current_url = None : Permet de réinjecter la valeur courante dans le popup et évite ainsi l'affichage de '???',
#                      on mettra par exemple "current_url=here.getSource()" en paramètre du
#                      Delivery_getVaultItemList utilisé dans le TALES de my_source dans le formulaire
# user_site = 1 : Permet de sélectionner uniquement les encaisses des sites auquels l'user est affecté,
#                 au lieu des encaisses de tous le sites
# exclude_user_site = 0 : Permet de ne pas s�lectionner les encaisses du site auquel appartient l'utilisateur
# owner_site = 1 :  Permet de sélectionner uniquement les encaisses des sites auquels le propriétaire du document est affecté,
#                 au lieu des encaisses de tous le sites
# main_agency = 0 :  Permet de sélectionner uniquement les encaisses des sites qui appartiennent � une agence principale,
# leaf_node = 1 : Sélectionne uniquement les noeuds qui sont des feuilles de l'arbre (qui n'ont pas de sous-catégories)
# strict_membership = 0 : Appartenance stricte. Si vault_type='site', on sélectionnera 'site/agence/principale/paris',
#                         mais pas 'site/agence/principale/paris/caveau', 'site/agence/principale/paris/surface' et
#                         leurs encaisses. Attention : possibilité de conflit (et donc de popup menu vide) si
#                         utilisé en même temps que leaf_node
# with_base = 1 : Définie si on renvoie la base categorie 'site' dans la liste de valeur
# all = 0 : Affiche aussi entrante/sortante, utile pour les inventaires
# user_vault = 0 : Display only subvaults that corresponds to the user assigned vault
# first_level = 0 : Ne prend que le premier niveau pour un vault type, meme si les sous categories
#                   ont le meme vault_type
# disable_user_site_for_manager = 0 : permet de desactiver l'option user_site pour les utilisateurs manager

from Products.ERP5Type.Cache import CachingMethod

def getVaultItemList(vault_type=None, exclude_vault_type=None,
    user_site=1, leaf_node=1, strict_membership=0, assignment=None,
    site_list=None, with_base=1, all=0, first_level=0,main_agency=0,
    exclude_site_list=None,mode_test=0):

  if vault_type is None:
    organisation_list = []
# XXX FOR NOW, LET'S USE SITE UNTIL THE LINK BETWEEN ORGANISATIONS AND SITE HAS BEEN SORTED OUT XXX
#   organisation = assignment.getDestinationValue().getMapping()
    organisation = assignment.getSiteValue()
    if organisation is not None:
      organisation_list.append(organisation)

    vault_type_dict = {}
    for organisation in organisation_list:
      vault_type_list = organisation.getVaultTypeList()
      for vault in vault_type_list:
        vault_type_dict['vault_type/' + vault] = 1
    vault_type = vault_type_dict.keys()

  if same_type(vault_type, ''):
    vault_type = [vault_type]
  if same_type(exclude_vault_type, None):
    exclude_vault_type = []
  elif same_type(exclude_vault_type, ''):
    exclude_vault_type = [exclude_vault_type]

  new_vault_type = []
  for v in vault_type:
    if v.startswith('vault_type/'):
      new_vault_type.append(v)
    else:
      new_vault_type.append('vault_type/' + v)
  vault_type = new_vault_type
  new_exclude_vault_type = []
  for v in exclude_vault_type:
    if v.startswith('vault_type/'):
      new_exclude_vault_type.append(v)
    else:
      new_exclude_vault_type.append('vault_type/' + v)
  exclude_vault_type = new_exclude_vault_type
  vault_dict = {}
  is_member_of = context.portal_categories.isMemberOf
  get_cat_value = context.portal_categories.getCategoryValue
  for site in site_list:
    site_object = get_cat_value(site, base_category='site')

    vault_type_value_list = [context.portal_categories.restrictedTraverse('vault_type/%s' % x) for x in vault_type]
    vault_type_uid_list = [x.getUid() for x in vault_type_value_list]
    catalog_kw = {}
    if strict_membership:
      catalog_kw['strict_vault_type_uid']=vault_type_uid_list
    else:
      catalog_kw['vault_type_uid']=vault_type_uid_list
    site_member_list = context.portal_catalog(portal_type='Category',
                             relative_url='%s%%' % site_object.getRelativeUrl(),
                             limit=None,
                             **catalog_kw
                             )
    for site_member in site_member_list:
      site_member_object = site_member.getObject()
      site_member_relative_url = site_member_object.getRelativeUrl()
      if exclude_site_list is not None:
        if site_member_relative_url in exclude_site_list:
          continue
      if main_agency:
        if site_member_relative_url.find('principale')<0:
          continue
      for exclude_vault_type_item in exclude_vault_type:
        if is_member_of(site_member_object, exclude_vault_type_item, strict=0) :
          break
      else:
        parent_value = site_member_object.getParentValue()
        if first_level == 1 and getattr(parent_value, 'getVaultType', None) is not None \
            and parent_value.getVaultType()==site_member_object.getVaultType():
          pass
        elif leaf_node == 1:
          if len(site_member_object) == 0 or site_member_relative_url.endswith("auxiliaire/encaisse_des_externes"):
            site_member_logical_path = site_member_object.getLogicalPath()
            vault_dict[site_member_relative_url] = [site_member_logical_path,site_member_relative_url]
        else:
          site_member_logical_path = site_member_object.getLogicalPath()
          vault_dict[site_member_relative_url] = [site_member_logical_path,site_member_relative_url]


  vault_list = vault_dict.values()

  # Sort the vault list by path
  vault_list.sort(lambda x, y: cmp(x[1], y[1]))
  vault_dict = {}
  # Transform each line of the vault list
  keep_level = []
  for vault_item in vault_list:
    # do not include testsite if not in test mode
    if mode_test == 0 and 'testsite' in vault_item[1]:
      continue
    title_path_list = vault_item[0].split('/')
    id_path_list    = vault_item[1].split('/')[1:] # exclude the base category
    path_len      = len(id_path_list)
    # remove some uneeded part in path
    if not all and ('Entrante' in title_path_list[-1] or "Sortante" in title_path_list[-1]):
      title_path_list = title_path_list[:-1]
      id_path_list = id_path_list[:-1]
      path_len = path_len - 1

    new_title_list = context.Base_calculateBeautifulSiteLogicalPath(title_path_list,path_len=path_len)

    new_id = '/'.join(new_title_list)
    if with_base:
      item_value = '/'.join(['site'] + id_path_list[:])
    else:
      item_value = '/'.join(id_path_list[:])
    item = (new_id, item_value)
    vault_dict[new_id] = item_value

  vault_list = vault_dict.items()
  vault_list.sort()
  return vault_list

getVaultItemList = CachingMethod(getVaultItemList, id=('Delivery_getVaultItemList', 'getVaultItemList'), 
                                 cache_factory='erp5_ui_long')


if vault_type is None:
  assignment = context.Baobab_getUserAssignment()
else:
  assignment = None

erp5_site = context.getPortalObject()
mode_test = 0
if hasattr(erp5_site, 'functionnal_test_mode'):
  if getattr(erp5_site,  'functionnal_test_mode') == 1:
    mode_test = 1

if disable_user_site_for_manager:
  from AccessControl import getSecurityManager
  u=getSecurityManager().getUser()
  if 'Manager' in u.getRoles():
    user_site=0

user_site_list = []
if user_site == 1 or owner_site==1:
  if owner_site:
    user_site_list = context.Baobab_getUserAssignedSiteList(user_id=context.owner_info()['id'])
  elif user_site:
    user_site_list = context.Baobab_getUserAssignedSiteList()
  # even if we are on a counter, we can see every thing in the same agency
  new_site_list = []
  for site in user_site_list:
    if "guichet" in  site:
      site = context.Baobab_getVaultSite(vault=site)
      new_site_list.append(site.getRelativeUrl())
    else:
      new_site_list.append(site)
  site_list = new_site_list
else:
  if base_site is not None:
    site_list = [base_site,]
  else:
    site_list = ['site']

exclude_site_list = None
if exclude_user_site:
  if len(user_site_list)==0:
    user_site_list = context.Baobab_getUserAssignedSiteList()
  new_list = []
  for user_site in user_site_list:
    root_site_url = context.Baobab_getVaultSite(vault=user_site).getRelativeUrl()
    if root_site_url not in new_list:
      new_list.append(root_site_url)
  exclude_site_list = new_list

vault_list = getVaultItemList(vault_type=vault_type, exclude_vault_type=exclude_vault_type,
  user_site=user_site, leaf_node=leaf_node, strict_membership=strict_membership,
  assignment=assignment, site_list=site_list, with_base=with_base, all=all,
  first_level=first_level,main_agency=main_agency,exclude_site_list=exclude_site_list,
  mode_test=mode_test)

if user_vault == 1:
  if len(user_site_list)==0:
    user_site_list = context.Baobab_getUserAssignedSiteList()
  user_site = user_site_list[0]
  if user_site.find('guichet')>=0:
    new_vault_list = [x for x in vault_list if x[1].startswith(user_site)]
    vault_list = new_vault_list

if current_url != None :
  if 'site' not in current_url:
    current_category_relative_url = 'site/'+current_url
    if with_base:
      current_url = current_category_relative_url
  else:
    current_category_relative_url = current_url
  current_category = context.portal_categories.getCategoryValue(current_category_relative_url)
  if current_category is not None :
    if current_url not in [x[1] for x in vault_list] :
      # Get the logical path of the current category
      logical_path_list = current_category.getLogicalPath().split('/')
      title = '/'.join(context.Base_calculateBeautifulSiteLogicalPath(logical_path_list,path_len=len(logical_path_list)))
      return [('', ''), (title, current_url)] + list(vault_list)
  else :
    return [('', ''), (context.Localizer.erp5_ui.gettext('Unknown Vault')+' : %s' % current_url, current_url)] + list(vault_list)
return [('', '')] + list(vault_list)
