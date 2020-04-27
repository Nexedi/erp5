return [i for i in context.objectValues(**kw) if i.getVisibilityState() == "visible"]
