import io
import six
from Products.ERP5Type.Utils import str2bytes

# pylint:disable=import-error
def generateBarcodeImage(self, barcode_type, data, REQUEST=None):
  # type: (str, str, HTTPRequest) -> bytes
  barcode_type = barcode_type.lower()
  if barcode_type == 'datamatrix':
    from subprocess import Popen, PIPE
    process = Popen(['dmtxwrite'],
                     stdin=PIPE,
                     stdout=PIPE,
                     stderr=PIPE,
                     close_fds=True)
    output, _ = process.communicate(input=str2bytes(data))
  elif barcode_type == 'ean13':
    if six.PY3:
      import barcode.ean
      import barcode.writer
      fp = io.BytesIO()
      barcode.ean.EuropeanArticleNumber13(
        data, writer=barcode.writer.ImageWriter()
      ).render().save(fp, format='png')
      output = fp.getvalue()
    else:
      from hubarcode.ean13 import EAN13Encoder
      encoder = EAN13Encoder(data)
      output = encoder.get_imagedata()
  elif barcode_type == 'code128':
    if six.PY3:
      import barcode.codex
      import barcode.writer
      class NoTextImageWriter(barcode.writer.ImageWriter):
        def _paint_text(self, *args):
          pass
      fp = io.BytesIO()
      barcode.codex.Code128(
        data, writer=NoTextImageWriter()
      ).render(
        # we also set a font_size of 0, so that the bounding box of the
        # image does not include white space for the text.
        writer_options={'font_size': 0}
      ).save(fp, format='png')
      output = fp.getvalue()
    else:
      from hubarcode.code128 import Code128Encoder
      encoder = Code128Encoder(data)
      encoder.text = '' # get barcode image only
      output = encoder.get_imagedata()
  elif barcode_type == 'qrcode':
    import qrcode
    fp = io.BytesIO()
    img = qrcode.make(str2bytes(data))
    img.save(fp, 'png')
    fp.seek(0)
    output = fp.getvalue()
  else:
    raise NotImplementedError('barcode_type=%s is not supported' % barcode_type)
  if REQUEST is not None:
    REQUEST.RESPONSE.setHeader('Content-Type', 'image/png')
  return output
# pylint:enable=import-error
