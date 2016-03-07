source = context.getBaobabSource()
destination = context.getBaobabDestination()

if source.split("/")[-1] == destination.split("/")[-1]:
  if ("reserve" in source) and ("caisse_courante" in destination):
    variation = context.getVariationText()
    result = variation.replace('new_emitted', 'valid')
    return result
return context.getVariationText()
