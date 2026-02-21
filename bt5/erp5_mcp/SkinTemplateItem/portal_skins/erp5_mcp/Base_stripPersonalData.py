"""Personal-data redaction policy for MCP tool results (GDPR).

MCPService._stripPersonalData calls this with a tool's structured result (a
JSON-compatible dict or list) when the MCP service has strip_personal_data
enabled, and passes on whatever comes back.

The generic policy is one rule: a personal record is masked down to its name.
Base_maskPersonalRecordData is where it lives and what it means; which records
are personal is Base_getPersonalDataTypeList, which an instance shadows to say
what else, beyond the Person, it holds to be personal data.

Nothing else is touched. A name is kept wherever it appears -- in search rows,
in module listboxes, in a relation field naming what it points at, and on the
personal record itself -- because a search whose rows read "[redacted]" leaves
every read tool with no answer to give, and buys little: the name is already
spread over every document the same authenticated user may read. What is worth
withholding is where a natural person lives and how they can be reached.

An instance adds rules of its own by shadowing THIS script from a skin folder
earlier in the skin path and calling Base_maskPersonalRecordData itself: a
project that delivers to private customers, say, goes on to mask the address
on the documents that deliver to them. To replace the policy outright, point
the MCP service's 'personal_data_policy_script' property elsewhere.
"""
return context.Base_maskPersonalRecordData(data)
