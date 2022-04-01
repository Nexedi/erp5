for rule in sorted(context.getPortalObject().portal_rules.contentValues(),
                  key=lambda x:x.getTitle()):
  if rule.getValidationState() != 'validated':
    continue
  print(rule.getId())
  print("  Title: %s" % (rule.getTitle()))
  print("  Trade Phases: %r" % (rule.getTradePhaseList()))
  print("  Test Method Id: %s" % (rule.getTestMethodId()))
  print("  Membership Criteria: %r" % (rule.getMembershipCriterionBaseCategoryList()))
  print("  Membership Criterion Category: %r" % (rule.getMembershipCriterionCategoryList()))
  print()

  for tester in sorted(rule.contentValues(), key=lambda x:x.getTitle()):
    print(rule.getId())
    print(" ", "\n  ".join([x for x in (
      "Id: %s" % tester.getId(),
      "Title: %s" % tester.getTitle(),
      "Type: %s" % tester.getPortalType(),
      "Updating: %s" % tester.isUpdatingProvider(),
      "Divergence: %s" % tester.isDivergenceProvider(),
      "Matching: %s" % tester.isMatchingProvider(),

      "Test Method Id: %s" % tester.getTestMethodId(),
      "Membership Criteria: %r" %
        (tester.getMembershipCriterionBaseCategoryList()),
      "Membership Criterion Category: %r" %
        (tester.getMembershipCriterionCategoryList()),
      )]))
    print()

return printed
