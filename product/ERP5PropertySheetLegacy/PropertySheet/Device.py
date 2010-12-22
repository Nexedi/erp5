##############################################################################
#
# Copyright (c) 2003 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
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



class Device:
    """
        Device class stores informations on a general network Device
        with one network interface
    """

    _properties = (
        {   'id'          : 'hostname',
            'description' : 'Hostname',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'ip_address',
            'description' : 'IP Address',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'netmask',
            'description' : 'Netmask',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'netmask_bits',
            'description' : 'Netmask Bits',
            'type'        : 'int',
            'mode'        : '' },
        {   'id'          : 'network_address',
            'description' : 'Network Address',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'broadcast_address',
            'description' : 'Broadcast Address',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'dns_server_ip_address',
            'description' : 'DNS Server IP Address',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'gateway_ip_address',
            'description' : 'Gateway IP Address',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'ppp_user',
            'description' : 'PPP User Login',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'ppp_password',
            'description' : 'PPP User Password',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'wlan_wep_key',
            'description' : 'WLAN Wep Key',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'wlan_essid',
            'description' : 'WLAN EssID',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'wlan_channel',
            'description' : 'WLAN Channel',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'ipsec_extra_config',
            'description' : 'IPSec Extra Config',
            'type'        : 'text',
            'mode'        : '' },
        {   'id'          : 'network_interface',
            'description' : 'Network Interface',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'network_type',
            'description' : 'Network Type',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'connection_type',
            'description' : 'Connection Type',
            'type'        : 'string',
            'mode'        : '' },
        {   'id'          : 'modem_type',
            'description' : 'Modem Type',
            'type'        : 'string',
            'mode'        : '' }
    )
