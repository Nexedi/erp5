## Script (Python) "SaleInvoice_exportSage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=batch_mode=0,cr='\r',**kw
##title=
##
# generate a export file from a Sale Invoice for the Sage software

def priceWrite(price):
  from string import zfill
  s = '%.2f' % price
  width = 13
  if len(s) > width:
    result = s[-width:]
  else:
    result = zfill(s,width)
  return result

def mecg_text(invoice_date, datetime, invoice_number, compta_number, code_comptable, corporate_name, due_date):

  
  content = '#MECG'+cr
  content += 'VE'+cr
  content += invoice_date+cr
  
  content += datetime+cr
  content += invoice_number+(cr*3)
  content += compta_number+(cr*2)
  content += code_comptable+(cr*2)
  content += corporate_name+cr
  content += '0'+cr
  
  content += due_date+cr
  content += (('0'+cr)*3)
  
  return content

def mecg_text_part2(is_invoice, amount):

  content = ''
  content += is_invoice+cr
  content += priceWrite(amount)+cr
  content += (cr*3)+(('0'+cr)*5)
  
  return content

def meca_text(amount):

  content = '#MECA'+cr
  content += '1'+cr
  content += 'VENTES'+cr
  content += priceWrite(amount)+cr
  content += '0'+cr

  return content



request = context.REQUEST


file_content = ''

# globals variables
invoice_date = context.getStartDate().strftime('%d%m%y')
from DateTime import DateTime
datetime = DateTime().strftime('%d%m%y')
invoice_number = context.getReference()

code_comptable = context.getDestinationAdministrationValue().getCodeComptable()
corporate_name = context.getDestinationAdministrationValue().getCorporateName()
due_date = context.Invoice_zGetDueDate().strftime('%d%m%y')

if context.getValueAddedTaxRecoverable():
  vat = context.Invoice_zGetTotalVat()
else: 
  vat = 0.0

incomeHT = context.getTotalPrice()
income = context.Invoice_zGetTotalNetPrice()
# the decimals must be corrects
payable = float('%.2f' % income) + float('%.2f' % vat);


# parameters of SaleInvoice_exportSageCodeComptableList
analytique='VENTES' 
source_section_title=context.getSourceSectionTitle()
#amount_type= 
region=context.getDestinationAdministrationValue().getDefaultAddressRegion()
if region == None:
  region = 'France'
else:
  region = region.split('/')[-1]


compte_client=context.getDestinationAdministrationValue().getCodeComptable()

if compte_client in (None, ''):
  if not batch_mode:
    message="Erreur+sur+la+facture:+il+n\'y+a+pas+de+compte+comptable+sur+l\'organisation+à+facturer"
    redirect_url = '%s?%s%s' % ( context.absolute_url()+'/view', 'portal_status_message=',message)
    request[ 'RESPONSE' ].redirect( redirect_url )
    return None
  else:
    return None

# only the lasts 5 letters are usable
compte_client = compte_client[-5:]

cee_region_list = [
'Belgique',
'Danemark',
'Allemagne',
'Grece',
'Espagne',
'France',
'Irlande',
'Italie',
'Luxembourg',
'Pays-Bas',
'Autriche',
'Portugal',
'Finlande',
'Suede',
'Grande-Bretagne',
'Tchequie',
'Estonie',
'Chypre',
'Letonie',
'Lituanie',
'Hongrie',
'Malte',
'Pologne',
'Slovenie',
'Slovaquie'
]

if region in cee_region_list:
  if region == 'France':
    location = region
  else:
    location = 'CEE'
else:
  location = 'HCEE'


# TTC
amount_type='TTC'
compta_number = '4110000'
code_comptable = context.SaleInvoice_exportSageCodeComptableList(analytique, source_section_title, amount_type, location, compte_client)
is_invoice = '0'
#amount = '%s' % payable 
amount =  payable 
file_content += mecg_text(invoice_date=invoice_date, datetime=datetime, invoice_number=invoice_number, compta_number=compta_number, code_comptable=code_comptable, corporate_name=corporate_name, due_date=due_date)
file_content += mecg_text_part2(is_invoice=is_invoice, amount=amount)

