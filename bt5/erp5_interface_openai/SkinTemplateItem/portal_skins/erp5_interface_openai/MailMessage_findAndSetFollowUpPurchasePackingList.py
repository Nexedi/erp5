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

# --- 1.1 find PDF attachment ---
for info in context.getAttachmentInformationList():
  if info['filename'] != info['uid']:
    ct = info.get('content_type', '').lower()
    fn = info.get('filename', '').lower()
    if 'pdf' in ct or fn.endswith('.pdf'):
      pdf_info = info
      break
else:
  return 'No PDF attachment found'

# --- 1.2 find OCR attachment ---
for info in context.getAttachmentInformationList():
  if info['filename'] != info['uid']:
    ct = info.get('content_type', '').lower()
    fn = info.get('filename', '').lower()
    if 'txt' in ct or fn.endswith('.txt'):
      ocr_info = info
      break
else:
  return 'No OCR attachment found'


pdf_data = context.getAttachmentData(index=pdf_info['index'])
ocr_data = safe_text(context.getAttachmentData(index=ocr_info['index']))

# --- 2. call OpenAI ---
conn = context.portal_web_services.searchFolder(reference='openai')
if not conn:
  return 'OpenAI connector not found'
conn = conn[0].getObject()

prompt = u"""Extract structured data from a scanned Purchase Packing List (Lieferschein / delivery note).

Rules:
- The document may be in German or English.
- Determine the language internally and use it to interpret field names.
- Do NOT include the language in the output.
- Use only information visible in the document.
- Do not translate company names or product names.
- Return only a JSON object, no explanation, no markdown.

Context:
- Buyer: Wölfel Engineering GmbH & Co. KG (including WBI, WWM, WWS)
  → Do NOT return these as supplier.

Fields:

- supplier_name:
  - Company that sold/shipped the goods.
  - Prefer the company name in the header or address block.
  - Do not choose product brands or internal departments (e.g. Einkauf).

- shipper_name:
  - Transport/logistics company, or null if not mentioned.

- shipping_date:
  - Delivery/shipping date (e.g. Lieferdatum).
  - Format as YYYY-MM-DD if possible, otherwise null.

- total_price:
  - Total amount as number, or null.

- order_reference:
  - Order or document number (e.g. Belegnummer, Bestellnummer, Lieferscheinnummer, Vorgang).
  - If multiple exist, choose the most likely one.

- items:
  - List of items:
    - description: copy as written; fix obvious OCR mistakes only if clearly recognizable
    - quantity: number or null
    - unit_price: number or null

- currency:
  - ISO code (EUR, USD, etc.) or null.

Return only the JSON object.

Use the following extracted ocr text to help you match data from the scanned PDF to actual values:

%s
"""%(ocr_data)

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

# Maybe instead of trying to find the correct document, we try to find the correct supplier.
# So instead of limiting us to 20 documents which could miss the correct one or only be from one wrong supplier
# we can try and find at most 20 suppliers with a name that could work (using group_by)
# We can then add the name as an additional filter for the next searches
# If all other searches fail with this filter, we might need to discard the supplier name

# Also maybe it would be better to search the other way, so first try using the whole name, then remove parts from it.
# The longer the match the better, so e.g. Company Germany and Company Belgium would both match if we only gave Company.
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
scored_candidates = []

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
      if pp and abs(float(pp) - float(total_price)) < 1.0:
        s += 5
    except Exception:
      pass

  for item in extracted_items:
    d = safe_text(item.get('description', '')).lower()
    dw = [w for w in d.split() if len(w) >= 4]
    m = sum(1 for w in dw if w in ttl)
    if m:
      s += min(m * 2, 6)

  scored_candidates.append({
    'obj': obj,
    'score': s,
    'supplier': safe_text(obj.getSourceSectionTitle('')),
    'title': safe_text(obj.getTitle()),
    'comment': safe_text(obj.getComment('')),
    'reference': safe_text(obj.getReference('')),
    'total_price': obj.getTotalPrice() if hasattr(obj, 'getTotalPrice') else None,
  })

# --- 5. select top 3 ---
# We reduce the size of the request but if the scoring is bad we might fail later
scored_candidates.sort(key=lambda x: x['score'], reverse=True)
top_candidates = [c for c in scored_candidates if c['score'] > 0][:3]

if not top_candidates:
  return 'No match (no scored candidates). extracted=%s' % extracted_json[:200]

# --- 6. prepare candidate data for GPT ---
candidate_data = []
for c in top_candidates:
  candidate_data.append({
    'id': c['obj'].getRelativeUrl(),
    'supplier': c['supplier'],
    'title': c['title'],
    'comment': c['comment'],
    'reference': c['reference'],
    'total_price': c['total_price'],
    'score': c['score'],
  })

# --- 7. build matching prompt ---
# This should be quite strict in the sense that if none of the candidates have e.g. their reference match any possible order number in the document it will most likely choose none of them
matching_prompt = u"""You are matching a scanned delivery note to internal purchase documents.

Task:
1. Carefully review the OCR text of the delivery note. Correct any mistakes in previously extracted fields (order/reference number, supplier, item descriptions, totals, etc.).
2. Determine if ANY of the candidates is a correct match using the corrected extraction or the ocr data.
   Only return a match if there is STRONG evidence.

STRICT RULES:
- Do NOT guess.
- Do NOT pick the closest match.
- If key fields do not align, you MUST return no match.
- Be conservative: false positives are worse than false negatives.

Strong evidence includes:
- Matching or very similar order/reference numbers (use OCR data)
- If the order/reference number of the candidate exists in the OCR data, this is very strong evidence
- Strong overlap in item descriptions
- Matching supplier (allow small variations)

Weak signals (NOT sufficient alone):
- Similar supplier name
- Partial keyword overlap
- Close total price

Return ONLY JSON:

If a correct match exists:
{
  "best_match_id": "...",
  "confidence": 0-1,
  "reason": "short explanation"
}

If NO correct match exists:
{
  "best_match_id": null,
  "confidence": 0,
  "reason": "why all candidates were rejected"
}

IMPORTANT:
- Confidence > 0.8 ONLY if multiple strong signals align
- Confidence < 0.5 if any uncertainty exists
- If in doubt → return null

ORIGINAL OCR TEXT:
%s

PREVIOUS EXTRACTION (may contain errors):
%s

CANDIDATES:
%s
""" % (
  prompt,
  extracted_json,
  json.dumps(candidate_data, ensure_ascii=False, indent=2)
)

# --- 8. call GPT for final decision ---

match_response = conn.getResponse(prompt=matching_prompt, attachment_data=pdf_data,
  attachment_filename=pdf_info.get('filename', 'a.pdf'),
  attachment_media_type='application/pdf', model='gpt-4.1')

match_response = match_response.strip()
if match_response.startswith('```'):
  match_response = u'\n'.join(l for l in match_response.splitlines() if not l.startswith('```')).strip()
match_response_json = json.loads(match_response)

best_match_id = match_response_json.get("best_match_id")
confidence = match_response_json.get("confidence")
best = None
if best_match_id:
  best = context.purchase_packing_list_module.get(best_match_id.split("/")[-1])

if not best:
  return 'No match. extracted=%s' % (extracted_json[:200])

# --- 5. link ---
# If we test on prod. comment out this line to not modify existing purchase packing lists
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

return 'Linked (confidence=%d) to "%s" (%s). scan=%s. extracted=%s' % (
  confidence, safe_text(best.getTitle()), best.getRelativeUrl(), scan_url, extracted_json[:200])
