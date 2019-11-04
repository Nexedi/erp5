/*jslint nomen: true, indent: 2 */
/*global window, rJS, RSVP, document, FileReader, Blob, jIO, ensureArray,
lockGadgetInQueue, unlockGadgetInQueue, Handlebars*/
(function (window, rJS, RSVP, document, FileReader, Blob, jIO, ensureArray,
           lockGadgetInQueue, unlockGadgetInQueue, Handlebars) {
  "use strict";

  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                         .getElementById("table-template")
                         .innerHTML,
    table_template = Handlebars.compile(source);

  function enableLink(link_element, url) {
    link_element.href = url;
    link_element.disabled = false;
    link_element.classList.remove("ui-disabled");
  }

  function getActionListByName(view_list, name) {
    return view_list.filter(d => d.name === name)[0].href;
  }

  function setLastTestResult(gadget, project_title, span_element) {
    var query = 'portal_type:="Benchmark Result" AND source_project_title:"' + project_title + '"';
    return gadget.jio_allDocs({
      query: query,
      limit: 2, //first result could be the running test
      sort_on: [['creation_date', 'descending']],
      select_list: ['simulation_state']
    })
    .push(function (result_list) {
      var i, state;
      result_list = result_list.data.rows;
      for (i = 0; i < result_list.length; i = i + 1) {
        state = result_list[i].value.simulation_state;
        if (state === "stopped" || state === "public_stopped") {
          span_element.classList.add("pass");
          break;
        } else if (state === "failed") {
          span_element.classList.add("fail");
          break;
        }
      }
    });
  }

  function getWebPage(gadget, project_reference) {
    var query = 'portal_type:="Web Page" AND reference:"' + project_reference + '-Home.Page" AND validation_state:"published_alive"',
        id, content;
    return gadget.jio_allDocs({
      query: query,
      limit: 1,
      select_list: ['id', 'text_content']
    })
    .push(function (result_list) {
      if (result_list.data.rows) {
        id = result_list.data.rows[0].id;
        content = result_list.data.rows[0].value.text_content;
      }
      return {"id": id, "content": content};
    });
  }

  function getUrlParameters(jio_key, view, sort_list, column_list, extended_search) {
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

  gadget_klass

    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")

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
        base_site = window.location.origin + window.location.pathname,
        project_url = base_site + modification_dict.jio_key,
        web_page_info;
      setLastTestResult(gadget, modification_dict.project_title, document.getElementById("test_result_span"));
      return getWebPage(gadget, modification_dict.project_reference)
        .push(function (result) {
          web_page_info = result;
          return gadget.jio_getAttachment(modification_dict.jio_key, "links");
        })
        .push(function (erp5_document) {
          var milestone_view = getActionListByName(ensureArray(erp5_document._links.view), "milestone");
          return gadget.getUrlForList([getUrlParameters('milestone_module', milestone_view, [["stop_date", "ascending"]]),
            getUrlParameters('task_module', "view", [["delivery.start_date", "descending"]],
                             ["title", "delivery.start_date", "delivery.stop_date", "destination_decision_title",
                              "source_title", "destination_title", "total_quantity", "task_line_quantity_unit_title"],
                             ('source_project_title:  "' + modification_dict.project_title + '" AND selection_domain_state_task_domain:  "confirmed"')),
            getUrlParameters('support_request_module', "view", [["delivery.start_date", "descending"]],
                             null, ('source_project_title:  "' + modification_dict.project_title + '" AND selection_domain_state_support_domain:  "validated"')),
            getUrlParameters('bug_module', "view", [["delivery.start_date", "descending"]],
                             ["title", "description", "delivery.start_date"],
                             ('source_project_title:  "' + modification_dict.project_title + '" AND selection_domain_state_bug_domain:  "started"')),
            getUrlParameters('bug_module', "view", [["delivery.start_date", "descending"]],
                             ["title", "description", "delivery.start_date"],
                             ('source_project_title:  "' + modification_dict.project_title + '" AND selection_domain_state_bug_domain:  "closed"')),
            getUrlParameters('task_report_module', 'view', [["delivery.start_date", "descending"]],
                             ["title", "delivery.start_date", "delivery.stop_date", "destination_decision_title",
                              "source_title", "destination_title", "total_quantity", "task_line_quantity_unit_title"],
                             ('source_project_title:  "' + modification_dict.project_title + '" AND selection_domain_state_task_report_domain:  "started"')),
            getUrlParameters('task_report_module', 'view', [["delivery.start_date", "descending"]],
                             ["title", "delivery.start_date", "delivery.stop_date", "destination_decision_title",
                              "source_title", "destination_title", "total_quantity", "task_line_quantity_unit_title"],
                             ('source_project_title:  "' + modification_dict.project_title + '" AND selection_domain_state_task_report_domain:  "closed"')),
            getUrlParameters('test_result_module', 'view', [["delivery.start_date", "descending"]],
                             null, ('source_project_title:  "' + modification_dict.project_title + '"')),
            getUrlParameters('test_suite_module', 'view', [["creation_date", "descending"]],
                             null, ('source_project_title:  "' + modification_dict.project_title + '"')),
            getUrlParameters('task_module', "view", [["delivery.start_date", "descending"]],
                             ["title", "delivery.start_date", "delivery.stop_date", "destination_decision_title",
                              "source_title", "destination_title", "total_quantity", "task_line_quantity_unit_title"],
                             ('source_project_title:  "' + modification_dict.project_title + '" AND selection_domain_state_task_domain:  "not_confirmed"')),
            getUrlParameters(web_page_info.id, "view") ]);
        })
        .push(function (url_list) {
          enableLink(document.getElementById("milestone_link"), url_list[0]);
          enableLink(document.getElementById("task_link"), url_list[1]);
          enableLink(document.getElementById("support_request_link"), url_list[2]);
          enableLink(document.getElementById("bug_link"), url_list[3]);
          enableLink(document.getElementById("closed_bug_link"), url_list[4]);
          enableLink(document.getElementById("report_link"), url_list[5]);
          enableLink(document.getElementById("closed_report_link"), url_list[6]);
          enableLink(document.getElementById("test_result_link"), url_list[7]);
          enableLink(document.getElementById("test_suite_link"), url_list[8]);
          enableLink(document.getElementById("not_confirmed_task_link"), url_list[9]);

          return gadget.getDeclaredGadget("editor");
        })
        .push(function (editor) {
          editor.render({"editor": "fck_editor", "editable": false, "value": web_page_info.content});
        });
    })

    .declareMethod('getContent', function () {
      return {};
    })

    .declareMethod('checkValidity', function () {
      return true;
    });

}(window, rJS, RSVP, document, FileReader, Blob, jIO, ensureArray,
  lockGadgetInQueue, unlockGadgetInQueue, Handlebars));