## Script (Python) "Container_printExtandLabel"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Coramy.MetoAPI import selectMeter, startFormat, setDecoration, setPrintSpeed, setPaperSpeed, setPixel, setTemparature, setNumber, endFormat, printText, printLine, printFrame, setAsdFont


def chaine(num, div):
    case = {
       10 : 1,
       100 : 2,
       1000: 3,
       10000: 4,
       100000: 5,
       1000000: 6

    }       
    longueur = case[div]
    #longueur = div / 10
    tmp = str( int(num) % div)

    result = ''
    for i in range(0,longueur):
        result += '0'

    result = result[:-len(tmp)] + tmp
    return result



raw_string = ''
container = context


# selecting printer (user dependent)
local_user = container.portal_membership.getAuthenticatedMember().getUserName()
if local_user == 'Nicole_Denis' :
  printer_name = 'Meto_XS40_2'
elif local_user == 'Christelle_Megret' :
  printer_name = 'Meto_XS40_3'
elif local_user == 'Jocelyne_Olejarz' :
  printer_name = 'Meto_XS40_4'
elif local_user == 'Nathalie_Wadoux' :
  printer_name = 'Meto_XS40_5'
elif local_user == 'Chantal_Hannequin' :
  printer_name = 'Meto_XS40_6'
else :
  printer_name = 'Meto_XS40_2'

delivery = container.aq_parent

# Destination
client_title = delivery.getDestinationValue(portal_type=['Organisation']).getTitle()
client_address_items = delivery.getDestinationValue(portal_type=['Organisation']).getDefaultAddress().asText(country='France').split('\n')
client_address_1 = client_address_items[0]
if len(client_address_items) > 2 :
  client_address_2 = client_address_items[1]
else :
  client_address_2 = ''
client_city = client_address_items[len(client_address_items)-1]
client_zip_code = delivery.getDestinationValue(portal_type=['Organisation']).getDefaultAddress().getZipCode()

# Expediteur
source_section = delivery.getSourceSectionTitle()
list = delivery.portal_catalog(Title=source_section, portal_type = 'Organisation')
if len(list) > 0:
    expe = list[0].getObject()

    expe_title = expe.getTitle()
    expe_address_items = expe.getDefaultAddress().asText(country='France').split('\n')
    expe_address = expe_address_items[0]
    expe_city = expe_address_items[len(expe_address_items)-1]
    

# Printing protocol starts here
# first set some parameters
raw_string += selectMeter()
raw_string += setAsdFont()
#raw_string += setDecoration(1)
raw_string += startFormat()
raw_string += setPrintSpeed()
raw_string += setPaperSpeed()
raw_string += setTemparature()


# then design the label
# adress
raw_string += printFrame(1, 29, 41, 35, 99, 5, 5, 10)
# ref colis
raw_string += printFrame(1, 29, 8, 35, 33, 5, 5, 10)
# code produit extand
raw_string += printFrame(1, 3, 94, 26, 46, 5, 5, 10)
raw_string += printLine(1, 3, 64, 15, 30, 10)
# dpt
raw_string += printFrame(1, 18, 64, 11, 30, 5, 5, 10)
# expediteur
raw_string += printFrame(1, 3, 8, 26, 56, 5, 5, 10)


# calcul modulo
#recepisse = str(int(atof(delivery.getId())) % 1000000) + str( container.getIntIndex() % 100  )
recepisse = chaine( delivery.getId() , 1000000) + chaine( container.getIntIndex() , 100 )


case_society = {
    'BLS':'5433',
    'Houvenaegel':'1194',
    'Coramy':'0193' 
}
code_client = case_society[ source_section ]

code = '12119591'+code_client+'4012'+recepisse + chaine( container.getGrossWeight() * 10 , 1000  ) + '00' + client_zip_code[:2]
totpair = int(code[0])
totimpair = 0

for i in range(15):
    totimpair += int(code[(2*i)+1])
    totpair += int(code[(2*i)+2]) 

cal1 = str((totpair * 3) + totimpair)
digit = str ( 10 - int( cal1[ len(cal1) - 1 ]  ) )

if digit == '10':
    digit = '0'

code_barre = code+digit



# code barre
raw_string += printText(2, "d", 0, 0, 300, 70, 139, code_barre, 10)
raw_string += printText(2, "9", 0, 0, 300, 65, 111, code_barre, 10)


# expediteur
raw_string += printText(2, "9", 0, 0, 2, 22, 62, "Expediteur", 10)
raw_string += printText(2, "9", 0, 0, 2, 15, 62, expe_title , 10)
raw_string += printText(2, "9", 0, 0, 1, 10, 62, expe_address , 10)
raw_string += printText(2, "9", 0, 0, 1, 4, 62, expe_city , 10)

# destinataire
raw_string += printText(2, "9", 0, 0, 2, 56, 139, client_title  , 10)
raw_string += printText(2, "9", 0, 0, 2, 46, 139, client_address_1   , 10)
raw_string += printText(2, "9", 0, 0, 2, 41, 139, client_address_2  , 10)
raw_string += printText(2, "9", 0, 0, 3, 31, 139, client_city  , 10)

# colis
raw_string += printText(2, "9", 0, 0, 1, 58, 38, "Cde "+ delivery.getId() , 10)
raw_string += printText(2, "9", 0, 0, 1, 41, 38, "Poids "+ str( container.getGrossWeight()) + " Kg", 10)
raw_string += printText(2, "9", 0, 0, 1, 49, 38, "Colis "+ str(container.getIntIndex()), 10)
raw_string += printText(2, "9", 0, 0, 1, 32, 38, "Ref. "+ recepisse, 10)
raw_string += printText(2, "9", 0, 0, 4, 18, 134, "EXTAND", 10)
raw_string += printText(2, "9", 0, 0, 6, 3, 130, "B12", 10)
raw_string += printText(2, "9", 0, 0, 5, 17, 86, client_zip_code[:2] , 10)

raw_string += printText(2, "9", 0, 0, 6, 2, 87, context.PlanTransportExtand(client_zip_code[:2])[1] , 10)

# set the quentity to print
raw_string += setNumber()
raw_string += endFormat()

# send data to printer
#return chaine(94.2,10000)
context.sendRawToCups(printer_name, raw_string)
