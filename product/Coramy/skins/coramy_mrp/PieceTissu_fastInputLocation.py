## Script (Python) "PieceTissu_fastInputLocation"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id_and_location_list=[]
##title=
##
# updates location property for all given items
from Products.Formulator.Errors import ValidationError, FormValidationError

request = context.REQUEST
compteur = 0

try :

  item_nb = int(len(id_and_location_list)/2)
  for i in range(item_nb) :
    item_result_list = context.portal_catalog(id = str(int(id_and_location_list[i*2])), portal_type="Piece Tissu")
    try :
      item = item_result_list[0].getObject()
      location = id_and_location_list[i*2+1]
    except :
      item = None
      location = None

    if item is not None and location is not None :
      item.setLocation(location)
      item.flushActivity(invoke=1)
      compteur += 1

except FormValidationError, validation_errors:
  redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=La+saisie+a+échoué.'
                                  )
else:
  redirect_url = '%s/view?%s' % ( context.absolute_url()
                                  , 'portal_status_message=%s+emplacements+mis+à+jour.' % compteur
                                  )

request[ 'RESPONSE' ].redirect( redirect_url )
