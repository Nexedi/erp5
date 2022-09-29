"""
Implementation of a highly sophisticated security system. Context has a security classification
like "personal/project", "collaborative/public" etc and we check if a given policy or a set of
policies (defined with wildcard, like "personal/*" or "*/project") applies to the context.

Classification has to have two levels, and first level is translated into a selected second-level
classification.

Some classifications require something more to apply (like */project requires follow_up), but
this check can be skipped by setting membershiponly to True.
"""

klass = context.getClassification()
if klass is None: return False
kl = klass.split('/')
if len(kl) == 1:
  # personal = personal/restricted
  if kl[0] == 'personal': kl.append('restricted')
  # collaborative = collaborative/team
  if kl[0] == 'collaborative': kl.append('team')

# personal/restricted is unconditional
if kl == ['personal,restricted']:
  return policy == 'personal/restricted'

pol = policy.split('/')

if not membershiponly:
  # project policies do not apply if we don't have follow_up
  if pol[1] == 'project':
    if context.getFollowUp() == None:
      return False

if len(pol) >= 2 and len(kl) >= 2:
  # if all conditions are met, check if the policy is ok (wildcards are ok)
  return (pol[0] in ('*', kl[0])) and (pol[1] in ('*', kl[1]))

return False
