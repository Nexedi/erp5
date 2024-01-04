debug=True
request=context.REQUEST
from Products.ERP5Type.Message import Message

# empty class for report data
class Dane:pass

# only one report implemented at this time - monthly VAT
mess=Message(domain='ui',message='VAT-7 is a monthly report')

#check dates - VAT report is always monthly
if request.from_date.month()!=request.at_date.month() or request.from_date.year()!=request.at_date.year():
  return request.RESPONSE.redirect(context.absolute_url()+'/AccountingTransactionModule_viewFiscalReportDialog?portal_status_message='+str(mess))

dane=Dane()
for f in range(20,60):
  setattr(dane,'p'+str(f),0)

dane.p08_1='x' # XXX: should we allow for accounting business of a person?

# data calculation
dane.p20=-context.getCredit(('7015','7025','7075','7315','7325'))
dane.p22=-context.getCredit(('7014','7024','7074','7314','7324'))
dane.p24=-context.getCredit(('7013','7023','7073','7313','7323'))
dane.p26=-context.getCredit(('7012','7022','7072','7312','7322'))
dane.p28=-context.getCredit(('7011','7021','7071','7311','7321'))
dane.p25=-context.getCredit(('2223',))
dane.p27=-context.getCredit(('2222',))
dane.p29=-context.getCredit(('2221',))

dane.p40=dane.p20+dane.p21+dane.p22+dane.p24+dane.p26+dane.p28+dane.p30+dane.p31+dane.p32+dane.p34+dane.p36
dane.p41=dane.p25+dane.p27+dane.p29+dane.p33+dane.p35+dane.p37+dane.p38-dane.p39

try:dane.p42=float(request.get('carryforward',0))
except ValueError:pass

dane.p44=context.getDebit(('304',))
dane.p45=context.getDebit(('2232',))
dane.p46=context.getDebit(('30',))-dane.p44
dane.p47=context.getDebit(('2231',))

dane.p50=dane.p42+dane.p43+dane.p45+dane.p47+dane.p48+dane.p49
if dane.p41>dane.p50:dane.p53=dane.p41-dane.p50-dane.p51-dane.p52
else:dane.p55=dane.p50-dane.p41+dane.p54
dane.p56=max(dane.p55-dane.p53,0)
dane.p59=dane.p55-dane.p56

if debug:
  for f in range(20,60):
    n='p'+str(f)
    print(n,getattr(dane,n))
  return printed

return container[report].index_html(REQUEST=context.REQUEST, RESPONSE=context.REQUEST.RESPONSE,dane=dane)
