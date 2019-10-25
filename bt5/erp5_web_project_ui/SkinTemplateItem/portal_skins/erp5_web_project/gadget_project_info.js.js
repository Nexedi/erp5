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

  function generateAjaxPromise(url) {
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          url: url,
          dataType: 'text'
        });
      })
      .push(function (evt) {
        return evt.target.responseText.split('\n');
      });
  }

  function setHTMLWithPromiseResult(span_element, promise) {
    return new RSVP.Queue()
      .push(function () {
        return promise;
      })
      .push(function (result) {
        span_element.innerHTML = result;
      });
  }

  function getActionListByName(view_list, name) {
    return view_list.filter(d => d.name === name)[0].href;
  }

  function getUrlParameters(jio_key, view, sort_list, column_list, extended_search) {
    return {
      command: 'display_with_history',
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

    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")

    .declareMethod('render', function (options) {
      var state_dict = {
          jio_key: options.jio_key || "",
          //TODO remove this hack
          forum_link: options.forum_link || "https://www.erp5.com/group_section/forum",
          //description_link: options.description_link || "https://www.erp5.com/project_section/nexedi-erp5",
          project_title: options.project_title,
          home_page_content: options.home_page_content
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        base_site = window.location.origin + window.location.pathname,
        project_url = base_site + modification_dict.jio_key,
        work_item_list = [],
        //execute ajax request asap and keep them as promises
        task_count_promise = generateAjaxPromise(project_url + "/Project_tasks"),
        bug_count_promise = generateAjaxPromise(project_url + "/Project_bugs"),
        closed_bug_count_promise = generateAjaxPromise(project_url + "/Project_bugs?closed=1"),
        unassigned_task_count_promise = generateAjaxPromise(project_url + "/Project_tasksToAssigne"),
        report_count_promise = generateAjaxPromise(project_url + "/Project_taskReports"),
        closed_report_count_promise = generateAjaxPromise(project_url + "/Project_taskReports?closed=1"),
        last_test_result_promise = generateAjaxPromise(project_url + "/Project_lastTestResult");

      //set html elements with promises result
      setHTMLWithPromiseResult(document.getElementById("task_count"), task_count_promise);
      setHTMLWithPromiseResult(document.getElementById("bug_count"), bug_count_promise);
      setHTMLWithPromiseResult(document.getElementById("closed_bug_count"), closed_bug_count_promise);
      setHTMLWithPromiseResult(document.getElementById("unassigned_task_count"), unassigned_task_count_promise);
      setHTMLWithPromiseResult(document.getElementById("report_count"), report_count_promise);
      setHTMLWithPromiseResult(document.getElementById("closed_report_count"), closed_report_count_promise);
      setHTMLWithPromiseResult(document.getElementById("last_test_result"), last_test_result_promise);

      gadget.element.querySelectorAll("h1")[0].innerHTML = modification_dict.project_title;
      document.getElementById("home_page_content").innerHTML = modification_dict.home_page_content;
      enableLink(document.getElementById("forum_link"), modification_dict.forum_link);
      //enableLink(document.getElementById("description_link"), modification_dict.description_link);

      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.jio_getAttachment(modification_dict.jio_key, "links")
          ]);
        })
        .push(function (result_list) {
          var view_list = ensureArray(result_list[0]._links.view),
            task_view = getActionListByName(view_list, "task_list"),
            bug_view = getActionListByName(view_list, "bug_list"),
            milestone_view = getActionListByName(view_list, "milestone"),
            task_report_view = getActionListByName(view_list, "task_report_list"),
            request_view = getActionListByName(view_list, "request_list"),
            url_promise_list = [];

          return gadget.getUrlForList([getUrlParameters('milestone_module', milestone_view, [["stop_date", "ascending"]]),
            getUrlParameters('task_module', task_view, [["delivery.start_date", "descending"]],
                             ["title", "delivery.start_date", "delivery.stop_date", "destination_decision_title",
                              "source_title", "destination_title", "total_quantity", "task_line_quantity_unit_title"],
                             ('selection_domain_state_task_domain:  "confirmed"')),
            getUrlParameters('support_request_module', request_view, [["delivery.start_date", "descending"]],
                             null, ('selection_domain_state_support_domain:  "validated"')),
            getUrlParameters('bug_module', bug_view, [["delivery.start_date", "descending"]],
                             ["title", "description", "delivery.start_date"],
                             ('selection_domain_state_bug_domain:  "started"')),
            getUrlParameters('bug_module', bug_view, [["delivery.start_date", "descending"]],
                             ["title", "description", "delivery.start_date"],
                             ('selection_domain_state_bug_domain:  "closed"')),
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
                             null, ('source_project_title:  "' + modification_dict.project_title + '"')) ]);
        })
        .push(function (url_list) {

          enableLink(document.getElementById("milestone_link"), url_list[0]);
          enableLink(document.getElementById("closed_bug_link"), url_list[4]);
          enableLink(document.getElementById("closed_report_link"), url_list[6]);
          enableLink(document.getElementById("test_result_link"), url_list[7]);
          enableLink(document.getElementById("test_suite_link"), url_list[8]);

          work_item_list.push({
            url: url_list[1],
            element_name: "Open tasks",
            element_count: "...",
            element_id: "task_span",
            link_id: "task_link",
            count_promise: task_count_promise
          });
          work_item_list.push({
            url: url_list[5],
            element_name: "Open task reports",
            element_count: "...",
            element_id: "open_report_span",
            link_id: "report_link",
            count_promise: report_count_promise
          });
          work_item_list.push({
            url: url_list[3],
            element_name: "Open bugs",
            element_count: "...",
            element_id: "open_bug_span",
            link_id: "bug_link",
            count_promise: bug_count_promise
          });
          work_item_list.push({
            url: url_list[2],
            element_name: "Support requests",
            element_count: "...",
            element_id: "support_span",
            link_id: "support_request_link",
            count_promise: task_count_promise
          });

          var i, line_list = [];
          for (i = 0; i < work_item_list.length; i += 1) {
            line_list.push({
              link: work_item_list[i].url,
              title: work_item_list[i].element_name,
              count: work_item_list[i].element_count,
              id: work_item_list[i].element_id
            });
          }
          gadget.element.querySelector('.document_list').innerHTML = table_template({
            document_list: line_list
          });
          for (i = 0; i < work_item_list.length; i += 1) {
            if (work_item_list[i].link_id) {
              enableLink(document.getElementById(work_item_list[i].link_id), work_item_list[i].url);
            }
            if (work_item_list[i].element_id) {
              setHTMLWithPromiseResult(document.getElementById(work_item_list[i].element_id), work_item_list[i].count_promise);
            }
          }
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