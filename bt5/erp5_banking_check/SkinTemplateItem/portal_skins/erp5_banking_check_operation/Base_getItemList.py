from Products.ERP5Type.Document import newTempBase

if vault is not None:
  if not vault.endswith('encaisse_des_billets_et_monnaies'):
    vault = "%s/%s" % (vault,'encaisse_des_billets_et_monnaies')

listbox_data = context.Delivery_getCheckbookList(batch_mode=1,node=vault,at_date=at_date)

result_list = []
i=0
for line in listbox_data:
  result_list.append(newTempBase(context, "new_%3i" % i, **line))
  i+=1
return result_list
