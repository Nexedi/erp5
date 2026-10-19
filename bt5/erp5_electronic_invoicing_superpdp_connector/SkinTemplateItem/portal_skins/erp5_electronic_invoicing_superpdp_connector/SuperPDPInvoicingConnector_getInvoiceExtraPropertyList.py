import json

portal = context.getPortalObject()
invoice = json.loads(text_content)

extra_dict = {
  "title": invoice["en_invoice"]["number"],
}

registration_identifier = invoice["en_invoice"]["seller"]["legal_registration_identifier"]
if registration_identifier["scheme"] == "0002":
  corporate_registration_code = registration_identifier["value"]

  # Search for Organisations so that we do not need to match manually every time
  matching_source_section_list = portal.portal_catalog(
    portal_type="Organisation",
    corporate_registration_code=corporate_registration_code,
    validation_state="validated",
  )

  if len(matching_source_section_list) == 1:
    extra_dict["source_section"] = matching_source_section_list[0]["relative_url"]

return extra_dict
