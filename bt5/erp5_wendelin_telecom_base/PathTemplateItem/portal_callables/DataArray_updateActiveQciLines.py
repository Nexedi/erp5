'''
  Find every active QCI in the Data Array's data,
  and create a Data Array Line indexed to each active QCI's data
  for easy data retrieval and viewing if needed.
  Should only be used on Data Arrays containing data for a per-QCI 3GPP KPI.
'''
QCI_COUNT = 256

data_zarray = context.getArray()
if data_zarray is None:
  return
data_zarray = data_zarray[:]

for qci in range(QCI_COUNT):
  qci_data_view = data_zarray[qci::QCI_COUNT]
  qci_dl_hi = qci_data_view['dl_hi']
  qci_ul_hi = qci_data_view['ul_hi']

  # Silent QCI: skip
  if all(x == 0. for x in qci_dl_hi) and all(x == 0. for x in qci_ul_hi):
    continue

  active_qci_id = "active_qci_%s" % qci
  if context.get(active_qci_id) is None:
    context.newContent(
      id=active_qci_id,
      portal_type='Data Array Line',
      reference=active_qci_id,
      index_expression='%s::%s' % (qci, QCI_COUNT)
    )
