# This script returns an iterable of the paths to standard JavaScript objects.
# If you want to customize your own site, please override this script
# in your own skin folder. Note that the returned items must be
# relative URLs instead of absolute URLs, i.e. they must be traversable
# from the portal object. This is required for further processing of JavaScript
# data, e.g. compression.
#
# BBB: For the history, erp5_xhtml_appearance.js is included by default when
#      js_list is not pre-defined before the global definitions.
js_list = ('jquery/core/jquery.min.js', 'jquery/ui/js/jquery-ui.min.js', 'erp5.js', 'erp5_knowledge_box.js', 'erp5_dhtml_style.js','live_test.js')
return js_list
