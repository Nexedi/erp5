"""
Short description:

  This script is able to aggregate form groups automaticcaly, according our own
  rules. This is required to do custom xhtml layout for which a flat rendering
  of groups doesn't work.


Detailed description:

  Actually, without this script, fields groups of the ERP5 form used for layout
  are rendered in a flat way like this:

    <html>
      <body>

        <div class="group1" id="group1">
          <div class="field" id="field10">(...)</div>
          <div class="field" id="field11">(...)</div>
          <div class="field" id="field12">(...)</div>
          (...)
        </div>

        <div class="group2" id="group2">
          <div class="field" id="field20">(...)</div>
          <div class="field" id="field21">(...)</div>
          (...)
        </div>

        <div class="group3" id="group3">
          <div class="field" id="field30">(...)</div>
          (...)
        </div>

        (...)

      </body>
    </html>

  This job is done by the erp5_web_default_template Page Template. The output
  is pure flat xhtml which, thanks to the default css file
  (erp5_web_default.css), is rendered as a "3-column + 1 footer" layout with
  ordered content (= main content is at the top of the page, which is a good SEO
  trick).

  But sometimes we need to do more complex layouts and those layout cannot be
  built via pure css on top of flat xhtml div like above. Instead, we need <div>
  wrappers with some level depth to control finely the box model of the page.

  Here is were this script help us solve the problem: it is able to aggregate
  some fields groups according our own rules. Then, the returned aggregation is
  rendered with wrapper to make custom layouts.

  To avoid performance issues, this script must respect the constraint of 1-pass
  parsing of the group list to generate the group structure.


Rules:

  1 - If the group id don't match any group_by_criterion string, the group will
      be added in the last aggregate (see 'footer' group in exemple below).
  2 - A group can't be in two differrent aggregate (no duplicate).
  3 - group_by_criterion parameter is ordered and the returned dict respect that
      order.
  4 - If multiples criterion match one group, the first matched criterion will be
      applied (see 'bottom right' in the exemple below, where it's in the 'bottom'
      aggregate and not in 'right' one).
  5 - This script is compatible with group titles set in parenthesis (handled by
      Form_getGroupTitleAndId script): the matching process will
      ignore the group title (look at '(Discount on Right Handed Tools) left
      discount').
  6 - Matching process between criterion and group id is not case sensitive.
  7 - Group naming should respect naming convention (everything in lower case for
      id and classe, no special char (only ascii and numbers), nything allowed as
      title, is classes separated by spaces).

  -> TODO: implement naming convention test.


Example:

  Form group list:
    * left column
    * left ad
    * (Discount on Right Handed Tools) left discount
    * metadata right
    * right ad
    * bottom content
    * footer
    * bottom right

  Script parameter:
    group_by_criterion = ['left', 'right', 'center', 'bottom']

  Returned data:
    [ ['left',   [ ('left column', 'left column', 'left column')
                 , ('left ad', 'left ad', 'left ad')
                 , ('left discount', 'Discount on Right Handed Tools', '(Discount on Right Handed Tools) left discount')
]]
    , ['right',  [ ('metadata right', 'metadata right', 'metadata right')
                 , ('right ad', 'right ad', 'right ad')
]]
    , ['center', [
]]
    , ['bottom', [ ('bottom content', 'bottom content', 'bottom content')
                 , ('footer', 'footer', 'footer')
                 , ('bottom right', 'bottom right', 'bottom right')
]]
]


Tips:

  * The returned list structure is designed to let you cast it as dict() if you don't
    care about group aggregate ordering. This can help you to get group aggregate
    more easily in table based HTML layouts.

"""


aggregate_list = []  # Returned data structure

if not len(group_by_criterion):
  return aggregate_list

aggregate_dict = {}  # Temporary data structure for easy grouping
layout_form = context

# Initialize aggregate dict
for criterion in group_by_criterion:
  aggregate_dict[criterion] = []

# Get the cached list of groups and titles
for group_details in layout_form.Form_getGroupTitleAndId():                   # Rule (5)
                                                                              # Rule (2)
  group_css_classes = group_details['gid']

  # Do not display hidden group
  if group_css_classes == 'hidden':
    continue

  # Criterion matching status
  matched = False

  # Parse the string from left to right
  for group_class in group_css_classes.lower().split(' '):                    # Rule (6) & (7)
    # Let criterion match group
    if group_class in group_by_criterion:
      # Put the group in the right aggregate
      aggregate_dict[group_class] = aggregate_dict[group_class] + [group_details]
      matched = True
      break                                                                   # Rule (4)

  if not matched:                                                             # Rule (1)
    # No 'group by' criterion found in group id, so put it in the last one
    last_aggregate = group_by_criterion[-1]
    aggregate_dict[last_aggregate] = aggregate_dict[last_aggregate] + [group_details]


# Reorder the list                                                            # Rule (3)
for criterion in group_by_criterion:
  aggregate = [ criterion
              , aggregate_dict[criterion]
]
  aggregate_list.append(aggregate)


return aggregate_list
