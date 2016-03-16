request = context.REQUEST

context.setTitle('%s - %s' % (start_number, stop_number))
for i in xrange(int(start_number), int(stop_number) + 1):
  newline = context.newContent(portal_type='Check', title=str(i))
  newline.setDestination(context.getDestinationSection())
  newline.setStartDate(context.getStartDate())

request.RESPONSE.redirect(context.absolute_url())
