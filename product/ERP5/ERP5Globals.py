##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

default_section_category = 'group/Coramy'

resource_type_list = ('Resource', 'MetaResource', 'Composant', 'Tissu',
                      'Modele', 'Category', 'Gamme', 'Forme', 'Vetement',
                      'Product', 'Assortiment', 'Service')

variation_type_list = ('Variation', 'Variante Tissu', 'Variante Modele',
                       'Variante Composant', 'Variante Gamme', 'Variante Morphologique')

node_type_list = ('Organisation','Person','Category','MetaNode',)

invoice_type_list = ('Invoice', 'Sale Invoice', 'Sales Invoice', 'Sale Invoice Transaction')

order_type_list = ('Order', 'Project', 'Samples Order',
                   'Packing Order','Production Order', 'Purchase Order', 'Sale Order',
                   'Sales Order', )

delivery_type_list = ('Delivery',
                      'Transaction',
                      'Packing List',
                      'Sales Packing List',
                      'Sale Packing List',
                      'Purchase Packing List',
                      'Inventory MP',
                      'Inventory PF',
                      'Movement MP',
                      'Movement PF',
                      'Accounting Transaction',
                      'Purchase Invoice Transaction',
                      'Sale Invoice Transaction',
                      'Production Packing List',
                      'Production Report',
                      )

order_or_delivery_type_list = tuple(list(order_type_list) + list(delivery_type_list))

variation_base_category_list = ('coloris', 'taille', 'variante', 'morphologie')
variation_base_category_id_list = variation_base_category_list # Temp Patch

# Invoice "movement" is not an accountable movement
# Accountable movements of invoices are of type Accounting Transaction Line
invoice_movement_type_list = (
                      'Invoice Line',
                      'Invoice Cell',
                      )

order_movement_type_list = (
                      'Purchase Order Line',
                      'Sales Order Line',
                      'Sale Order Line',
                      'Sample Order Line',
                      'Production Order Line',
                      'Packing Order Line',
                      'Delivery Cell',
                       )  # Delivery Cell is both used for orders and deliveries XXX

delivery_movement_type_list = (
                      'Delivery Line',
                      'Delivery Cell',
                      'Purchase Packing List Line',
                      'Sales Packing List Line',
                      'Purchase Invoice Transaction Line',
                      'Sale Invoice Transaction Line',
                      'Accounting Transaction Line',
                      'Inventory Line',
                      'Inventory Cell',
                      'Inventory MP Line',
                      'Inventory PF Line',
                      'Movement MP Line',
                      'Movement PF Line',
                      'Purchase Packing List Line',
                      'Sales Packing List Line',
                      'Production Report Component',
                      'Production Report Operation',
                      'Production Report Cell',
                      'Production Packing List Line',
                      'Container Line',
                      'Container Cell'
                       )

order_or_delivery_or_invoice_movement_type_list = tuple(list(order_movement_type_list) + \
                           list(delivery_movement_type_list) + \
                           list(invoice_movement_type_list)
                          )

invoice_or_invoice_movement_type_list = tuple(list(invoice_type_list) + \
                           list(invoice_movement_type_list)
                          )

acquisition_movement_type_list = order_or_delivery_or_invoice_movement_type_list

movement_type_list = tuple(list(order_movement_type_list) + \
                           list(delivery_movement_type_list) + \
                           ['Simulation Movement']
                          )

simulated_movement_type_list = tuple(filter(lambda x: x != 'Container Line' and x != 'Container Cell',
                                            movement_type_list))

container_type_list = ('Container',)

item_type_list = ('Piece Tissu',)

discount_type_list = ('Remise',)

# Bellow, we only use order_or_delivery_movement_type_list for movements
# Since we simulation only acquires from orders or deliveries
movement_or_order_type_list = tuple(list(acquisition_movement_type_list) + list(order_type_list))
movement_or_delivery_type_list = tuple(list(acquisition_movement_type_list) + list(delivery_type_list))
movement_or_delivery_or_order_type_list = tuple(list(acquisition_movement_type_list)
                                              + list(delivery_type_list) + list(order_type_list))
movement_or_delivery_or_order_or_invoice_type_list = tuple(list(acquisition_movement_type_list)
                                              + list(delivery_type_list) + list(order_type_list)
                                              + list(invoice_type_list))
movement_or_item_or_delivery_or_order_type_list = tuple(list(acquisition_movement_type_list)
                                              + list(delivery_type_list) + list(order_type_list)
                                              + list(item_type_list))
movement_or_item_or_delivery_or_order_or_invoice_type_list = tuple(list(acquisition_movement_type_list)
                                              + list(delivery_type_list) + list(order_type_list)
                                              + list(invoice_type_list)
                                              + list(item_type_list))

movement_or_item_or_delivery_or_order_or_resource_type_list= tuple(list(acquisition_movement_type_list)
                                              + list(delivery_type_list) + list(order_type_list)
                                              + list(item_type_list)
                                              + list(resource_type_list))

movement_or_item_or_delivery_or_order_or_invoice_or_resource_type_list= \
                                                tuple(list(acquisition_movement_type_list)
                                              + list(delivery_type_list) + list(order_type_list)
                                              + list(invoice_type_list)
                                              + list(item_type_list)
                                              + list(resource_type_list))

## Inventory States

current_inventory_state_list = ('delivered', 'started', 'stopped', 'invoiced') # invoiced is Coramy specific and should be removed
draft_order_state =  ('cancelled', 'draft', 'auto_planned' )
planned_order_state =  ('planned', 'ordered', )
reserved_inventory_state_list = ('confirmed', 'getting_ready', 'ready')
future_inventory_state_list = ('planned', 'ordered',)

## Default Order of base_category in Columns and Lines
# Goal: always show information the same way
# Rule: always try to represent a variation the same way
# Possible Improvement: use order as priority. If twice in column, movement least priority to tab
column_base_category_list = ('taille', )
line_base_category_list = ('coloris', 'couleur', )
tab_base_category_list = ('morphologie', )

