"""
  This script is invoked at the end of ingestion process.
  The default behaviour is to receive messages so that they
  are marked as 'New' and appear in the worklist.
"""
context.setReportNumber(context.getTitle().split(' ').pop())
context.receive()