# HT
amount_type='HT'
compta_number = context.SaleInvoice_exportSageCodeComptableList(analytique, source_section_title, amount_type, location, compte_client)
code_comptable = ''
is_invoice = '1'
#amount = '%s' % incomeHT 
amount = incomeHT
file_content += mecg_text(invoice_date=invoice_date, datetime=datetime, invoice_number=invoice_number, compta_number=compta_number, code_comptable=code_comptable, corporate_name=corporate_name, due_date=due_date)
file_content += mecg_text_part2(is_invoice=is_invoice, amount=amount)
file_content += meca_text(amount=amount)



# discount
discount_list_tmp = context.contentValues(filter={'portal_type':'Remise'})
discount_list_tmp2 = filter(lambda x: x not in [None,0] ,discount_list_tmp)

discount_list = filter(lambda x: x.getImmediateDiscount(), discount_list_tmp2 )

if len(discount_list) > 1:
  discount_list.sort(lambda x,y: cmp(y.getIntIndex(),x.getIntIndex()))

income_old = income
income_new = 0
discount_total = 0
did_we_have_another_discount = 0

for discount_line in discount_list:
  if discount_line.getDiscountTypeTitle() == 'Escompte':
    # escompte
    amount_type='escompte'
    compta_number = context.SaleInvoice_exportSageCodeComptableList(analytique, source_section_title, amount_type, location, compte_client)
    code_comptable = ''

    income_new = income_old / (1 - discount_line.getDiscountRatio())
    discount_total += income_new - income_old 
    remise_price = income_new - income_old

    income_old = income_new


    amount = remise_price
    is_invoice = '0'
    file_content += mecg_text(invoice_date=invoice_date, datetime=datetime, invoice_number=invoice_number, compta_number=compta_number, code_comptable=code_comptable, corporate_name=corporate_name, due_date=due_date)
    file_content += mecg_text_part2(is_invoice=is_invoice, amount=amount)
    file_content += meca_text(amount=amount)
  else:
    # all others discounts
    did_we_have_another_discount = 1

    income_new = income_old / (1 - discount_line.getDiscountRatio())
    discount_total += income_new - income_old 
    income_old = income_new
    

if did_we_have_another_discount:
  amount_type='discount'
  compta_number = context.SaleInvoice_exportSageCodeComptableList(analytique, source_section_title, amount_type, location, compte_client)
  code_comptable = ''
 
  amount = discount_total
  is_invoice = '0'

  file_content += mecg_text(invoice_date=invoice_date, datetime=datetime, invoice_number=invoice_number, compta_number=compta_number, code_comptable=code_comptable, corporate_name=corporate_name, due_date=due_date)
  file_content += mecg_text_part2(is_invoice=is_invoice, amount=amount)
  file_content += meca_text(amount=amount)

# VAT
amount_type='tva'
compta_number = context.SaleInvoice_exportSageCodeComptableList(analytique, source_section_title, amount_type, location, compte_client)
code_comptable = ''
is_invoice = '1'
amount = vat
file_content += mecg_text(invoice_date=invoice_date, datetime=datetime, invoice_number=invoice_number, compta_number=compta_number, code_comptable=code_comptable, corporate_name=corporate_name, due_date=due_date)
file_content += mecg_text_part2(is_invoice=is_invoice, amount=amount)


# and this is the end ....
if batch_mode:
  return file_content
else:
  # add the header and the end of the file
  file = '#FLG 000'+cr
  file += '#VER 5'+cr
  file += file_content
  file += '#FIN'

  request.RESPONSE.setHeader('Content-Type','text/plain')
  return file
