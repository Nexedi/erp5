"""Returns the dict of parameters that have to be passed to getInventory/getMovementHistoryList
for the cell_index. This script returns parameters even if the cell does not exist.
"""

portal = context.getPortalObject()
budget_model = context.getParentValue().getSpecialiseValue()

budget_cell = context.getCell(*cell_index)

if budget_cell is None:
  # if cell does not exist, use a temporary cell at those coordinates
  budget_cell = context.newContent(portal_type='Budget Cell', temp_object=True)
  budget_cell.edit(
     mapped_value_property_list=('quantity',),
     membership_criterion_base_category_list
        =[bc for bc in context.getVariationBaseCategoryList() if bc not
                in context.getMembershipCriterionBaseCategoryList()],
     membership_criterion_category_list=cell_index)

kw = budget_model.getInventoryQueryDict(budget_cell)

if engaged_budget:
  kw.setdefault('stock_explanation_simulation_state',
                  portal.getPortalReservedInventoryStateList() +
                  portal.getPortalCurrentInventoryStateList() +
                  portal.getPortalTransitInventoryStateList())

# those are simulation state parameters equivalent to getCurrentInventoryQuery that can be passed to getMovementHistoryList
kw.setdefault('simulation_state', portal.getPortalCurrentInventoryStateList() + portal.getPortalTransitInventoryStateList())
kw.setdefault('transit_simulation_state', portal.getPortalTransitInventoryStateList())
kw.setdefault('omit_transit', False)

return kw
