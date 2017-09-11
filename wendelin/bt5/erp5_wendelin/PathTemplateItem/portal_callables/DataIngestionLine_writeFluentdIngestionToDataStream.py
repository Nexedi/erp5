data_stream = out_data_stream['Data Stream']
data_stream.appendData(''.join([c[1] for c in context.unpack(data_chunk)]))
