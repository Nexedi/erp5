import json

invoice_dict = json.loads(text_content)["en_invoice"]

registration_identifier = invoice_dict["seller"]["legal_registration_identifier"]
corporate_registration_code = None
if registration_identifier["scheme"] == "0002":
  corporate_registration_code = registration_identifier["value"]

return {
  "vat_code": invoice_dict["seller"]["vat_identifier"],
  "corporate_registration_code": corporate_registration_code,
}
