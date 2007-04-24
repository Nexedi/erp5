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
                      'Product', 'Assortiment', 'Service', 'Currency',
                      'Component')

portal_variation_type_list = ('Variation', 'Variante Tissu', 'Variante Modele',
                       'Variante Composant', 'Variante Gamme', 'Variante Morphologique')

portal_node_type_list = ('Organisation','Person','Category','MetaNode',
    'Account')

portal_payment_node_type_list = ('Bank Account', 'Credit Card', )

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
                      'Inventory',
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

portal_transformation_type_list = (
                      'Transformation',
)

portal_variation_base_category_list = ('coloris', 'taille', 'variante', 'morphologie')
portal_option_base_category_list = ('industrial_phase',)

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
                      'Purchase Order Cell',
                      'Sales Order Line',
                      'Sale Order Line',
                      'Sale Order Cell',
                      'Project Line',
                      'Sample Order Line',
                      'Production Order Line',
                      'Production Order Cell',
                      'Production Packing List Line',
                      'Production Report Line',
                      'Production Report Cell',
                      'Packing Order Line',
                      'Delivery Cell',
                       )  # Delivery Cell is both used for orders and deliveries XXX

portal_accounting_transaction_type_list = (
                      'Accounting Transaction',
                      'Sale Invoice Transaction',
                      'Purchase Invoice Transaction',
                      'Payment Transaction',
                      'Pay Sheet Transaction',
                      'Amortisation Transaction')

portal_accounting_movement_type_list = (
                      'Purchase Invoice Transaction Line',
                      'Sale Invoice Transaction Line',
                      'Pay Sheet Transaction Line',
                      'Accounting Transaction Line',
                      'Balance Transaction Line',
                      'Amortisation Transaction Line'
                      )

portal_delivery_movement_type_list = (
                      'Delivery Line',
                      'Delivery Cell',
                      'Purchase Packing List Line',
                      'Purchase Packing List Cell',
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
                      'Sale Packing List Cell',
                      'Production Report Component',
                      'Production Report Operation',
                      'Production Report Line',
                      'Production Report Cell',
                      'Production Packing List Line',
                      'Production Packing List Cell',
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

portal_supply_type_list = ('Purchase Supply','Sale Supply')

portal_supply_path_type_list = ('Supply Line','Supply Cell')

# This transaction lines are special because destination must be None.
portal_balance_transaction_line_type_list = ('Balance Transaction Line',)

## Default Order of base_category in Columns and Lines
# Goal: always show information the same way
# Rule: always try to represent a variation the same way
# Possible Improvement: use order as priority. If twice in column, movement least priority to tab
portal_column_base_category_list = ('taille', )
portal_line_base_category_list = ('coloris', 'couleur', )
portal_tab_base_category_list = ('morphologie', )

# Accounting defaults values
portal_default_gap_root = 'gap/france/pcg'

# Security default values: a list of base categories which security groups are based on
# WARNING: order must be consistent with Portal Types Roles Definitions.
portal_assignment_base_category_list = ['site', 'group', 'function']

portal_draft_order_state_list =  ('cancelled', 'draft', 'auto_planned' )
portal_planned_order_state_list =  ('planned', 'ordered', )

portal_future_inventory_state_list = ('planned', 'ordered',)
portal_transit_inventory_state_list = ()
portal_reserved_inventory_state_list = ('confirmed', 'getting_ready', 'ready')
portal_current_inventory_state_list = ('delivered', 'started', 'stopped', 'invoiced')
# invoiced is Coramy specific and should be removed

portal_updatable_amortisation_transaction_state_list = ('draft',)
