/*global window, rJS, RSVP, URL*/
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, URL) {
  "use strict";
  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .allowPublicAcquisition('getUrlFor', function (argument_list) {
      var i;
      if (argument_list[0].command === "index") {
        for (i = 0; i < this.props[argument_list[0].options.list_method_template].data.total_rows; i += 1) {
          if (argument_list[0].options.jio_key === this.props[argument_list[0].options.list_method_template].data.rows[i].id) {
            return this.props[argument_list[0].options.list_method_template].data.rows[i].value.link;
          }
        }
      }
      return this.getUrlFor(argument_list[0]);
    })

    .allowPublicAcquisition('jio_allDocs', function (argument_list) {
      var tmp = argument_list[0].list_method_template,
        i,
        base_url,
        link,
        gadget = this;
      return this.getDeclaredGadget(tmp)
        .push(function (jio_gadget) {
          if (tmp === 'nexedi_blog_jio') {
            link = 'link';
          } else {
            link = 'link_alternate_href';
          }
          argument_list[0].select_list.push(link);
          return jio_gadget.allDocs(argument_list[0]);
        })
        .push(function (result) {
          gadget.props[tmp]  = result;
          for (i = 0; i < gadget.props.rss_list.length; i += 1) {
            if (tmp === gadget.props.rss_list[i].scope) {
              base_url = gadget.props.rss_list[i].url;
            }
          }
          for (i = 0; i < result.data.total_rows; i += 1) {
            if (!/^https?:\/\//i.test(result.data.rows[i].value[link])) {
              result.data.rows[i].value[link] = new URL(result.data.rows[i].value[link], base_url).href;
            }
            if (!result.data.rows[i].value.link) {
              result.data.rows[i].value.link = result.data.rows[i].value[link];
            }
          }
          return result;
        })
        .push(undefined, function (error) {
          //Anonymous User
          if ((error.target !== undefined) && (error.target.status === 403)) {
            //redirect to login page
            //any jio call is fine
            return gadget.jio_getAttachment(
              'portal_workflow',
              'links'
            );
          }
          throw error;
        });
    })
    .allowPublicAcquisition('getUrlParameter', function (argument_list) {
      return this.getUrlParameter(argument_list)
        .push(function (result) {
          if (result === undefined) {
            if (argument_list[0].indexOf('listbox_rss_nexedi_blog_sort_list') !== -1) {
              return [['pubDate', 'descending']];
            }
            return [['updated', 'descending']];
          }
          return result;
        });
    })

    .declareMethod("render", function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {
                "_view": {
                  "listbox_rss_gitlab_erp5": {
                    "column_list": [
                      ['title', 'Title']
                    ],
                    "list_method_template": 'gitlab_erp5_jio',
                    "show_anchor": 0,
                    "default_params": {},
                    "editable": 0,
                    "css_class": 'invisible',
                    "editable_column_list": [],
                    "key": "field_listbox_rss_gitlab_erp5",
                    "lines": 5,
                    "query": 'urn:jio:allDocs?query=__id%3A%20!%3D%20"%2F0"',
                    "portal_type": [],
                    "search_column_list": [],
                    "sort_column_list": [],
                    "title": "Gitlab ERP5",
                    "type": "ListBox"
                  },
                  "listbox_rss_gitlab_slapos": {
                    "column_list": [
                      ['title', 'Title']
                    ],
                    "list_method_template": 'gitlab_slapos_jio',
                    "show_anchor": 0,
                    "default_params": {},
                    "editable": 0,
                    "css_class": 'invisible',
                    "editable_column_list": [],
                    "key": "field_listbox_rss_gitlab_slapos",
                    "lines": 5,
                    "query": 'urn:jio:allDocs?query=__id%3A%20!%3D%20"%2F0"',
                    "portal_type": [],
                    "search_column_list": [],
                    "sort_column_list": [],
                    "title": "Gitlab Slapos",
                    "type": "ListBox"
                  },
                  "listbox_rss_nexedi_blog": {
                    "column_list": [
                      ['title', 'Title']
                    ],
                    "list_method_template": 'nexedi_blog_jio',
                    "show_anchor": 0,
                    "default_params": {},
                    "editable": 0,
                    "css_class": 'invisible',
                    "editable_column_list": [],
                    "key": "field_listbox_rss_nexedi_blog",
                    "lines": 5,
                    "query": 'urn:jio:allDocs?query=__id%3A%20!%3D%20"%2F0"',
                    "portal_type": [],
                    "search_column_list": [],
                    "sort_column_list": [],
                    "title": "Nexedi Blog",
                    "type": "ListBox"
                  }
                }
              },
              "_links": {
                "type": {
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: [
                [
                  "left",
                  [["listbox_rss_gitlab_erp5"], ["listbox_rss_nexedi_blog"]]
                ],
                [
                  "right",
                  [["listbox_rss_gitlab_slapos"]]
                ]
              ]
            }
          });
        });
    })
    .ready(function () {
      var gadget = this,
        i,
        list = [];
      gadget.props = {
        'rss_list': [
          {
            'url': 'https://lab.nexedi.com/nexedi/erp5.atom',
            'parser': 'atom',
            'scope':  'gitlab_erp5_jio'
          },
          {
            'url': 'https://lab.nexedi.com/nexedi/slapos.atom',
            'parser': 'atom',
            'scope':  'gitlab_slapos_jio'
          },
          {
            'url': 'https://www.erp5.com/blog/WebSection_viewContentListAsRSS',
            'parser': 'rss',
            'scope':  'nexedi_blog_jio'
          }
        ]
      };
      for (i = 0; i < gadget.props.rss_list.length; i += 1) {
        list.push(gadget.getDeclaredGadget(gadget.props.rss_list[i].scope));
      }
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all(list);
        })
        .push(function (result_list) {
          list = [];
          for (i = 0; i < gadget.props.rss_list.length; i += 1) {
            list.push(
              result_list[i].createJio({
                type: "query",
                sub_storage: {
                  type: "parser",
                  parser: gadget.props.rss_list[i].parser,
                  sub_storage: {
                    type: "http"
                  },
                  document_id: 'ERP5Site_getHTTPResource?url=' + gadget.props.rss_list[i].url,
                  attachment_id: 'enclosure'
                }
              })
            );
          }
          return RSVP.all(list);
        });
    });
}(window, rJS, RSVP, URL));