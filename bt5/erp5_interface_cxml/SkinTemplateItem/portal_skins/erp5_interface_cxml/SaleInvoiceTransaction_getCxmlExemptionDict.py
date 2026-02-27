vat_exemption = context.getVatExemption()

exemption_dict = {
  'exemptDetail': None,
  'exemptCode': None,
  'ExemptReason': None,
  'description': None,
}

if vat_exemption in ("rev_charge", "eu"):
  exemption_dict['exemptDetail'] = "zeroRated"
  exemption_dict['exemptCode'] = "AE"
  exemption_dict['ExemptReason'] = "Reverse charge system"
  if vat_exemption == "rev_charge":
    exemption_dict['description'] = "EU Reverse Charge - Service"
  elif vat_exemption == "eu":
    exemption_dict['description'] = "EU Reverse Charge - Goods"


return exemption_dict
