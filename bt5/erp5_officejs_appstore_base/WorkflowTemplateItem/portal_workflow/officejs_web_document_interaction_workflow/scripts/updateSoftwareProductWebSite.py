web_page = state_change['object']
if web_page.getPublicationSection() == "application/landing_page":
  software_product = web_page.getFollowUpValue("Software Product")
  if software_product:
    # XXX Should be using an alarm
    software_product.activate(
      after_path_and_method_id=(
        (web_page.getPath(),),
        ("immediateReindexObject", )
       )).SoftwareProduct_fixRelatedWebSite()
