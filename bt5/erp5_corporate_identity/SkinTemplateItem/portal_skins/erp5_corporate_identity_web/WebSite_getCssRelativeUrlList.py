'''=============================================================================
                          List of CSS Files to load
============================================================================='''
if scope is not None:
  if scope == "global":
    return (
      'roboto/roboto.css',
      'roboto-condensed/roboto-condensed.css',
      'heuristica/heuristica.css',
      'ci_web_css/normalize.css',
      'ci_web_css/ci_web.css',
    )
return ()
