##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#                    Kazuhiko <kazuhiko@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

"""Send a mail with attachments.
"""

import smtplib
import re
from datetime import date
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.Message import Message

def sendMail(subject,
             body,
             attachments = [],
             status = False,
             from_mail = 'nobody@erp5.org',
             to_mail = [ 'erp5-report@erp5.org' ]):
    if attachments:
        msg = MIMEMultipart()
    else:
        msg = Message()

    msg['Subject'] = subject
    msg['From']    = from_mail
    msg['To']      = ', '.join(to_mail)
    msg['X-ERP5-Tests'] = 'ERP5'

    if status:
        msg['X-ERP5-Tests-Status'] = 'OK'

    # Guarantees the message ends in a newline
    msg.preamble = subject
    msg.epilogue = ''

    if attachments:
        mime_text = MIMEText(body)
        mime_text.add_header('Content-Disposition', 'attachment',
                             filename='body')
        msg.attach(mime_text)
        html_re = re.compile('<html>', re.I)
        for item in attachments:
            mime_text = MIMEText(item)
            if html_re.match(item):
                mime_text.set_type('text/html')
                mime_text.add_header('Content-Disposition', 'attachment',
                                     filename='attachment.html')
            else:
                mime_text.add_header('Content-Disposition', 'attachment',
                                     filename='attachment.txt')
            msg.attach(mime_text)

    else:
        msg.set_payload(body)

    # Send the email via our own SMTP server.
    s = smtplib.SMTP()
    s.connect()
    s.sendmail(from_mail, to_mail, msg.as_string())
    s.close()
