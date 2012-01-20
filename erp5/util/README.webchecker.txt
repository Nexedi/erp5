Utility able to call wget and varnishlog to extract Headers and return all failures
according expected caching policy.

This utility is configurable through a configuration file like:

[web_checker]
url = http://www.example.com/
working_directory = /home/me/tmp/crawled_content
varnishlog_binary_path = varnishlog
email_address = me@example.com
smtp_host = localhost
debug_level = debug

[header_list]
Last-Modified = True
Cache-Control = max-age=300
                max-age=3600
Vary = Accept-Language, Cookie, Accept-Encoding
       Accept-Language, Cookie
       Accept-Language,Cookie,Accept-Encoding
       Accept-Language,Cookie
Expires = True

[header url=.*/sitemap]
Last-Modified = True

[header content-type=.*/javascript]
Last-Modified = True
Cache-Control = max-age=3600
Expires = True

[no_header content-type=(image/.*|text/css)]
Vary = None

[erp5_extension_list]
prohibited_file_name_list = WebSection_viewAsWeb
                            Base_viewHistory
                            list
prohibited_folder_name_list = web_page_module
                              document_module



with
  url : website to check
  working_directory : fetched data will be downloaded
  varnishlog_binary_path :  path to varnishlog
  email_address : email address to send result
  smtp_host : smtp host to use
  debug_level : log level of this utility (debug =>very verbose,
                                          info=>normal,
                                          warning=>nothing)

  header_list : Key == Header id.
                value: if equals to True, it means that header needs to be present in RESPONSE
                      if it is a tuple, the Header value must sastify at least one of the proposed values

  erp5_extension_list: Optional section.
    prohibited_file_name_list: which check that any links redirect to prohibited forms
      like WebSection_viewAsWeb, Base_viewHistory, list, ...
    prohibited_folder_name_list: usefull to detect that links does not redirect to
      specified modules like, web_page_module, document_module, ...


This utility requires wget => 1.12
And a callable varnishlog.
The utility must be run on same server where varnish is running.

web_checker reads varnishlogs to detect if a Query goes to the backend.
