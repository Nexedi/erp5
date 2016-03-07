# redirect to the given report
return getattr(context, report).generatePDF(REQUEST=context.REQUEST, RESPONSE=context.REQUEST.RESPONSE)
