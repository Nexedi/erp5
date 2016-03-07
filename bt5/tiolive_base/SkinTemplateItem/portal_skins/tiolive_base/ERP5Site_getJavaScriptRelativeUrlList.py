# This script returns an iterable of the paths to standard JavaScript objects.
# If you want to customize your own site, please override this script
# in your own skin folder. Note that the returned items must be
# relative URLs instead of absolute URLs, i.e. they must be traversable
# from the portal object. This is required for further processing of JavaScript
# data, e.g. compression.
#
# BBB: For the history, erp5_xhtml_appearance.js is included by default when
#      js_list is not pre-defined before the global definitions.

js_list = ('MochiKit/MochiKit.js',
           'erp5_knowledge_box.js',
           'erp5.js',
           'portal_wizard/proxy/web_site_module/express_frame/express_advertisement.js',)
return js_list
