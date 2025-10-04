if not reference:
  raise ValueError('reference is not defined')

if reference.startswith("fluent"):
  return {}

cdn_fluentd_tag_prefix = "cdnaccess."
if not reference.startswith(cdn_fluentd_tag_prefix):
  raise ValueError('reference %s is not a valid CDN Access fluentd tag' % reference)

reference = reference[len(cdn_fluentd_tag_prefix):]
return {
  'resource_reference' : context.data_product_module.cdn_access_log_data.getReference(),
  'specialise_reference': reference,
  'reference': reference
}
