## Script (Python) "mail_received"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=theMail
##title=
##
# This method gets called when a mail arrives at the portal object

# the variable called 'theMail' contains the entire mail in a dictionary
# set out in the following format:
#
#        {'attachments': {},
#         'body': 'THis is a mailIn test from ME.\n\nHa Ha\n\n-Andy\n\n',
#         'headers': {'content-transfer-encoding': '7bit',
#                     'content-type': 'text/plain;\n charset="iso-8859-1"',
#                     'date': 'Tue, 13 Jun 2000 09:34:08 +0100',
#                     'from': '"Andy Dawkins" <andyd@nipltd.com>',
#                     'importance': 'Normal',
#                     'message-id': '<NEBBLGACMKDPCFFIIEALKEDDCBAA.andyd@nipltd.com>',
#                     'mime-version': '1.0',
#                     'subject': 'Mail In Test',
#                     'to': '<testing@legolas.private.nipltd.com>'},
#         'localpart': 'testing'}

# This is just an example Mail handeler method
# It is designed to give you an idea of how one should be written
# And it is used to test the MailIn tool

# Get the members folder
mf = container.portal_url.getPortalObject().Members

# Check if the localpart exists in the members folder
if not theMail['localpart'] in mf.objectIds():
  raise "NotFound", "Cannot find the user '%s' that the email was destined for"%theMail['localpart']

# get a handle on the user folder
uf = mf[theMail['localpart']] 

uf.invokeFactory(type_name='MailMessage', 
                        id=container.strip_punctuation(theMail['headers']['message-id']),
                     title=theMail['headers'].get('subject'),
                   subject=theMail['headers'].get('subject'),
                      date=theMail['headers'].get('date'),
                        to=theMail['headers'].get('to'),
                    sender=theMail['headers'].get('from'),
                   replyto=theMail['headers'].get('replyto'),
                      body=theMail['body'],
                   headers=theMail['headers'],
                 otherInfo=theMail['localpart'],
               attachments=theMail['attachments']
                 )
           
# the return of None indicates a success
# The return of anything else assumes that you are returning an error message
# and most MTA's will bounce that error message back to the mail sender
return None
