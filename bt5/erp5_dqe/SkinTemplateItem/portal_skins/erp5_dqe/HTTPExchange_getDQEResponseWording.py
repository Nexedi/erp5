resource_value = context.getResourceValue()
if not resource_value.isMemberOf('http_exchange_resource/dqe'):
  return {}
response_dict = context.HTTPExchange_getDQEResponseDict()

dqe_resource_category = context.getPortalObject().portal_categories.http_exchange_resource.dqe

# In addresses DQE sends 'DQELibErreur' and we use that
# in other cases we use hard-coded mapping that is in fr
# it is for Data Warehouse use and Investigation tab
if resource_value in (
  dqe_resource_category.DefaultAddress, dqe_resource_category.DeliveryAddress
):
  return response_dict.get('DQELibErreur', 'Inconnue').encode('utf-8')
elif resource_value == dqe_resource_category.DefaultEmail:
  return {
    '00': 'E-mail valide',
    '01': 'E-mail correct, mais le nom n’a pas pu être contrôlé',
    '02': 'Adresse e-mail non trouvée pour ce domaine',
    '03': 'Boîte pleine (Soft Bounce)',
    '04': 'E-mail vide',
    '91': 'Erreur de syntaxe',
    '92': 'Domaine inconnu',
    '93': 'Domaine blacklisté',
    '94': 'Nom d’utilisateur non autorisé (nom réservé ou insulte)',
    '95': 'Adresse e-mail temporaire jetable',
    '99': 'Service non disponible (timeout)',
  }.get(
    response_dict.get('IdError'), 'Inconnue'
  )
elif resource_value in (
  dqe_resource_category.DefaultTelephone, dqe_resource_category.MobileTelephone,
):
  return {
    0: 'Numéro de téléphone incorrect ',
    1: 'La ligne est construite, avec confirmation que la ligne a été utilisée récemment',
    2: 'La ligne est construite mais sans confirmation que la ligne est bien utilisée',
  }.get(
    response_dict.get('IdError'), 'Inconnue'
  )
elif resource_value == dqe_resource_category.OrganisationData:
  return {
    'FOUND': 'Organisation trouvée ',
    'NOT FOUND': 'Organisation introuvable',
  }.get(
    response_dict.get('DQE_status', 'NOT FOUND'), 'Inconnue'
  )
elif resource_value == dqe_resource_category.RelocationData:
  if response_dict.get('RESULT', 'FALSE') == 'TRUE':
    return 'Déménagée'
  return 'Non déménagée'
return ''
