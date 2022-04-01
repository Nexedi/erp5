for builder in sorted(context.getPortalObject().portal_deliveries.contentValues(),
                  key=lambda x:x.getTitle()):
  print(builder.getId())
  print("  Title: %s" % (builder.getTitle()))
  print("  Simulation Select Method: %s" % (builder.getSimulationSelectMethodId()))
  print("  Delivery Select Method: %s" % (builder.getDeliverySelectMethodId()))
  print("  After Generation Script: %s" % (builder.getDeliveryAfterGenerationScriptId()))
  print()

  for mg in sorted(builder.contentValues(), key=lambda x:x.getTitle()):
    print(builder.getId())
    print(" ", "\n  ".join([x for x in (
      "Id: %s" % mg.getId(),
      "Title: %s" % mg.getTitle(),
      "Type: %s" % mg.getPortalType(),
      "Collect Order Group: %s" % mg.getCollectOrderGroup(),
      "Tested Properties: %r" % mg.getTestedPropertyList(),
      "Update Always: %r" % mg.isUpdateAlways(),

      )]))
    print()

return printed
