## Script (Python) "Container_sendExtandEdi"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from DateTime import DateTime
from string import zfill,ljust

request = context.REQUEST
msg = ''


def decoupe(s,width):
    from string import ljust
    import string
    if len(s) > width:
        result = s[-width:]
    else:
        #result = string.ljust(s,width)
        result = (' ' * (width-len(s))) + s
        #return ' '+s
    return result

def chaine(num, width):
    s = str(int(num))
    if len(s) > width:
        result = s[-width:]
    else:
        result = zfill(s,width)
    return result


object_list = context.object_action_list(selection_name='sales_packing_list_selection')
for delivery in object_list:

    if delivery.getDeliveryMode() == 'Transporteur/Extand':

        # Destination
        client_title = delivery.getDestinationValue(portal_type=['Organisation']).getTitle()
        client_address_items = delivery.getDestinationValue(portal_type=['Organisation']).getDefaultAddress().asText(country='France').split('\n')
        client_address_1 = client_address_items[0]
        if len(client_address_items) > 2 :
            client_address_2 = client_address_items[1]
        else :
            client_address_2 = ''
        if len(client_address_items) > 3 :
            client_address_3 = client_address_items[2]
        else :
            client_address_3 = ''

        #client_city = client_address_items[len(client_address_items)-1]
        client_city = delivery.getDestinationValue(portal_type=['Organisation']).getDefaultAddress().getCity()

        client_zip_code = delivery.getDestinationValue(portal_type=['Organisation']).getDefaultAddress().getZipCode()

        client_tel = delivery.getDestinationValue(portal_type=['Organisation']).getDefaultTelephone().asText().split('\n')[0]


     

        plat = context.PlanTransportExtand(client_zip_code[:2])[0] 


        container_list = delivery.contentValues(filter={'portal_type':'Container'})
        for container in container_list:

            #recepisse = "%08d%02d" % (delivery.getId() ,container.getIntIndex())
            recepisse = chaine( delivery.getId(), 8 )+chaine(str(container.getIntIndex()) , 2)

            case_society = {
                'BLS':'5433',
                'Houvenaegel':'1194',
                'Coramy':'0193' 
            }
            source_section = delivery.getSourceSectionTitle()
            code_client = case_society[ source_section ]
     
            msg += "301959"+code_client+recepisse+"0100"+client_zip_code[:2]+chaine(container.getGrossWeight() * 10 , 3)        

            msg += DateTime().strftime("%Y%m%d")
          
            num_com_client = delivery.getCausalityValue(portal_type=['Sales Order']).getDestinationReference()
            msg += plat+"001000"+decoupe( num_com_client ,80)+decoupe(client_title ,32)+decoupe(client_address_1,32)
            msg += decoupe(client_address_2,32)+decoupe(client_address_3,32)+decoupe(client_zip_code,10)
            msg += decoupe(client_city,32)+decoupe(client_tel,16)+'\r\n'
            

request.RESPONSE.setHeader('Content-Type','application/text')
return msg
