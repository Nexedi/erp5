"""This script is a placeholder for projects to implement extra constraint to prevent grouping of accounting transaction lines.
Note that the sequence of letters will still remain unique for section, mirror_section and node, regardless of extra grouping parameters.

For instance, we can refuse to group together lines for different order by returning the reference of the order in that script.

The returned value must be hashable.
"""

# By default we take into account ledger and mirror accounting.

# We consider ledger so that, by default we don't group lines from different ledger.
# This may be customized too, depending on how ledgers are used in customized implementations.

# We consider mirror accounting because that when using internal accounting transaction between
# two entities of the group, the grouping has to be valid for both sides
# (source_section & destination_section).
# This behavior was introduced in nexedi/erp5@f3bebea3 for compatibility,
# some old sites where accounting lines have been grouped together regardless of
# the mirror node can decide to ignore the mirror account.
# Maybe to ignore mirror account for transactions created before the date they
# deployed this new versions.
# This can be achieved easily by customizing this script.

if source:
  return context.getLedger(), context.getSource(portal_type='Account')
return context.getLedger(), context.getDestination(portal_type='Account')
