import json

invoice = json.loads(text_content)
return {
  "title": invoice["en_invoice"]["number"],
}
