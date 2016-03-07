# TODO: pre-select entries in fast input for checkbooks already present on context.
# Resuires modification to fast input listbox and checking all portal types using this script.
# See CashContainer_initFastInputForm.

context.REQUEST.form['list_start'] = 0
return context.CheckbookDelivery_fastInputForm()
