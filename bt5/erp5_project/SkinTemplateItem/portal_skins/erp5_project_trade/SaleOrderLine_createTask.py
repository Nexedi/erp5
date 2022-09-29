#print kw
#return printed

task = context.task_module.newContent(
                                      portal_type='Task',
                                      title=title,
                                      reference=reference,
                                      source=source,
                                      source_section=source_section,
                                      destination_decision=destination_decision,
                                      destination_section=destination_section,
                                      source_project=source_project,
                                      destination=destination,
                                      start_date=start_date,
                                      stop_date=stop_date,
                                      task_line_resource=task_line_resource,
                                      task_line_quantity=task_line_quantity,
                                      task_line_price=task_line_price,
                                      task_line_quantity_unit=task_line_quantity_unit,
                                      price_currency=price_currency,
                                      description=description,
                                     )
translateString = context.Base_translateString
portal_status_message = translateString("Object created.")
return task.Base_redirect('view',
          keep_items = dict(portal_status_message=portal_status_message),)
