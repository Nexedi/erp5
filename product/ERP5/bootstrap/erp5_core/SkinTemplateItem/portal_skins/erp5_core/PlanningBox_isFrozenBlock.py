# Define the condition for the bloc is frozen or not.
# The Bloc is frozen when:
# - it's a Simulation Movement
# - The user is not allowed to edit it
# - it's a part of a block
# - the object is from secondary layer

return (not context.portal_membership.checkPermission('Modify portal content', block.parent_activity.object)) or \
            (block.property_dict['sec_layer']) or \
            (not ((block.position_x.relative_begin > 0) and \
                   (block.position_x.relative_end < 1) and \
                   (block.property_dict['stat'] == 0)))
