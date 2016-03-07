portal = context.getPortalObject()

repository = portal.getPromiseParameter('portal_templates', 'repository')
portal.portal_templates.updateRepositoryBusinessTemplateList(repository.split())
