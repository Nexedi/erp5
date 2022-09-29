"""

 To extend your current ERP5Site_getJavaScriptRelativeUrlList,
 first, find ERP5Site_getJavaScriptRelativeUrlList,
 then put 'erp5_datepicker_ui.js' at the last.

 The following is an example. To enable datepicker, you must include
 'erp5_datepicker_ui.js' in the list.

"""
js_list = ('jquery/core/jquery.min.js', 'erp5.js', 'erp5_datepicker_ui.js')
return js_list
