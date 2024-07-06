# Copyright (C) 2005-2009 AG Projects
#

# This file is distributed by AG Projects under the same licence as SOAPpy.
# That licence is (as of release 0.12.0):
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#  Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  Neither the name of actzero, inc. nor the names of its contributors may
#  be used to endorse or promote products derived from this software without
#  specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
#  OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
#  DAMAGE.

import weakref

from wstools        import WSDLTools
from SOAPpy.Client  import SOAPProxy
from SOAPpy.Types   import headerType, faultType

##
## Hierarchy of the WSDL elements and how the elements relate to each other
## (if they have one to one or one to many relationship between them):
##
##      1:n          1:n       1:1          1:1           1:n
## WSDL ---> Service ---> Port ---> Binding ---> PortType ---> Operations
##


class Proxy(object):
    """
    WSDL Proxy

    SOAPProxy wrapper that parses method names, namespaces, soap actions from
    the WSDL reference passed into the constructor. The WSDL reference can be
    an URL or a previously obtained WSDL instance (from another proxy).

    Usage example:
        url = 'http://www.example.org/wsdl'

        # Get the `SomePort` port from the first service in the WSDL
        s1 = WSDL.Proxy(url, port='SomePort')

        # Get the `OtherPort` port of the `OtherService` service.
        # Reuse the WSDL obtained before to avoid requesting it again
        # from the SOAP server.
        s2 = WSDL.Proxy(s1._wsdl, service='OtherService', port='OtherPort')

        s1.somefunction()
        s2.otherfunction()
    """

    def __init__(self, wsdl, service=None, port=None, auth=None, **kwargs):
        if not hasattr(wsdl, 'targetNamespace'):
            wsdl = WSDLTools.WSDLReader().loadFromURL(wsdl)


        #auth = auth and headerType({'auth': SoapAuth(auth).SOAPout}) or None
        auth = auth and headerType({'auth': auth}) or None

        self._wsdl = wsdl
        self._service = wsdl.services[service or 0]
        self._port = self._service.ports[port or 0]
        self._name = self._service.name
        self.__doc__ = self._service.documentation
        self._auth   = auth
        self._kwargs = kwargs
        self._trace  = False  ## Dump SOAP input and output to sdtout
        self._simple = True   ## Convert results to python native types

        binding = self._port.getBinding()
        portType = binding.getPortType()
        for operation in portType.operations:
            callinfo = WSDLTools.callInfoFromWSDL(self._port, operation.name)
            method = MethodProxy(self, callinfo)
            setattr(self, operation.name, method)



class MethodProxy(object):
    def __init__(self, parent, callinfo):
        self.__name__ = callinfo.methodName
        self.__doc__ = callinfo.documentation
        self.callinfo = callinfo
        self.parent = weakref.ref(parent)

    def __call__(self, *args, **kwargs):
        parent = self.parent()
        callinfo = self.callinfo
        header = parent._auth
        proxy = SOAPProxy(callinfo.location, header=header, **parent._kwargs)
        proxy.namespace  = callinfo.namespace
        proxy.soapaction = callinfo.soapAction
        proxy.simplify_objects   = parent._simple
        proxy.config.dumpSOAPIn  = parent._trace
        proxy.config.dumpSOAPOut = parent._trace
        proxy.config.dumpHeadersIn  = parent._trace
        proxy.config.dumpHeadersOut = parent._trace
        return proxy.__getattr__(self.__name__)(*args, **kwargs)
