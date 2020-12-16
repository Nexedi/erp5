from Products.PythonScripts.standard import html_quote

# even if we have several divergence testers, the first
# one is enough for displaying the title.
tester = context.getCausalityValue()
return '<div>%s</div><div><em>%s</em></div>' % (
    html_quote(tester.getTranslatedTitle()),
    context.getExplanationMessage())
