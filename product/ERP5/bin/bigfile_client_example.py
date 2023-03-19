input_file = open('big_file.log', 'r')

import six.moves.http_client
connection =  six.moves.http_client.HTTPConnection('192.168.242.68:12001')

import base64
base64string = base64.encodebytes('zope:insecure')[:-1]

n = 1 << 20


######################################
# Create new document
######################################

headers = {
    'Authorization': 'Basic %s' % base64string,
    }
connection.request('POST', "/erp5/portal_contributions/newContent?" \
                           "portal_type=Big%20File&filename=big_file.log&container_path=big_file_module&data=", "", headers)
result = connection.getresponse()
path = result.getheader("X-Document-Location")
result.close()
path = '/%s' % '/'.join(path.split('/')[3:])
print(path)

######################################
# Upload chunks
######################################

input_file.seek(0, 2)
end = input_file.tell()

input_file.seek(0)
pos = input_file.tell()

first = True

while pos < end:
  next_pos = pos + n
  if next_pos > end:
    next_pos = end

  body_content = input_file.read(next_pos-pos)
  if first:
    headers = {
        'Authorization': 'Basic %s' % base64string,
        }
  else:
    headers = {
        'Authorization': 'Basic %s' % base64string,
        'Content-Range': 'bytes %i-%i/%i' % (pos, next_pos-1, next_pos),
        }
  connection.request('PUT', path, body_content, headers)
  result = connection.getresponse()

  pos = input_file.tell()
  first = False

######################################
# Download chunks
######################################

output_file = open('output_file.webm', 'wb')
output_file.seek(0)

headers = {
  'Authorization': 'Basic %s' % base64string,
  'Content-Range': 'bytes */*',
}
connection.request('PUT', path, '', headers)
result = connection.getresponse()
filerange = result.getheader('Range')
size = int(filerange.split('-')[1])

pos = 0
while pos < size:

  next_pos = pos + n
  if next_pos > size:
    next_pos = size

  headers = {
    'Authorization': 'Basic %s' % base64string,
    'Range': 'bytes=%s-%s' % (pos, next_pos),
  }
  connection.request('GET', path, '', headers)
  result = connection.getresponse()
  output_file.write(result.read())
  result.close()

  pos = output_file.tell()
