mapping_dict = {
  "wire_transfer": "Account"
}
payment_mode = context.getPaymentConditionPaymentMode()
return mapping_dict[payment_mode]
