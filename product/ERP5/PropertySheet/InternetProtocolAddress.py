##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Yusei TAHARA <yusei@nexedi.com>
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


class InternetProtocolAddress:
    """
        Information about IP address
	(used by yet to add InternetProtocolAddress which is like a Phone / Address
	please review following what mandriva in sysconfig 
	
	dhcp must be handled maybe with category
    """

    _properties = (
        {   'id'          : 'host_name',
            'description' : 'Hostname',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'ip_address',
            'description' : 'IP Address',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'netmask',
            'description' : 'Netmask',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'netmask_bit',
            'description' : 'Netmask Bits',
            'type'        : 'int',
            'mode'        : 'w' },
        {   'id'          : 'network_address',
            'description' : 'Network Address',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'broadcast_address',
            'description' : 'Broadcast Address',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'dns_server_ip_address',
            'description' : 'DNS Server IP Address',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'gateway_ip_address',
            'description' : 'Gateway IP Address',
            'type'        : 'string',
            'mode'        : 'w' },
        {   'id'          : 'network_interface',
            'description' : 'Network Interface',
            'type'        : 'string',
            'mode'        : 'w' },
    )
