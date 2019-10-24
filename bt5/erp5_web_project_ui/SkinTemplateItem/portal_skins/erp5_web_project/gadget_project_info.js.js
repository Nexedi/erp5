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

  function generateLink(gadget, link_element, command, options) {
    return gadget.getUrlFor({command: command, options: options})
      .push(function (result) {
        enableLink(link_element, result);
      });
  }

  function generateInfo(gadget, span_element, info_url) {
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          url: info_url,
          dataType: 'text'
        });
      })
      .push(function (evt) {
        return evt.target.responseText.split('\n');
      })
      .push(function (result) {
        span_element.innerHTML = result;
      });
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

  function setHTMLelementWithPromise(span_element, promise) {
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

  //rJS(window)
  gadget_klass

    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")

    .declareMethod('render', function (options) {
      //console.log("info gadget render options:");
      //console.log(options);
      var state_dict = {
          jio_key: options.jio_key || "",
          //HACK
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
        task_count_promise = generateAjaxPromise(project_url + "/Project_tasks"),
        bug_count_promise = generateAjaxPromise(project_url + "/Project_bugs");

      document.getElementById("home_page_content").innerHTML = modification_dict.home_page_content;

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
            request_view = getActionListByName(view_list, "request_list");

          gadget.element.querySelectorAll("h1")[0].innerHTML = modification_dict.project_title;

          enableLink(document.getElementById("forum_link"), modification_dict.forum_link);
          //enableLink(document.getElementById("description_link"), modification_dict.description_link);

          generateLink(gadget, document.getElementById("milestone_link"), 'display_with_history', {
            'jio_key': 'milestone_module', 'page': 'form', 'view': milestone_view,
            'field_listbox_sort_list:json': [["stop_date", "ascending"]]
          }, {});

          generateLink(gadget, document.getElementById("support_request_link"), 'display_with_history', {
            'jio_key': 'support_request_module',
            'page': 'form',
            'view': request_view,
            'field_listbox_sort_list:json': [["delivery.start_date", "descending"]],
            'extended_search': ('selection_domain_state_support_domain:  "validated"')
          });

          var bug_options = {
            'jio_key': 'bug_module', 'page': 'form', 'view': bug_view,
            'field_listbox_sort_list:json': [["delivery.start_date", "descending"]],
            'field_listbox_column_list:json': ["title", "description", "delivery.start_date"],
            'extended_search': ('selection_domain_state_bug_domain:  "started"')
          }, closed_bug_options = {};
          generateLink(gadget, document.getElementById("bug_link"), 'display', bug_options);
          Object.assign(closed_bug_options, bug_options);
          closed_bug_options.extended_search = ('selection_domain_state_bug_domain:  "closed"');
          generateLink(gadget, document.getElementById("closed_bug_link"), 'display', closed_bug_options);
          //generateInfo(gadget, document.getElementById("bug_count"), project_url + "/Project_bugs");
          setHTMLelementWithPromise(document.getElementById("bug_count"), bug_count_promise);
          generateInfo(gadget, document.getElementById("closed_bug_count"), project_url + "/Project_bugs?closed=1");

          generateLink(gadget, document.getElementById("task_link"), 'display_with_history', {
            'jio_key': 'task_module', 'page': 'form', 'view': task_view,
            'field_listbox_sort_list:json': [["delivery.start_date", "descending"]],
            'field_listbox_column_list:json': ["title", "delivery.start_date", "delivery.stop_date", "destination_decision_title",
                                               "source_title", "destination_title", "total_quantity", "task_line_quantity_unit_title"],
            'extended_search': ('selection_domain_state_task_domain:  "confirmed"')
          });
          //generateInfo(gadget, document.getElementById("task_count"), project_url + "/Project_tasks");
          setHTMLelementWithPromise(document.getElementById("task_count"), task_count_promise);
          generateInfo(gadget, document.getElementById("unassigned_task_count"), project_url + "/Project_tasksToAssigne");

          var task_report_options = {
            'jio_key': 'task_report_module', 'page': 'form', 'view': 'view',
            'field_listbox_sort_list:json': [["delivery.start_date", "descending"]],
            'field_listbox_column_list:json': ["title", "delivery.start_date", "delivery.stop_date", "destination_decision_title",
                                               "source_title", "destination_title", "total_quantity", "task_line_quantity_unit_title"],
            'extended_search': ('source_project_title:  "' + modification_dict.project_title + '" AND selection_domain_state_task_report_domain:  "started"')
          }, closed_task_report_options = {};
          generateLink(gadget, document.getElementById("report_link"), 'display_with_history', task_report_options);
          Object.assign(closed_task_report_options, task_report_options);
          closed_task_report_options.extended_search = ('source_project_title:  "' + modification_dict.project_title + '" AND selection_domain_state_task_report_domain:  "closed"');
          generateLink(gadget, document.getElementById("closed_report_link"), 'display_with_history', closed_task_report_options);
          generateInfo(gadget, document.getElementById("report_count"), project_url + "/Project_taskReports");
          generateInfo(gadget, document.getElementById("closed_report_count"), project_url + "/Project_taskReports?closed=1");

          generateLink(gadget, document.getElementById("test_result_link"), 'display_with_history', {
            'jio_key': 'test_result_module',
            'page': 'form',
            'view': 'view',
            'field_listbox_sort_list:json': [["delivery.start_date", "descending"]],
            'extended_search': ('source_project_title:  "' + modification_dict.project_title + '"')
          });
          generateInfo(gadget, document.getElementById("last_test_result"), project_url + "/Project_lastTestResult");

          generateLink(gadget, document.getElementById("test_suite_link"), 'display_with_history', {
            'jio_key': 'test_suite_module',
            'page': 'form',
            'view': 'view',
            'field_listbox_sort_list:json': [["creation_date", "descending"]],
            'extended_search': ('source_project_title:  "' + modification_dict.project_title + '"')
          });

          var i, promise_list = [];
          work_item_list.push({
            display_options: {
              'jio_key': 'bug_module', 'page': 'form', 'view': bug_view,
              'field_listbox_sort_list:json': [["delivery.start_date", "descending"]],
              'field_listbox_column_list:json': ["title", "description", "delivery.start_date"],
              'extended_search': ('selection_domain_state_bug_domain:  "started"')
            },
            action_name: "Open bugs",
            action_count: "......",
            span_id: "open_bug_id",
            count_promise: bug_count_promise
          });
          work_item_list.push({
            display_options: {
              'jio_key': 'task_module', 'page': 'form', 'view': task_view,
              'field_listbox_sort_list:json': [["delivery.start_date", "descending"]],
              'field_listbox_column_list:json': ["title", "delivery.start_date", "delivery.stop_date", "destination_decision_title",
                                                 "source_title", "destination_title", "total_quantity", "task_line_quantity_unit_title"],
              'extended_search': ('selection_domain_state_task_domain:  "confirmed"')
            },
            action_name: "Tasks",
            action_count: "......",
            span_id: "task_id",
            count_promise: task_count_promise
          });
          work_item_list.push({
            display_options: {
              'jio_key': 'support_request_module',
              'page': 'form',
              'view': request_view,//'view',
              'field_listbox_sort_list:json': [["delivery.start_date", "descending"]],
              'extended_search': ('selection_domain_state_support_domain:  "validated"')
            },
            action_name: "Support Requests",
            action_count: "......",
            span_id: "support_id",
            count_promise: task_count_promise
          });
          for (i = 0; i < work_item_list.length; i += 1) {
            promise_list.push(gadget.getUrlFor({command: 'display', options: work_item_list[i].display_options}));
          }
          return RSVP.all(promise_list);
        })
        .push(function (link_list) {
          var i, line_list = [];
          for (i = 0; i < work_item_list.length; i += 1) {
            line_list.push({
              link: link_list[i],
              title: work_item_list[i].action_name,
              count: work_item_list[i].action_count,
              id: work_item_list[i].span_id
            });
          }
          gadget.element.querySelector('.document_list').innerHTML = table_template({
            document_list: line_list
          });
          for (i = 0; i < work_item_list.length; i += 1) {
            setHTMLelementWithPromise(document.getElementById(work_item_list[i].span_id), work_item_list[i].count_promise);
            //generateInfo(gadget, document.getElementById(work_item_list[i].span_id), project_url + work_item_list[i].count_script);
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