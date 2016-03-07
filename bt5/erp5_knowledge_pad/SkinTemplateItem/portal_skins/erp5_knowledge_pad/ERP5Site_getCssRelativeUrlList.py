# This script returns an iterable of the paths to standard CSS objects.
# If you want to customize your own site, please override this script
# in your own skin folder. Note that the returned items must be
# relative URLs instead of absolute URLs, i.e. they must be traversable
# from the portal object. This is required for further processing of CSS
# data, e.g. compression.
#
# BBB: For the history, erp5.css is included by css_list_template.
#      So this script has nothing to do in reality.
css_list = ('erp5_knowledge_box.css',)
return css_list
