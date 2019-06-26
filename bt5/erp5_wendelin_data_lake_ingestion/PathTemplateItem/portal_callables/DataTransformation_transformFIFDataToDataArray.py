portal = context.getPortalObject()
reference_separator = portal.getIngestionReferenceDictionary()["reference_separator"]
reference_extension = input_stream_data.getReference().split(reference_separator)[-1]
result = str(context.processRawData(input_stream_data, output_array, output_descriptor, reference_extension))
