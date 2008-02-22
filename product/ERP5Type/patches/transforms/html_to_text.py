#  This is taken from PortalTransforms product
#
# Copyright (c) 2002-2003, Benjamin Saller <bcsaller@ideasuite.com>, and 
# 	                the respective authors.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.	
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following disclaimer
#       in the documentation and/or other materials provided with the
#       distribution. 
#     * Neither the name of Archetypes nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission. 
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 


from Products.PortalTransforms.libtransforms.retransform import retransform

class html_to_text(retransform):
    inputs  = ('text/html',)
    output = 'text/plain'

def register():
    # XXX convert entites with htmlentitydefs.name2codepoint ?
    return html_to_text("html_to_text",
                       ('<script [^>]>.*</script>(?im)', ''),
                       ('<style [^>]>.*</style>(?im)', ''),
                       ('<head [^>]>.*</head>(?im)', ''),
                       
                       # added for ERP5, we want to transform <br/> in newlines
                       ('<br[\s\/]*>(?im)', '\n'),

                       ('(?im)<(h[1-6r]|address|p|ul|ol|dl|pre|div|center|blockquote|form|isindex|table)(?=\W)[^>]*>', ' '),
                       ('<[^>]*>(?i)(?m)', ''),
                       )
