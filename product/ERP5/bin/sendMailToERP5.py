#!/usr/bin/python

# This python module will send a mail message to a ERP5 site
# Taken from sendMailToZope.py in CMFMailin.

# $Id: sendMailToZope.py,v 1.1.1.1 2002/05/31 09:13:06 andyd Exp $

__version__='$Revision: 1.1.1.1 $'[11:-2]  

import sys, urllib
import rfc822, StringIO, string

def sendMail(url, messageText):
    if url:
        if not url[-len('/postUTF8MailMessage'):] == '/postUTF8MailMessage':
            url = url + '/postUTF8MailMessage'

        try:
            result = urllib.urlopen(url, urllib.urlencode({'file':messageText})).read()
        except (IOError,EOFError),e:
            print "ZMailIn Error: Problem Connecting to server",e
            sys.exit(73)
                
        # if the ZMailIn Client's method returned anything, then 'something bad' happened.
        if result:
            print result
            sys.exit(1)
                        
        sys.exit(0)

    print "ZMailIn Error: No ZMailIn Client URL found or specified."
    sys.exit(1)
    

if __name__ == '__main__':
    # This gets called by the MTA when a new message arrives.
    # The mail message file gets passed in on the stdin

    # First get a handle on the message file
    f = sys.stdin   
    messageText = f.read()
        
    url = ''
    if len(sys.argv)>1:
        url = sys.argv[1]
        
    if not url:
        print "ZMailIn Error: You must specify the URL" \
              " to the ERP5 instance in the First arguement. " \
              "i.e. python sendMailToERP5.py http://www.myserver.com/erp5/"
        sys.exit(1)

    sendMail(url, messageText)
        
