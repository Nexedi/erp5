context.REQUEST.RESPONSE.setHeader("Content-Type", "text/html; charset=utf-8")
return "\n".join([str(context.getTitle()),
                  str(context.getShortTitle()),
                  str(context.getDescription()),
                  str(",".join(context.getContributorTitleList())),
                  str(context.getEffectiveDate())])
