o=state_change['object']
u=o.getUrlString()
i=u.find('://')
if i>-1:
  prot=u[:i]
  if prot not in o.getProtocolList():
    raise ValueError("Protocol "+prot+" not supported")
  o.setUrlString(u[i+3:])
  o.setUrlProtocol(prot)
