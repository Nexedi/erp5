## Script (Python) "grille_consommation_update"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=reference_taille, form_id
##title=
##
items = context.getTailleList()
request = context.REQUEST

# This is a bug fix related to an issue in Base
# which does not update attributes if the value is unchanged

default_quantity = {}
for j in items:
  cell = context.newCell(reference_taille, j, base_id='quantity')
  try:
    default_quantity[j] = cell.quantity
  except:
    redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Error+Missing+Data.'
                              )
    return request[ 'RESPONSE' ].redirect( redirect_url )

reference_quantity = default_quantity[reference_taille]

if reference_quantity is None or reference_quantity == 0:
    redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Error+Zero+Value.'
                              )
    return request[ 'RESPONSE' ].redirect( redirect_url )

for i in items:
  for j in items:
    cell = context.newCell(i, j, base_id='quantity')
    if default_quantity[j] is not None:
      try:
        cell.edit(quantity = default_quantity[j] / default_quantity[i] )
      except:
        pass

redirect_url = '%s/%s?%s' % ( context.absolute_url()
                              , form_id
                              , 'portal_status_message=Grille+Consommation+Updated.'
                              )
return request[ 'RESPONSE' ].redirect( redirect_url )
