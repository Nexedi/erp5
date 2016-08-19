ingestion_policy = state_change['object']
reference = context.REQUEST.get('reference')
data_chunk = context.REQUEST.get('data_chunk')
ingestion_policy.activate(
    serialization_tag="IngestionPolicy_forward_%s" %ingestion_policy.getUid()
  ).IngestionPolicy_forward(reference, data_chunk)
