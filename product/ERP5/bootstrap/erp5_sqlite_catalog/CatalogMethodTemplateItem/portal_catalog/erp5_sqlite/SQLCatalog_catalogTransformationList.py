# Indexing all transformation lines for all possible variations of a Resource can be very costly.
# Avoid doing this in a single transaction, and split the operation.

batch_size = 100
current_batch = []
current_size = 0

for i, transformation in enumerate(getDefaultConversionTransformationValue):
  if transformation is None:
    continue
  transformation_relative_url = transformation.getRelativeUrl()
  variation_list_list = getTransformationVariationCategoryCartesianProduct[i]
  size = len(transformation)*len(variation_list_list)

  if size + current_size < batch_size:
    current_batch.append((transformation_relative_url, variation_list_list))
    current_size += size
  else:
    if current_batch:
      context.activate(activity='SQLQueue').SQLCatalog_catalogTransformation(current_batch)
    current_batch = [(transformation_relative_url, variation_list_list)]
    current_size = size


if current_batch:
  context.activate(activity='SQLQueue').SQLCatalog_catalogTransformation(current_batch)
