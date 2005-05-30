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

portal_default_section_category = 'group/Coramy'

portal_resource_type_list = ('Resource', 'MetaResource', 'Composant', 'Tissu',
                      'Modele', 'Category', 'Gamme', 'Forme', 'Vetement',
                      'Product', 'Assortiment', 'Service', 'Currency')

portal_variation_type_list = ('Variation', 'Variante Tissu', 'Variante Modele',
                       'Variante Composant', 'Variante Gamme', 'Variante Morphologique')

portal_node_type_list = ('Organisation','Person','Category','MetaNode',)

portal_invoice_type_list = ('Invoice', 'Sale Invoice', 'Sales Invoice', 'Sale Invoice Transaction',
                            'Pay Sheet Transaction')

portal_order_type_list = ('Order', 'Project', 'Samples Order',
                   'Packing Order','Production Order', 'Purchase Order', 'Sale Order',
                   'Sales Order', )

portal_delivery_type_list = ('Delivery',
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
                      'Pay Sheet Transaction',
                      'Purchase Invoice Transaction',
                      'Sale Invoice Transaction',
                      'Production Packing List',
                      'Production Report',
                      'Balance Transaction',
                      'Payment Transaction',
                      'Amortisation Transaction',
                      'Pay Sheet Transaction',
                      'Internal Packing List',
                      )

portal_variation_base_category_list = ('coloris', 'taille', 'variante', 'morphologie')

# Invoice "movement" is not an accountable movement
# Accountable movements of invoices are of type Accounting Transaction Line
portal_invoice_movement_type_list = (
                      'Invoice Line',
                      'Invoice Cell',
                      'Pay Sheet Line',
                      'Pay Sheet Cell',
                      )

portal_order_movement_type_list = (
                      'Purchase Order Line',
                      'Sales Order Line',
                      'Sale Order Line',
                      'Project Line',
                      'Sample Order Line',
                      'Production Order Line',
                      'Packing Order Line',
                      'Delivery Cell',
                       )  # Delivery Cell is both used for orders and deliveries XXX

portal_delivery_movement_type_list = (
                      'Delivery Line',
                      'Delivery Cell',
                      'Purchase Packing List Line',
                      'Sales Packing List Line',
                      'Purchase Invoice Transaction Line',
                      'Sale Invoice Transaction Line',
                      'Pay Sheet Transaction Line',
                      'Accounting Transaction Line',
                      'Inventory Line',
                      'Inventory Cell',
                      'Inventory MP Line',
                      'Inventory PF Line',
                      'Movement MP Line',
                      'Movement PF Line',
                      'Purchase Packing List Line',
                      'Sale Packing List Line',
                      'Production Report Component',
                      'Production Report Operation',
                      'Production Report Cell',
                      'Production Packing List Line',
                      'Container Line',
                      'Container Cell',
                      'Balance Transaction Line',
                      'Internal Packing List Line',
                      'Amortisation Transaction Line'
                       )

portal_container_type_list = ('Container',)

portal_container_line_type_list = ('Container Line',)

portal_item_type_list = ('Piece Tissu','Nexedi VPN')

portal_discount_type_list = ('Remise',)

portal_alarm_type_list = ('Supply Alarm Line','Alarm')

portal_payment_condition_type_list = ('Condition Paiement',)

portal_supply_type_list = ('Supply Line','Supply Cell')

# This transaction lines are special because destination must be None.
portal_balance_transaction_line_type_list = ('Balance Transaction Line',)

## Inventory States

portal_current_inventory_state_list = ('delivered', 'started', 'stopped', 'invoiced') # invoiced is Coramy specific and should be removed
portal_transit_inventory_state_list = ('started',) # This MUST be a subset of portal_current_inventory_state_list, it indicates movements that left the source, but didn't arrive at the destination yet.
portal_target_inventory_state_list = ('ready', 'delivered', 'started', 'stopped', 'invoiced') # if simulation_state in target_list, target_quantity should be considered instead of quantity for stock indexing XXX why do we need two inventory_state_list ?
portal_draft_order_state_list =  ('cancelled', 'draft', 'auto_planned' )
portal_planned_order_state_list =  ('planned', 'ordered', )
portal_reserved_inventory_state_list = ('confirmed', 'getting_ready', 'ready')
# ????
# portal_reserved_inventory_state_list2 = ('ready',)
portal_future_inventory_state_list = ('planned', 'ordered',)

## Default Order of base_category in Columns and Lines
# Goal: always show information the same way
# Rule: always try to represent a variation the same way
# Possible Improvement: use order as priority. If twice in column, movement least priority to tab
portal_column_base_category_list = ('taille', )
portal_line_base_category_list = ('coloris', 'couleur', )
portal_tab_base_category_list = ('morphologie', )

portal_criterion_base_category_list = ('source','destination','resource',
                                       'destination_section','source_section')
portal_mapped_value_property_list = ('start_date','stop_date')
