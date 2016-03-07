"""Initialize an unique codification on project, because projects are often used as security group.
"""
codification = context.getPortalObject().portal_ids.generateNewId(id_group='project.codification', id_generator='uid', default=1)
context.setCodification('PROJ-%s' % codification)
