portal = context.getPortalObject()
portal_preferences = portal.portal_preferences

fluentbit_host = portal_preferences.getPreference('fluentd_gateway_host')
fluentbit_port = portal_preferences.getPreference('fluentd_gateway_port')

fluentbit_config = (
  "[SERVICE]\n"
  "    flush           5\n"
  "[INPUT]\n"
  "    name            tail\n"
  "    path            </path/to/enb.xlog>\n"
  "    tag             %s\n"
  "    Read_from_Head  True\n"
  "    db              </path/to/db>\n"
  "    Buffer_Max_Size 1M\n"
  "[OUTPUT]\n"
  "    name            forward\n"
  "    match           *\n"
  "    Host            %s\n"
  "    Port            %s\n"
  "    Self_Hostname   <hostname>\n"
  "    Retry_Limit     50\n"
  "    tls             on\n"
  "    tls.verify      off"
) % (virtual_ors_tag, fluentbit_host, fluentbit_port)
return fluentbit_config
