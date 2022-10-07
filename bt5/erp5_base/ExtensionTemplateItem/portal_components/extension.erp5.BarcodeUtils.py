def generateBarcodeImage(self, barcode_type, data, REQUEST=None):
  # huBarcode's DataMatrix support has limitation for data size.
  # huBarcode's QRCode support is broken.
  # more 1-D barcode types can be added by pyBarcode library.
  barcode_type = barcode_type.lower()
  if barcode_type == 'datamatrix':
    from subprocess import Popen, PIPE
    process = Popen(['dmtxwrite'],
                     stdin=PIPE,
                     stdout=PIPE,
                     stderr=PIPE,
                     close_fds=True)
    output, _ = process.communicate(input=data)
  elif barcode_type == 'ean13':
    from hubarcode.ean13 import EAN13Encoder
    encoder = EAN13Encoder(data)
    output = encoder.get_imagedata()
  elif barcode_type == 'code128':
    from hubarcode.code128 import Code128Encoder
    encoder = Code128Encoder(data)
    encoder.text = '' # get barcode image only
    output = encoder.get_imagedata()
  elif barcode_type == 'qrcode':
    import qrcode
    from six.moves import cStringIO as StringIO
    fp = StringIO()
    img = qrcode.make(data)
    img.save(fp, 'png')
    fp.seek(0)
    output = fp.read()
  else:
    raise NotImplementedError('barcode_type=%s is not supported' % barcode_type)
  if REQUEST is not None:
    REQUEST.RESPONSE.setHeader('Content-Type', 'image/png')
  return output
