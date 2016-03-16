return [line for line in context.searchFolder(**kw) if not (line.getId() == "default_bug_line")]
