/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, ensureArray, DOMParser, XMLSerializer, SimpleQuery, ComplexQuery, Query*/
(function (window, rJS, RSVP, document, ensureArray, DOMParser, XMLSerializer, SimpleQuery, ComplexQuery, Query) {
  "use strict";

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
      doc = parser.parseFromString(html, "text/html"),
      link_list = doc.getElementsByTagName("a");
    for (i = 0; i < link_list.length; i += 1) {
      link_list[i].setAttribute('href', addRedirectionToReference(link_list[i].getAttribute('href'), url));
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

  function setLastTestResult(gadget, project_title, span_element, svg_element) {
    span_element.classList.remove("ui-disabled");
    var query = createProjectQuery(project_title,
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
            document.getElementById("test_result_running").classList.remove("ui-hidden");
            break;
          case 'failed':
            svg_element.classList.add("fail");
            document.getElementById("test_result_fail").classList.remove("ui-hidden");
            break;
          case 'cancelled':
            svg_element.classList.add("cancelled");
            document.getElementById("test_result_running").classList.remove("ui-hidden");
            break;
          case 'stopped':
          case 'public_stopped':
            svg_element.classList.add("pass");
            document.getElementById("test_result_pass").classList.remove("ui-hidden");
            break;
          default:
            svg_element.classList.add("ui-hidden");
          }
        }
      });
  }

  function createProjectQuery(project_title, key_value_list) {
    var i, query_list = [];
    if (project_title) {
      query_list.push(new SimpleQuery({
        key: "source_project_title",
        operator: "",
        type: "simple",
        value: project_title
      }));
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

  function getWebPageInfo(gadget, project_reference) {
    var id,
      content,
      edit_view,
      redirector_ulr,
      query,
      query_list = [],
      valid_state_list = ["shared_alive", "released_alive", "published_alive"];
    query_list.push(new SimpleQuery({
      key: "portal_type",
      operator: "=",
      type: "simple",
      value: "Web Page"
    }));
    query_list.push(new SimpleQuery({
      key: "reference",
      operator: "=",
      type: "simple",
      value: project_reference + '-Home.Page'
    }));
    query = new ComplexQuery({
      operator: "AND",
      query_list: query_list,
      type: "complex"
    });
    return gadget.getUrlFor({command: 'push_history', options: {page: "project_redirector"}})
      .push(function (url) {
        redirector_ulr = url;
        return gadget.jio_allDocs({
          query: Query.objectToSearchText(query),
          select_list: ['validation_state', 'text_content']
        });
      })
      .push(function (result_list) {
        if (result_list.data.rows[0]) {
          var i, state, web_page;
          for (i = 0; i < result_list.data.rows.length; i = i + 1) {
            state = result_list.data.rows[i].value.validation_state;
            if (valid_state_list.includes(state)) {
              web_page = result_list.data.rows[i];
              break;
            }
          }
          if (web_page) {
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
        }
        return {"id": id, "content": content, "edit_view": edit_view};
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
          project_title: options.project_title,
          project_reference: options.project_reference
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        web_page_info,
        editor;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            getWebPageInfo(gadget, modification_dict.project_reference),
            gadget.getDeclaredGadget("editor"),
            gadget.getSetting("hateoas_url")
          ]);
        })
        .push(function (result_list) {
          var document_view = result_list[2] +
            '/ERP5Document_getHateoas?mode=traverse&relative_url=' +
            modification_dict.jio_key + '&view=Project_viewDocumentList',
            milestone_view = result_list[2] +
            '/ERP5Document_getHateoas?mode=traverse&relative_url=' +
            modification_dict.jio_key + '&view=Project_viewMilestoneList';
          web_page_info = result_list[0];
          editor = result_list[1];
          editor.render({"editor": "fck_editor", "editable": false,
                         "value": web_page_info.content});
          return gadget.getUrlForList([
            //TODO drop 4, 6 and 9 calls when closed links removal is confirmed
            getUrlParameterDict('milestone_module', milestone_view, [["stop_date", "ascending"]],
              null, createProjectQuery(null, [["selection_domain_date_milestone_domain", "future"]])),
            getUrlParameterDict('task_module', "view", [["delivery.start_date", "descending"]],
              ["title", "delivery.start_date", "source_title"],
              createProjectQuery(modification_dict.project_title,
                [["selection_domain_state_task_domain", "confirmed"]])),
            getUrlParameterDict('support_request_module', "view", [["delivery.start_date", "descending"]],
              null, createProjectQuery(modification_dict.project_title,
                [["selection_domain_state_support_domain", "validated"]])),
            getUrlParameterDict('bug_module', "view", [["delivery.start_date", "descending"]],
              ["title", "description", "source_person_title", "destination_person_title", "delivery.start_date"],
              createProjectQuery(modification_dict.project_title,
                [["selection_domain_state_bug_domain", "started"]])),
            getUrlParameterDict('bug_module', "view", [["delivery.start_date", "descending"]],
              ["title", "description", "delivery.start_date"],
              createProjectQuery(modification_dict.project_title,
                [["selection_domain_state_bug_domain", "closed"]])),
            getUrlParameterDict('task_report_module', 'view', [["delivery.start_date", "descending"]],
              ["title", "delivery.start_date", "source_title"],
              createProjectQuery(modification_dict.project_title,
                [["selection_domain_state_task_report_domain", "started"]])),
            getUrlParameterDict('task_report_module', 'view', [["delivery.start_date", "descending"]],
              ["title", "delivery.start_date", "delivery.stop_date", "destination_decision_title",
                "source_title", "destination_title", "total_quantity", "task_line_quantity_unit_title"],
              createProjectQuery(modification_dict.project_title,
                [["selection_domain_state_task_report_domain", "closed"]])),
            getUrlParameterDict('test_result_module', 'view', [["delivery.start_date", "descending"]],
              null, createProjectQuery(modification_dict.project_title, [])),
            getUrlParameterDict('test_suite_module', 'view', [["creation_date", "descending"]],
              null, createProjectQuery(modification_dict.project_title, [])),
            getUrlParameterDict('task_module', "view", [["delivery.start_date", "descending"]],
              ["title", "delivery.start_date", "delivery.stop_date", "destination_decision_title",
                "source_title", "destination_title", "total_quantity", "task_line_quantity_unit_title"],
              createProjectQuery(modification_dict.project_title,
                [["selection_domain_state_task_domain", "not_confirmed"]])),
            getUrlParameterDict(web_page_info.id, web_page_info.edit_view),
            getUrlParameterDict(modification_dict.jio_key, document_view, [["modification_date", "descending"]],
              ["download", "title", "reference", "modification_date"], createProjectQuery(null, [["selection_domain_state_document_domain", "confirmed"]]))
          ]);
        })
        .push(function (url_list) {
          //TODO update url_list index when closed links removal is confirmed
          enableLink(document.getElementById("milestone_link"), url_list[0]);
          enableLink(document.getElementById("task_link"), url_list[1]);
          enableLink(document.getElementById("support_request_link"), url_list[2]);
          enableLink(document.getElementById("bug_link"), url_list[3]);
          //enableLink(document.getElementById("closed_bug_link"), url_list[4]);
          enableLink(document.getElementById("report_link"), url_list[5]);
          //enableLink(document.getElementById("closed_report_link"), url_list[6]);
          enableLink(document.getElementById("test_result_link"), url_list[7]);
          enableLink(document.getElementById("test_suite_link"), url_list[8]);
          //enableLink(document.getElementById("not_confirmed_task_link"), url_list[9]);
          if (web_page_info.id) {
            enableLink(document.getElementById("web_page_link"), url_list[10]);
          }
          enableLink(document.getElementById("document_link"), url_list[11]);
          setLastTestResult(gadget, modification_dict.project_title,
                            document.getElementById("test_result_span"),
                            document.getElementById("test_result_svg"));
        });
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, RSVP, document, ensureArray, DOMParser, XMLSerializer, SimpleQuery, ComplexQuery, Query));