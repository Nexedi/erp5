return [brain
        for brain in context.portal_selections.getSelectionValueList(context=context,
                                                selection_name= 'production_order_module_selection')
        if brain.getStartDate() is not None and brain.getStopDate() is not None]
