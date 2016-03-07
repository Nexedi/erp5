source = context.getSource()
if source != None:
  if not 'ventilation' in source:
     return "%s/caveau/serre/encaisse_des_billets_retires_de_la_circulation"  %("/".join(source.split("/")[:-3]),)
  else:
     return "%s/caveau/serre/encaisse_des_billets_retires_de_la_circulation"  %("/".join(source.split("/")[:-4]),)
