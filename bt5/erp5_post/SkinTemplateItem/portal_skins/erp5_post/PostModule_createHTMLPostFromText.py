return context.PostModule_createHTMLPost(
  title=data.splitlines()[0][:30] if data else None,
  source_reference=source_reference,
  data=data,
  follow_up=follow_up,
  predecessor=predecessor,
  immediate_reindex_context_manager=immediate_reindex_context_manager,
)
