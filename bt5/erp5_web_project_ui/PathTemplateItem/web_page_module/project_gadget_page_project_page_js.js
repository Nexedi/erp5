/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, ensureArray, DOMParser, XMLSerializer,
SimpleQuery, ComplexQuery, Query, domsugar*/
(function (window, rJS, RSVP, document, ensureArray, DOMParser, XMLSerializer,
            SimpleQuery, ComplexQuery, Query, domsugar) {
  "use strict";

  var VALID_STATE_LIST = ["shared", "released", "published",
                          "shared_alive", "released_alive", "published_alive"];

  function addRedirectionToReference(href, url) {
    if (!href.startsWith("https") && !href.startsWith("http") &&
        !href.startsWith("ftp") && !href.includes("/")
        ) {
      href = url + "&n.reference=" + href;
    }
    return href;
  }

  function parseHTMLLinks(html, url) {
    var parser = new DOMParser(), i,
      oSerializer = new XMLSerializer(),
      doc = parser.parseFromString(html || '', "text/html"),
      link_list = doc.querySelectorAll("a");
    doc.querySelector("head").appendChild(domsugar('link', {
      href: "gadget_erp5_page_project.css",
      type: "text/css",
      rel: "stylesheet"
    }));
    for (i = 0; i < link_list.length; i += 1) {
      link_list[i].setAttribute('href',
                                addRedirectionToReference(link_list[i]
                                                          .getAttribute('href'), url));
    }
    return oSerializer.serializeToString(doc);
  }

  function enableLink(link_element, url) {
    link_element.href = url;
    link_element.disabled = false;
    link_element.classList.remove("ui-disabled");
  }

  function getActionListByName(view_list, name) {
    return view_list.filter(d => d.name === name)[0].href;
  }

  function createMultipleSimpleOrQuery(key, value_list) {
    var i,
      query_list = [];
    for (i = 0; i < value_list.length; i += 1) {
      query_list.push(new SimpleQuery({
        key: key,
        operator: "",
        type: "simple",
        value: value_list[i]
      }));
    }
    return new ComplexQuery({
      operator: "OR",
      query_list: query_list,
      type: "complex"
    });
  }

  function createProjectQuery(project_jio_key, key_value_list) {
    var i, query_list = [], id_query_list = [], id_complex_query;
    if (project_jio_key) {
      //relation to project or child project lines
      id_query_list.push(new SimpleQuery({
        key: "source_project__relative_url",
        operator: "",
        type: "simple",
        value: project_jio_key
      }));
      id_query_list.push(new SimpleQuery({
        key: "source_project__relative_url",
        operator: "",
        type: "simple",
        value: project_jio_key + "/%%"
      }));
      id_complex_query = new ComplexQuery({
        operator: "OR",
        query_list: id_query_list,
        type: "complex"
      });
      query_list.push(id_complex_query);
    }
    for (i = 0; i < key_value_list.length; i += 1) {
      query_list.push(new SimpleQuery({
        key: key_value_list[i][0],
        operator: "",
        type: "simple",
        value: key_value_list[i][1]
      }));
    }
    return Query.objectToSearchText(new ComplexQuery({
      operator: "AND",
      query_list: query_list,
      type: "complex"
    }));
  }

  function setLatestTestResult(gadget, svg_element, project_jio_key) {
    var query = createProjectQuery(project_jio_key,
                 [["portal_type", "Test Result"]]);
    return gadget.jio_allDocs({
      query: query,
      limit: 1,
      sort_on: [['creation_date', 'descending']],
      select_list: ['simulation_state']
    })
      .push(function (result_list) {
        var state;
        result_list = result_list.data.rows;
        if (result_list.length > 0) {
          svg_element.classList.remove("ui-hidden");
          state = result_list[0].value.simulation_state;
          switch (state) {
          case 'started':
            svg_element.classList.add("running");
            document.querySelector("#test_result_running")
              .classList.remove("ui-hidden");
            break;
          case 'failed':
            svg_element.classList.add("fail");
            document.querySelector("#test_result_fail")
              .classList.remove("ui-hidden");
            break;
          case 'cancelled':
            svg_element.classList.add("cancelled");
            document.querySelector("#test_result_running")
              .classList.remove("ui-hidden");
            break;
          case 'stopped':
          case 'public_stopped':
            svg_element.classList.add("pass");
            document.querySelector("#test_result_pass")
              .classList.remove("ui-hidden");
            break;
          default:
            svg_element.classList.add("ui-hidden");
          }
        }
      });
  }

  function getWebPageInfo(gadget, project_jio_key, publication_section) {
    var id,
      content,
      edit_view,
      redirector_ulr,
      query,
      query_list = [],
      web_page;
    query_list.push(new SimpleQuery({
      key: "portal_type",
      operator: "=",
      type: "simple",
      value: "Web Page"
    }));
    query_list.push(new SimpleQuery({
      key: "follow_up__relative_url",
      operator: "=",
      type: "simple",
      value: project_jio_key
    }));
    query_list.push(new SimpleQuery({
      key: "publication_section__relative_url",
      operator: "=",
      type: "simple",
      value: "publication_section/" + publication_section
    }));
    query_list.push(createMultipleSimpleOrQuery('validation_state', VALID_STATE_LIST));
    query = new ComplexQuery({
      operator: "AND",
      query_list: query_list,
      type: "complex"
    });
    return gadget.getUrlFor({command: 'push_history',
                             options: {page: "project_redirector"}})
      .push(function (url) {
        redirector_ulr = url;
        return gadget.jio_allDocs({
          query: Query.objectToSearchText(query),
          select_list: ['text_content'],
          limit: 2
        });
      })
      .push(function (result_list) {
        if (result_list.data.rows[0]) {
          web_page = result_list.data.rows[0];
          id = web_page.id;
          content = parseHTMLLinks(web_page.value.text_content, redirector_ulr);
          return gadget.jio_getAttachment(id, "links")
            .push(function (web_page_document) {
              edit_view = getActionListByName(
                ensureArray(web_page_document._links.view),
                "view_editor"
              );
              return {"id": id, "content": content, "edit_view": edit_view};
            });
        }
        return null;
      });
  }

  function getUrlParameterDict(jio_key, view, sort_list, column_list, extended_search) {
    return {
      command: 'push_history',
      options: {
        'jio_key': jio_key,
        'page': 'form',
        'view': view,
        'field_listbox_sort_list:json': sort_list,
        'field_listbox_column_list:json': column_list,
        'extended_search': extended_search
      }
    };
  }

  rJS(window)

    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getSetting", "getSetting")

    .declareMethod('render', function (options) {
      var state_dict = {
          jio_key: options.jio_key || "",
          publication_section: options.publication_section
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        web_page_info,
        url_parameter_list,
        promise_list,
        editor;
      return new RSVP.Queue()
        .push(function () {
          promise_list = [
            gadget.getSetting("hateoas_url")
          ];
          if (modification_dict.publication_section) {
            promise_list.push(gadget.getDeclaredGadget("editor"));
            promise_list.push(getWebPageInfo(gadget, modification_dict.jio_key,
                                             modification_dict.publication_section));
          }
          return RSVP.all(promise_list);
        })
        .push(function (result_list) {
          var document_view = result_list[0] +
            '/ERP5Document_getHateoas?mode=traverse&relative_url=' +
            modification_dict.jio_key + '&view=Project_viewDocumentList',
            milestone_view = result_list[0] +
            '/ERP5Document_getHateoas?mode=traverse&relative_url=' +
            modification_dict.jio_key + '&view=Project_viewMilestoneList',
            activity_view = result_list[0] +
            '/ERP5Document_getHateoas?mode=traverse&relative_url=' +
            modification_dict.jio_key + '&view=Project_viewActivityList';
          web_page_info = result_list[2];
          if (web_page_info) {
            editor = result_list[1];
            editor.render({"editor": "fck_editor", "editable": false,
                           "value": web_page_info.content});
          }
          url_parameter_list = [
            getUrlParameterDict('milestone_module',
                                milestone_view,
                                [["stop_date", "ascending"]],
                                null,
                                createProjectQuery(null, [["selection_domain_date_milestone_domain", "future"]])),
            getUrlParameterDict('task_module',
                                "view",
                                [["delivery.start_date", "descending"]],
                                ["title", "delivery.start_date", "source_title, translated_simulation_state_title"],
                                createProjectQuery(modification_dict.jio_key,
                                                   [["selection_domain_state_task_domain", "opened"]])),
            getUrlParameterDict('support_request_module',
                                "view",
                                [["delivery.start_date", "descending"]],
                                null,
                                createProjectQuery(modification_dict.jio_key,
                                                   [["selection_domain_state_support_domain", "validated"]])),
            getUrlParameterDict('bug_module',
                                "view",
                                [["delivery.start_date", "descending"]],
                                ["title", "description", "source_person_title", "destination_person_title",
                                 "delivery.start_date", "translated_simulation_state_title"],
                                createProjectQuery(modification_dict.jio_key,
                                                   [["selection_domain_state_bug_domain", "open"]])),
            getUrlParameterDict('task_report_module',
                                'view',
                                [["delivery.start_date", "descending"]],
                                ["title", "delivery.start_date", "source_title",
                                 "translated_simulation_state_title"],
                                createProjectQuery(modification_dict.jio_key,
                                                   [["selection_domain_state_task_report_domain", "confirmed"]])),
            getUrlParameterDict('test_result_module',
                                'view',
                                [["delivery.start_date", "descending"]],
                                null,
                                createProjectQuery(modification_dict.jio_key, [])),
            getUrlParameterDict('test_suite_module',
                                'view',
                                [["creation_date", "descending"]],
                                null,
                                createProjectQuery(modification_dict.jio_key,
                                                   [["translated_validation_state_title", "validated"]])),
            getUrlParameterDict(modification_dict.jio_key,
                                document_view,
                                [["modification_date", "descending"]],
                                ["download", "title", "reference", "modification_date"],
                                createProjectQuery(null, [["selection_domain_state_document_domain", "confirmed"]])),
            getUrlParameterDict(modification_dict.jio_key,
                                activity_view,
                                [["modification_date", "descending"]])
          ];
          if (web_page_info) {
            url_parameter_list.push(getUrlParameterDict(web_page_info.id, web_page_info.edit_view));
          }
          return gadget.getUrlForList(url_parameter_list);
        })
        .push(function (url_list) {
          enableLink(document.querySelector("#milestone_link"), url_list[0]);
          enableLink(document.querySelector("#task_link"), url_list[1]);
          enableLink(document.querySelector("#support_request_link"), url_list[2]);
          enableLink(document.querySelector("#bug_link"), url_list[3]);
          enableLink(document.querySelector("#report_link"), url_list[4]);
          enableLink(document.querySelector("#test_result_link"), url_list[5]);
          enableLink(document.querySelector("#test_suite_link"), url_list[6]);
          enableLink(document.querySelector("#document_link"), url_list[7]);
          enableLink(document.querySelector("#activity_link"), url_list[8]);
          if (web_page_info) {
            enableLink(document.querySelector("#web_page_link"), url_list[9]);
          }
          //XXX move into a job to call it async
          setLatestTestResult(gadget, document.querySelector("#test_result_svg"),
                              modification_dict.jio_key);
        });
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, RSVP, document, ensureArray, DOMParser, XMLSerializer, SimpleQuery, ComplexQuery, Query, domsugar));