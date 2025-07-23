portal = context.getPortalObject()

portal.data_stream_module.setIdGenerator('_generatePerNodeId')
portal.data_array_module.setIdGenerator('_generatePerNodeId')
portal.data_analysis_module.setIdGenerator('_generatePerNodeId')
portal.data_descriptor_module.setIdGenerator('_generatePerNodeId')
