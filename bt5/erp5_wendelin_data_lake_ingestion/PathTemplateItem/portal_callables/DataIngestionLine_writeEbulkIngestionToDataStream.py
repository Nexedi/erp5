import base64
decoded = base64.b64decode(data_chunk)
data_stream.appendData(decoded)
