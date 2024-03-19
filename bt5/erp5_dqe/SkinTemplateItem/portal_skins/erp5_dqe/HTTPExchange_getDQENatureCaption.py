dqe_resource_category = context.getPortalObject().portal_categories.http_exchange_resource.dqe
# Values are hard-coded to fr, it is for Data Warehouse use and Investigation tab
return {
  dqe_resource_category.DefaultEmail: "Email",
  dqe_resource_category.DefaultTelephone: "Téléphone fixe",
  dqe_resource_category.MobileTelephone: "Mobile",
  dqe_resource_category.DefaultAddress: "Adresse facturation",
  dqe_resource_category.DeliveryAddress: "Adresse livraison",
  dqe_resource_category.OrganisationData: "Organisation",
  dqe_resource_category.RelocationData: "Déménagement",
}.get(context.getResourceValue(), '')
