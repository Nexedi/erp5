##############################################################################
#
# Copyright (c) 2003 Nexedi SARL and Contributors. All Rights Reserved.
#                    Guillaume Michon <guillaume@nexedi.com>
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



class VPN:
    """
        VPN Class stores specific informations on a Nexedi VPN Device
    """

    _properties = (
        {   'id'          : 'external_ip_address',
            'description' : 'External IP address',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'bind_shared_key',
            'description' : 'Bind Shared Key',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'bind_zone',
            'description' : 'Bind Zone',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'bind_records',
            'description' : 'Bind Records',
            'type'        : 'text',
            'mode'        : '' },
        {   'id'          : 'bind_reverse_records',
            'description' : 'Bind Reverse Records',
            'type'        : 'text',
            'mode'        : '' },
        {   'id'          : 'shorewall_rules_extra_config',
            'description' : 'Shorewall Rules Extra Config',
            'type'        : 'text',
            'mode'        : '' },
        {   'id'          : 'root_password',
            'description' : 'Root Password',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'web_password',
            'description' : 'Web Password',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'vpn_type',
            'description' : 'VPN Type',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'bridge_device',
            'description' : 'Bridge Device',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'version',
            'description' : 'OS Version',
            'type'        : 'string',
            'mode'        : '' },
           
            
  
                      
        {   'id'          : 'second_netmask_bits',
            'description' : 'Netmask Bits of Second Interface',
            'type'        : 'int',
            'mode'        : '' },
        {   'id'          : 'second_network_address',
            'description' : 'Network Address of Second Interface',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'second_wlan_wep_key',
            'description' : 'WLAN Key of Second Interface',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'second_wlan_essid',
            'description' : 'WLAN EssID of Second Interface',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'second_wlan_channel',
            'description' : 'WLAN Channel of Second Interface',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'second_network_interface',
            'description' : 'Second Network Interface',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'second_network_type',
            'description' : 'Network Type of Second Interface',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'second_dhcp_range_start',
            'description' : 'DHCP Range Start of Second Interface',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'second_dhcp_range_end',
            'description' : 'DHCP Range End of Second Interface',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'second_dhcp_extra_config',
            'description' : 'DHCP Extra Config of Second Interface',
            'type'        : 'text',
            'mode'        : '' },
        {   'id'          : 'second_dhcp_wlan_port',
            'description' : 'WLAN Port of Second Interface',
            'type'        : 'string',
            'mode'        : '' },
        
            
            
            
        {   'id'          : 'third_netmask_bits',
            'description' : 'Netmask Bits of Third Interface',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'third_network_address',
            'description' : 'Network Address of Third Interface',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'third_network_interface',
            'description' : 'Third Network Interface',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'third_network_type',
            'description' : 'Network Type of Third Interface',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'third_dhcp_range_start',
            'description' : 'DHCP Range Start of Third Interface',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'third_dhcp_range_end',
            'description' : 'DHCP Range End of Third Interface',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'third_dhcp_extra_config',
            'description' : 'DHCP Extra Config of Third Interface',
            'type'        : 'text',
            'mode'        : '' }
  
    )
