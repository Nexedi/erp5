##############################################################################
#
# Copyright (c) 2001 Zope Foundation and Contributors.
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from Products.SiteAccess.VirtualHostMonster import VirtualHostMonster
from ZPublisher.BaseRequest import quote

def __call__(self, client, request, response=None):
    '''Traversing at home'''
    vh_used = 0
    stack = request['TraversalRequestNameStack']
    path = None
    while 1:
        if stack and stack[-1] == 'VirtualHostBase':
            vh_used = 1
            stack.pop()
            protocol = stack.pop()
            host = stack.pop()
            if ':' in host:
                host, port = host.split(':')
                request.setServerURL(protocol, host, port)
            else:
                request.setServerURL(protocol, host)
            if '*' in stack:
              stack[stack.index('*')] = host.split('.')[0]
            path = list(stack)

        # Find and convert VirtualHostRoot directive
        # If it is followed by one or more path elements that each
        # start with '_vh_', use them to construct the path to the
        # virtual root.
        vh = -1
        for ii in range(len(stack)):
            if stack[ii] == 'VirtualHostRoot':
                vh_used = 1
                pp = ['']
                at_end = (ii == len(stack) - 1)
                if vh >= 0:
                    for jj in range(vh, ii):
                        pp.insert(1, stack[jj][4:])
                    stack[vh:ii + 1] = ['/'.join(pp), self.id]
                    ii = vh + 1
                elif ii > 0 and stack[ii - 1][:1] == '/':
                    pp = stack[ii - 1].split('/')
                    stack[ii] = self.id
                else:
                    stack[ii] = self.id
                    stack.insert(ii, '/')
                    ii += 1
                path = stack[:ii]
                # If the directive is on top of the stack, go ahead
                # and process it right away.
                if at_end:
                    request.setVirtualRoot(pp)
                    del stack[-2:]
                break
            elif vh < 0 and stack[ii][:4] == '_vh_':
                vh = ii

        if vh_used or not self.have_map:
            if path is not None:
                path.reverse()
                vh_part = ''
                if path and path[0].startswith('/'):
                    vh_part = path.pop(0)[1:]
                if vh_part:
                    request['VIRTUAL_URL_PARTS'] = vup = (
                        request['SERVER_URL'],
                        vh_part, quote('/'.join(path)))
                else:
                    request['VIRTUAL_URL_PARTS'] = vup = (
                        request['SERVER_URL'], quote('/'.join(path)))
                request['VIRTUAL_URL'] = '/'.join(vup)

                # new ACTUAL_URL
                add = (path and
                       request['ACTUAL_URL'].endswith('/')) and '/' or ''
                request['ACTUAL_URL'] = request['VIRTUAL_URL'] + add

            return
        vh_used = 1 # Only retry once.
        # Try to apply the host map if one exists, and if no
        # VirtualHost directives were found.
        host = request['SERVER_URL'].split('://')[1].lower()
        hostname, port = (host.split( ':', 1) + [None])[:2]
        ports = self.fixed_map.get(hostname, 0)
        if not ports and self.sub_map:
            get = self.sub_map.get
            while hostname:
                ports = get(hostname, 0)
                if ports:
                    break
                if '.' not in hostname:
                    return
                hostname = hostname.split('.', 1)[1]
        if ports:
            pp = ports.get(port, 0)
            if pp == 0 and port is not None:
                # Try default port
                pp = ports.get(None, 0)
            if not pp:
                return
            # If there was no explicit VirtualHostRoot, add one at the end
            if pp[0] == '/':
                pp = pp[:]
                pp.insert(1, self.id)
            stack.extend(pp)

VirtualHostMonster.__call__ = __call__