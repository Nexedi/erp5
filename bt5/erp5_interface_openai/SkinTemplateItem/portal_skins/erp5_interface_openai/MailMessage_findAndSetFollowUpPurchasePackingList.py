# -*- coding: utf-8 -*-
import json
import six

def safe_text(val):
  if val is None:
    return u''
  if six.PY2 and isinstance(val, str):
    return val.decode('utf-8', 'replace')
  return six.text_type(val)

def ascii_only(s):
  if six.PY2:
    if isinstance(s, unicode):
      return s.encode('ascii', 'ignore').decode('ascii')
    return s.decode('ascii', 'ignore')
  return s.encode('ascii', 'ignore').decode('ascii')

# --- 1. find PDF attachment ---
for info in context.getAttachmentInformationList():
  if info['filename'] != info['uid']:
    ct = info.get('content_type', '').lower()
    fn = info.get('filename', '').lower()
    if 'pdf' in ct or fn.endswith('.pdf'):
      pdf_info = info
      break
else:
  return 'No PDF attachment found'

pdf_data = context.getAttachmentData(index=pdf_info['index'])

# --- 2. call OpenAI ---
conn = context.portal_web_services.searchFolder(reference='openai')
if not conn:
  return 'OpenAI connector not found'
conn = conn[0].getObject()

prompt = u"""You are analyzing a scanned PDF of a Purchase Packing List \
(Lieferschein / delivery note) that our company received from a supplier.

Context:
- We are the BUYER (recipient of the goods). Our company is W\u00f6lfel.
- The SUPPLIER is the company that sent the goods to us.
- A shipper/carrier may have transported the goods on behalf of the supplier.

Extract the following fields from the PDF and return as JSON only \
(no explanation, no markdown fences, just the JSON object):

- supplier_name: the name of the company that SOLD and shipped the goods \
to us (NOT our company, NOT the carrier)
- shipper_name: the logistics/carrier company that transported the goods, \
or null if same as supplier or not mentioned
- shipping_date: delivery/shipping date in YYYY-MM-DD format, or null
- total_price: total invoice/delivery amount as a float, or null
- order_reference: any order number, delivery number, Belegnummer, \
Bestellnummer, Lieferscheinnummer, or Auftragsnummer found on the document, \
or null
- items: list of line items, each with keys: \
description (product/article name as written on the document), \
quantity (float or null), unit_price (float or null)
- currency: ISO currency code (EUR, USD, etc.) or null"""

r = conn.getResponse(prompt=prompt, attachment_data=pdf_data,
  attachment_filename=pdf_info.get('filename', 'a.pdf'),
  attachment_media_type='application/pdf', model='gpt-4.1')

r = r.strip()
if r.startswith('```'):
  r = u'\n'.join(l for l in r.splitlines() if not l.startswith('```')).strip()
extracted = json.loads(r)
extracted_json = json.dumps(extracted, ensure_ascii=True)

supplier_name = safe_text(extracted.get('supplier_name') or '').lower()
order_ref = safe_text(extracted.get('order_reference') or '').lower()
total_price = extracted.get('total_price')
extracted_items = extracted.get('items') or []

# --- 3. search catalog (no fallback) ---
kw = {'portal_type': 'Purchase Packing List'}
seen = {}
candidates = []

if supplier_name:
  for w in ascii_only(supplier_name).split():
    if len(w) >= 4:
      for b in context.portal_catalog(source_section_title='%%%s%%' % w, limit=20, **kw):
        if b.uid not in seen:
          seen[b.uid] = 1
          candidates.append(b.getObject())
      break

for item in extracted_items[:2]:
  desc = ascii_only(safe_text(item.get('description', '')))
  for w in desc.split():
    if len(w) >= 5:
      for b in context.portal_catalog(title='%%%s%%' % w, limit=10, **kw):
        if b.uid not in seen:
          seen[b.uid] = 1
          candidates.append(b.getObject())
      break

if order_ref:
  oref = ascii_only(order_ref)
  if oref:
    for b in context.portal_catalog(reference=oref, limit=10, **kw):
      if b.uid not in seen:
        seen[b.uid] = 1
        candidates.append(b.getObject())

if not candidates:
  return 'No candidates found. extracted=%s' % extracted_json[:300]

# --- 4. score ---
best_s = 0
best = None
for obj in candidates:
  s = 0
  ss = safe_text(obj.getSourceSectionTitle('')).lower()
  ttl = safe_text(obj.getTitle()).lower()
  cmt = safe_text(obj.getComment('')).lower()
  ref = safe_text(obj.getReference('')).lower()

  if supplier_name and ss:
    if supplier_name in ss or ss in supplier_name:
      s += 4
    else:
      s += min(sum(1 for w in supplier_name.split() if len(w) >= 3 and w in ss), 3)
  if order_ref:
    if order_ref in cmt: s += 6
    if order_ref in ref: s += 6
  if total_price is not None:
    try:
      pp = obj.getTotalPrice()
      if pp and abs(float(pp) - float(total_price)) < 1.0: s += 5
    except Exception: pass
  for item in extracted_items:
    d = safe_text(item.get('description', '')).lower()
    dw = [w for w in d.split() if len(w) >= 4]
    m = sum(1 for w in dw if w in ttl)
    if m: s += min(m * 2, 6)
  if s > best_s:
    best_s = s
    best = obj

if not best or best_s <= 0:
  return 'No match (score=%d, n=%d). extracted=%s' % (best_s, len(candidates), extracted_json[:200])

# --- 5. link ---
context.setFollowUpValue(best)

# --- 6. create Purchase Packing List Scan ---
try:
  scan = context.purchase_packing_list_scan_module.newContent(
    portal_type='Purchase Packing List Scan',
    title=pdf_info.get('filename', 'scan.pdf'),
    follow_up_value=best,
  )
  scan.setTextContent(json.dumps(extracted, ensure_ascii=False, indent=2))
  scan.setData(pdf_data)
  scan.setContentType('application/pdf')
  scan_url = scan.getRelativeUrl()
except Exception as e:
  scan_url = 'scan failed: %s' % repr(e)[:100]

return 'Linked (score=%d) to "%s" (%s). scan=%s. extracted=%s' % (
  best_s, safe_text(best.getTitle()), best.getRelativeUrl(), scan_url, extracted_json[:200])
