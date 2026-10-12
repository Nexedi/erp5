"""Restrict portal types to selected fields to prevent sensitive data being send to a LLM."""

restricted_column_map = {
  # Send no personal data to LLM
  "Person": ["uid"],
}

try:
  return restricted_column_map[portal_type_id]
except KeyError:
  return None
