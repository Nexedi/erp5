## Script (Python) "SalesPackingList_exportEdi"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=batch_mode=0,**kw
##title=
##
# export d un fichier Edi
# format de fichier attendu
# Traduction .rec du fichier Edifact par NY Net

from string import rjust, zfill
import string
from DateTime import DateTime

def chaine(num, width):
    s = str(int(num))
    if len(s) > width:
        result = s[-width:]
    else:
        result = zfill(s,width)
    return result

def decoupe(s,width):
    if len(s) > width:
        result_tmp = s[-width:]
    else:
        result_tmp = rjust(s,width)
    return result_tmp

request=context.REQUEST

retour_chariot = "\r\n"

result = ""
num_article = 0
total_qty = 0
csp_sequence_expe = 1



result += "START:AVISAUCHAVISAUCH"+retour_chariot
result += "UNH_DEBUT_MESSAGE____:DESADVEAN005"+retour_chariot

code_fonction = '9'
result += "BGM_AVIS_EXPEDITION__:"+decoupe(context.getId() , 8)+code_fonction+retour_chariot 
result += "DTM_DATE_DOCUMENT____:"+DateTime().strftime("%Y%m%d%H%M")+retour_chariot

sales_order = context.getCausalityValue(portal_type=['Sales Order'])

result += "DTM_DATE_LIVR_DEMANDE:"+sales_order.getTargetStopDate().strftime("%Y%m%d%H%M")+retour_chariot

result += "DTM_DATE_HEURE_EXPE__:"+context.getTargetStartDate().strftime("%Y%m%d%H%M")+retour_chariot

try:
  result += "RFF_NUMERO_COMMANDE__:"+ sales_order.getDestinationReference() +retour_chariot
except:
  if not batch_mode:
    message="Erreur+sur+la+facture:+il+n\'y+a+pas+de+numéro+de+commande+sur+la+commande"
    redirect_url = '%s?%s%s' % ( context.absolute_url()+'/view', 'portal_status_message=',message)
    request[ 'RESPONSE' ].redirect( redirect_url )
    return None
  else:
    return None

try:
  result += "RFF_DATE_COMMANDE____:"+ sales_order.getDateReception().strftime("%Y%m%d") +retour_chariot
except:
  if not batch_mode:
    message="Erreur+sur+la+facture:+il+n\'y+a+pas+de+date+de+réception+sur+la+commande"
    redirect_url = '%s?%s%s' % ( context.absolute_url()+'/view', 'portal_status_message=',message)
    request[ 'RESPONSE' ].redirect( redirect_url )
    return None
  else:
    return None


# XXX
result += "RFF_BON_LIVRAISON____:"+ context.getId() +retour_chariot
result += "RFF_DATE_____________:"+ context.getTargetStopDate().strftime("%Y%m%d%H%M") +retour_chariot


source_section = sales_order.getSourceSectionTitle()
list = sales_order.portal_catalog(Title=source_section, portal_type = 'Organisation')


if len(list) > 0:
  source =  list[0].getObject()
  ean_source = source.getEan13Code()
  result += "NAD_EXPEDITEUR_______:"+ ean_source + retour_chariot


ean_destination = sales_order.getDestinationDecisionValue(portal_type=['Organisation']).getEan13Code()

if ean_destination in (None,''):
  if not batch_mode:
    message="Erreur+sur+la+facture:+il+n\'y+a+pas+de+code+ean+sur+l\'organisation:+commandé+par."
    redirect_url = '%s?%s%s' % ( context.absolute_url()+'/view', 'portal_status_message=',message)
    request[ 'RESPONSE' ].redirect( redirect_url )
    return None
  else:
    return None

result += "NAD_EMETTEUR_CDE_____:"+ ean_destination + retour_chariot
result += "NAD_INTER_A_LIVRER___:"+ ean_destination + retour_chariot
result += "NAD_DEST_MESSAGE_____:"+ ean_destination + retour_chariot


result += "TOD_CONDITION_LIVR___:"+"SD"+retour_chariot
result += "TDT_DETAIL_TRANSPORT_:"+"3031"+retour_chariot


# { ean13code:  send_quantity , ...}
send_quantity_dict = {}
packing_list_movement_list = context.getMovementList()
for movement in packing_list_movement_list:
  send_quantity_dict[ movement.Amount_getCodeEan13Client() ] = int(movement.getTargetQuantity())

# [ (ean13code, difference) ]
difference_quantity_list = []
sales_order_movement_list = sales_order.getMovementList()


for movement in sales_order_movement_list: 
  desired_quantity = int(movement.getTargetQuantity() ) 
  eanCode = movement.Amount_getCodeEan13Client()
  try:
    send_quantity = send_quantity_dict[ eanCode ] 
    difference_quantity =  (desired_quantity - send_quantity)  

    if difference_quantity <> 0:
      difference_quantity_list.append( ( eanCode , difference_quantity ) ) 
    if send_quantity == 0:
      del send_quantity_dict[ eanCode ]
  except KeyError:
    None 

if send_quantity_dict <> {}:
  num_ct = 1
else:
  num_ct = 0
pac_emballage = chaine( num_ct , 8 ) + "CT" 

weight = context.PackingList_getTotalGrossWeight()

result += "CSP_SEQUENCE_EXPE____:"+ decoupe( "%i"%csp_sequence_expe,12) +retour_chariot
result += "PAC_EMBALLAGE________:"+ pac_emballage + retour_chariot
result += "MEA_MESURES_POIDS_TOT:"+ str(weight) +retour_chariot

if difference_quantity_list <> []:
  for difference_quantity in difference_quantity_list:
    result += "LIN_ARTICLE__________:"+difference_quantity[0]+retour_chariot
    result += "QVR_EXPED_PARTIELLE__:"+"%i"%(difference_quantity[1])+retour_chariot 


if send_quantity_dict <> {}:

  result += "CSP_SEQUENCE_EXPE____:"+decoupe( "%i"% (csp_sequence_expe+1),12) + "%i"%csp_sequence_expe +retour_chariot
  csp_sequence_expe += 1
  result += "PAC_EMBALLAGE________:"+pac_emballage +retour_chariot
  result += "QTY_QUANTITE_KGM_____:"+ str(weight) + retour_chariot

  for ean_key in send_quantity_dict.keys():
    num_article += 1
    result += "LIN_ARTICLE__________:" + decoupe( "%i" % num_article , 5 ) + ean_key + retour_chariot
    result += "QTY_QTE_EXPEDIEE_UC__:" + "%i"%(send_quantity_dict[ ean_key ]) + retour_chariot

  result += "CNT_CONTROLE_TOTAL___:%i"% num_article+retour_chariot 

if batch_mode:
  return result
else:
  request.RESPONSE.setHeader('Content-Type','application/text')
  return result
