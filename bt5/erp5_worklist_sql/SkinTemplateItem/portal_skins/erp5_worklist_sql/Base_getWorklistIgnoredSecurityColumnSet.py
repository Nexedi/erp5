# Be careful when returning column names here.
# A legitimate use case is when you have a lot of users (ex: customer accounts)
# *and* the number of rows in your worklist table is proportional to the number
# of such users *and* such users will not see worklists.
# If you ignore all security columns, no security will be applied anymore on
# worklist listing (document security will of course still apply).
return ()
