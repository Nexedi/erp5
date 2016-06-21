/*globals window, document, RSVP, rJS, Handlebars, promiseEventListener,
          loopEventListener, jQuery, URI, location, console*/
/*jslint indent: 2*/
(function (window, document, RSVP, rJS, Handlebars, promiseEventListener,
           $) {
  "use strict";

  $.mobile.ajaxEnabled = false;
  $.mobile.linkBindingEnabled = false;
  $.mobile.hashListeningEnabled = false;
  $.mobile.pushStateEnabled = false;

  var hateoas_url = "hateoas/",
    PAGE_LIST = "list",
    PAGE_NEW_EXPENSE_REPORT = "new_expense_report",
    PAGE_CONNECTION = "connect",
    PAGE_LOGOUT = "logout",
    PAGE_SYNC = "sync",
    PAGE_VIEW_EXPENSE_REPORT = "view",
    DEFAULT_PAGE = PAGE_LIST,
    query = 'portal_type:"Data Stream" OR portal_type:"Data Set" OR \
      portal_type:"Data Supply" OR portal_type:"Data Acquisition Unit" OR \
      portal_type:"Data Aggregation Unit" OR portal_type:"Data Analysis" OR \
      portal_type:"Data Array" OR portal_type:"Data Ingestion" OR \
      portal_type:"Data License" OR portal_type:"Data Operation" OR \
      portal_type:"Data Product" OR portal_type:"Data Release" OR \
      portal_type:"Data Set" OR portal_type:"Ingestion Policy" OR \
      portal_type:"Sensor"';

  //////////////////////////////////////////
  // History Support with Jio
  //////////////////////////////////////////
  function createJio(gadget) {
    return gadget.getDeclaredGadget("jio_gadget")
      .push(function (jio_gadget) {
        return jio_gadget.createJio({
          type: "replicate",
          query: {query: query, limit: [0, 1234567890]},
          use_remote_post: true,
          local_sub_storage: {
            type: "query",
            sub_storage: {
              type: "uuid",
              sub_storage: {
                type: "indexeddb",
                database: "erp5js_test60"
              }
            }
          },
          remote_sub_storage: {
            type: "erp5",
            url: (new URI(hateoas_url)).absoluteTo(location.href).toString(),
            default_view_reference: "view"
          }
        });

      });
  }

  //////////////////////////////////////////
  // Page rendering
  //////////////////////////////////////////
  function redirectToDefaultPage(gadget) {
    // Redirect to expected page by default
    return gadget.aq_pleasePublishMyState({page: DEFAULT_PAGE})
      .push(gadget.pleaseRedirectMyHash.bind(gadget));
  }

  function renderSynchroPage(gadget) {
    return new RSVP.Queue()
      .push(function () {
        return gadget.aq_pleasePublishMyState({page: PAGE_LOGOUT});
      })
      .push(function (url) {
        gadget.props.header_element.innerHTML = gadget.props.header_template({
          title: "Synchronize"
        });
        gadget.props.content_element.innerHTML =
          gadget.props.synchro_template({});
        $(gadget.props.element).trigger("create");
        return promiseEventListener(
          gadget.props.content_element.querySelector('form.synchro-form'),
          'submit',
          false
        );
      })
      .push(function () {
        gadget.props.content_element.querySelector("input[type=submit]")
                                 .disabled = true;
        return gadget.getDeclaredGadget("jio_gadget");
      })
      .push(function (jio_gadget) {
        // XXX improve later
        gadget.props.header_element.innerHTML = gadget.props.sync_loader_template({
          title: "Synchronize"
        });
          
        // ivan dump to json dict
        //jio_gadget.allDocs(query = query).push(function (response) {
        //  console.log(response.data.total_rows);
        //  for (i = 0; i < response.data.total_rows; i += 1) {
        //    console.log(response.data.rows[i].value.description);
        //  }
        //});
        // eof ivan

        return jio_gadget.repair()
          .push(function () {
            return redirectToDefaultPage(gadget);
          }, function (error) {
            // XXX improve later
            gadget.props.header_element.innerHTML = gadget.props.header_template({
              title: "Synchronize"
            });
            if (error.target !== undefined) {
              if (error.target.status === 401) {
                // Redirect to the login view
                return gadget.aq_pleasePublishMyState({page: PAGE_CONNECTION})
                  .push(gadget.pleaseRedirectMyHash.bind(gadget));
              }
              if (error.target.status === 0) {
                // No network?
                gadget.props.content_element.innerHTML = "Can not sync";
                $(gadget.props.element).trigger("create");
                return;
              }
            }
            throw error;
          });
      })
      .push(function () {
        // XXX improve later
        gadget.props.header_element.innerHTML = gadget.props.header_template({
          title: "Synchronize"
        });
      });
  }

  function renderDocumentListPage(gadget) {
    var documentlist = [];
    return gadget.getDeclaredGadget("jio_gadget")
      .push(function (jio) {
        return RSVP.all([
          gadget.aq_pleasePublishMyState({page: PAGE_SYNC}),
          gadget.aq_pleasePublishMyState({page: PAGE_NEW_EXPENSE_REPORT}),
          jio.allDocs({query: query, 
            sort_on: [["reference", "ascending"]], 
            select_list: ["reference", "description", "title", 
                          "portal_type"], 
            limit: [0, 10000000]})
        ]);
      })
      .push(function (result_list) {
        var i,
          promise_list = [],
          result = result_list[2];
        for (i = 0; i < result.data.total_rows; i += 1) {
          documentlist.push({
            description: result.data.rows[i].value.description,
            reference: result.data.rows[i].value.reference,
            title: result.data.rows[i].value.title,
            portal_type: result.data.rows[i].value.portal_type
          });
          if (!result.data.rows[i].value.reference) {
            delete documentlist[documentlist.length - 1].reference;
          }
          promise_list.push(
            gadget.aq_pleasePublishMyState({page: PAGE_VIEW_EXPENSE_REPORT, key: result.data.rows[i].id})
          );
        }
        gadget.props.header_element.innerHTML = gadget.props.header_template({
          title: "Data Stream",
          right_url: result_list[1],
          right_title: "New"
        });
        return RSVP.all(promise_list);
      })
      .push(function (result_list) {
        var i, json_dict = [];
        //console.log(documentlist);
        for (i = 0; i < result_list.length; i += 1) {
          documentlist[i].url = result_list[i];
          //add to json_dict
          json_dict[i] = JSON.stringify(
                         {'title': documentlist[i].title,
                          'relative_url': documentlist[i].relative_url,
                          'portal_type': documentlist[i].portal_type,
                          'description': documentlist[i].description});
        }
        gadget.props.content_element.innerHTML =
          gadget.props.document_list_template({
            document_list: documentlist,
            json_dict: json_dict,
            // XXX Hardcoded
            sync_url: "#page=sync"
          });
        $(gadget.props.element).trigger("create");
      });
  }

  function renderConnectPage(gadget) {
    return new RSVP.Queue()
      .push(function () {
        gadget.props.header_element.innerHTML = gadget.props.header_template({
          title: "Connect"
        });
        gadget.props.content_element.innerHTML =
          gadget.props.login_template({});
        $(gadget.props.element).trigger("create");
        gadget.props.content_element.querySelector("input[type=text]")
                                 .focus();
        gadget.props.content_element.querySelector("input[type=text]")
                                 .select();
        return promiseEventListener(
          gadget.props.content_element.querySelector('form.login-form'),
          'submit',
          false
        );
      })
      .push(function (evt) {
        gadget.props.content_element.querySelector("input[type=submit]")
                                 .disabled = true;
        var login = evt.target.elements[0].value,
          passwd = evt.target.elements[1].value;
        document.cookie = "__ac=" + window.btoa(login + ":" + passwd) + "; path=/";
        return redirectToDefaultPage(gadget);
      });
  }

  function renderLogoutPage(gadget) {
    return new RSVP.Queue()
      .push(function () {
        gadget.props.header_element.innerHTML = gadget.props.header_template({
          title: "Logout"
        });
        gadget.props.content_element.innerHTML =
          gadget.props.logout_template({});
        $(gadget.props.element).trigger("create");
        return promiseEventListener(
          gadget.props.content_element.querySelector('form.logout-form'),
          'submit',
          false
        );
      })
      .push(function () {
        gadget.props.content_element.querySelector("input[type=submit]")
                                 .disabled = true;
        document.cookie = "__ac=; path=/";
        return redirectToDefaultPage(gadget);
      });
  }

  function renderNewExpenseReportPage(gadget) {
    gadget.props.header_element.innerHTML = gadget.props.header_template({
      title: "New Data Stream"
    });
    gadget.props.content_element.innerHTML =
      gadget.props.new_expense_report_template({});
    $(gadget.props.element).trigger("create");

    gadget.props.content_element.querySelector("input[type=text]")
                             .focus();
    gadget.props.content_element.querySelector("input[type=text]")
                             .select();
    return new RSVP.Queue()
      .push(function () {
        return RSVP.all([
          promiseEventListener(
            gadget.props.content_element.querySelector('form.new-expense-report-form'),
            'submit',
            false
          ),
          gadget.getDeclaredGadget("jio_gadget")
        ]);
      })
      .push(function (result_list) {
        var submit_event = result_list[0],
          jio_gadget = result_list[1],
          i,
          doc = {
            // XXX Hardcoded
            parent_relative_url: "data_stream_module",
            portal_type: "Data Stream"
          }
        gadget.props.content_element.querySelector("input[type=submit]")
                                    .disabled = true;

        for (i = 0; i < submit_event.target.length; i += 1) {
          // XXX Should check input type instead
          if (submit_event.target[i].name) {
            doc[submit_event.target[i].name] = submit_event.target[i].value;
          }
        }

        return jio_gadget.post(doc);
      })
      .push(function () {
        return redirectToDefaultPage(gadget);
      });
  }


  function renderViewExpenseReportPage(gadget, key) {
    gadget.props.header_element.innerHTML = gadget.props.header_template({
      title: "View Data Stream"
    });
    return gadget.getDeclaredGadget("jio_gadget")
      .push(function (jio) {
        return jio.get(key);
      })
      .push(function (doc) {
        gadget.props.content_element.innerHTML =
          gadget.props.view_expense_report_template(doc);
        $(gadget.props.element).trigger("create");

        // XXX JP asked to edit documents before sync
        // Ivan: to have full example replace "!doc.reference" -> 1==1
        if (1==1) {
          gadget.props.header_element.innerHTML = gadget.props.edit_template({
            title: "Edit Data Stream",
            right_url: "Save"
          });
            
          return new RSVP.Queue()
            .push(function () {
              return RSVP.all([
                promiseEventListener(
                  gadget.props.header_element.querySelector('form.edit-form'),
                  'submit',
                  false
                ),
                gadget.getDeclaredGadget("jio_gadget")
              ]);
            })
            .push(function (result_list) {
              var submit_form = gadget.props.content_element
                  .querySelector('.view-expense-report-form'),
                jio_gadget = result_list[1],
                i,
                doc = {
                  // XXX Hardcoded
                  parent_relative_url: "data_stream_module",
                  portal_type: "Data Stream"
                };
              for (i = 0; i < submit_form.length; i += 1) {
                if (submit_form[i].name) {
                  doc[submit_form[i].name] = submit_form[i].value;
                }
              }
              return jio_gadget.put(key, doc);
            })
            .push(function () {
              return redirectToDefaultPage(gadget);
            });
        }
      });
  }


  rJS(window)
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          $(element).trigger("create");
          g.props.element = element;
          g.props.header_element = element.querySelector('.gadget-header').querySelector('div');
          g.props.content_element = element.querySelector('.gadget-content');

          g.props.view_expense_report_template = Handlebars.compile(
            document.querySelector(".view-expense-report-template").innerHTML
          );
          g.props.new_expense_report_template = Handlebars.compile(
            document.querySelector(".new-expense-report-template").innerHTML
          );
          g.props.login_template = Handlebars.compile(
            document.querySelector(".login-template").innerHTML
          );
          g.props.logout_template = Handlebars.compile(
            document.querySelector(".logout-template").innerHTML
          );
          g.props.synchro_template = Handlebars.compile(
            document.querySelector(".synchro-template").innerHTML
          );
          g.props.edit_template = Handlebars.compile(
            document.querySelector(".edit-template").innerHTML
          );
          g.props.document_list_template = Handlebars.compile(
            document.querySelector(".document-list-template").innerHTML
          );
          g.props.header_template = Handlebars.compile(
            document.querySelector(".header-template").innerHTML
          );
          g.props.sync_loader_template = Handlebars.compile(
            document.querySelector(".sync-loader-template").innerHTML
          );
        });
    })
    // Configure jIO storage
    .ready(function (g) {
      return createJio(g);
    })

    //////////////////////////////////////////
    // Acquired method
    //////////////////////////////////////////
    .declareAcquiredMethod('pleaseRedirectMyHash', 'pleaseRedirectMyHash')

    //////////////////////////////////////////
    // Declare method
    //////////////////////////////////////////
    .declareMethod('render', function (options) {
      var result,
        gadget = this;
      gadget.props.options = options;

      if (options.page === undefined) {
        result = redirectToDefaultPage(this);
      } else if (options.page === PAGE_CONNECTION) {
        result = renderConnectPage(this);
      } else if (options.page === PAGE_LIST) {
        result = renderDocumentListPage(this);
      } else if (options.page === PAGE_SYNC) {
        result = renderSynchroPage(this);
      } else if (options.page === PAGE_NEW_EXPENSE_REPORT) {
        result = renderNewExpenseReportPage(this);
      } else if (options.page === PAGE_VIEW_EXPENSE_REPORT) {
        result = renderViewExpenseReportPage(this, options.key);
      } else if (options.page === PAGE_LOGOUT) {
        result = renderLogoutPage(this);
      } else {
        throw new Error("not implemented page " + options.page);
      }
      return result;
    });

}(window, document, RSVP, rJS, Handlebars, promiseEventListener, jQuery));