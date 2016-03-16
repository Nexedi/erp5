""" Rename pad on server.
"""
pad = context.restrictedTraverse(knowledge_pad_relative_url)
pad.setTitle(knowledge_pad_title)
