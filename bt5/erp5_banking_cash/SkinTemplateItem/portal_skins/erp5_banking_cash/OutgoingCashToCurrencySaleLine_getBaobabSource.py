currency = context.getResourceTitle()

var_ressource_title = context.getParentValue().getResourceTitle().lower()
var_ressource_title = var_ressource_title.replace(" ", "_")

encaisse_devise = "/encaisse_des_devises/%s/sortante" %(var_ressource_title)
#encaisse_devise = "/encaisse_des_devises/%s/sortante" %(context.getParentValue().getResourceTitle().lower())


counter_site = context.getSource()
destination = counter_site + encaisse_devise
return destination
