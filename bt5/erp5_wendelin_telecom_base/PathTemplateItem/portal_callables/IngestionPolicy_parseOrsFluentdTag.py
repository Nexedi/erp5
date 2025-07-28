if not reference:
  raise ValueError('reference is not defined')

ors_fluentd_tag_prefix = "ors."
if not reference.startswith(ors_fluentd_tag_prefix):
  raise ValueError('reference %s is not a valid ORS fluentd tag' % reference)

reference = reference[len(ors_fluentd_tag_prefix):]

return {
  'resource_reference' : context.data_product_module.ors_enb_log_data.getReference(),
  'specialise_reference': reference,
  'reference': reference
}
