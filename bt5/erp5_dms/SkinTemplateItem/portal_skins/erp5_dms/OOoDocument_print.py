"""
We assume that if you want a printout, you'd be happy with pdf
so this is what we return.
"""

request = context.REQUEST
return context.index_html(request, request.RESPONSE, format='pdf')
