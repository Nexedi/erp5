/*global window, rJS, RSVP, calculatePageTitle, SimpleQuery, ComplexQuery,
         Query, QueryFactory */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, calculatePageTitle, SimpleQuery, ComplexQuery,
           Query, QueryFactory) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("renderEditorPanel", "renderEditorPanel")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")

    /////////////////////////////////////////////////////////////////
    // Proxy methods to the child gadget
    /////////////////////////////////////////////////////////////////
    .declareMethod('checkValidity', function checkValidity() {
      return this.getDeclaredGadget("erp5_form")
        .push(function (declared_gadget) {
          return declared_gadget.checkValidity();
        });
    }, {mutex: 'changestate'})
    .declareMethod('getContent', function getContent() {
      return this.getDeclaredGadget("erp5_form")
        .push(function (declared_gadget) {
          return declared_gadget.getContent();
        });
    }, {mutex: 'changestate'})
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function render(options) {
      var gadget = this;
      return gadget.getUrlParameter('extended_search')
        .push(function (extended_search) {
          var state_dict = {
            jio_key: options.jio_key,
            view: options.view,
            editable: options.editable,
            erp5_document: options.erp5_document,
            form_definition: options.form_definition,
            erp5_form: options.erp5_form || {},
            extended_search: extended_search
          };
          return gadget.changeState(state_dict);
        });
    })

    .onStateChange(function onStateChange() {
      var form_gadget = this;

      // render the erp5 form
      return form_gadget.getDeclaredGadget("erp5_form")
        .push(function (erp5_form) {
          var form_options = form_gadget.state.erp5_form;

          form_options.erp5_document = form_gadget.state.erp5_document;
          form_options.form_definition = form_gadget.state.form_definition;
          form_options.view = form_gadget.state.view;
          form_options.jio_key = form_gadget.state.jio_key;
          form_options.editable = form_gadget.state.editable;

          // XXX Hardcoded for listbox's hide/configure functionalities
          form_options.form_definition.hide_enabled = true;
          form_options.form_definition.configure_enabled = true;

          // XXX not generic, fix later
          if (form_gadget.state.extended_search) {
            form_options.form_definition.extended_search = form_gadget.state.extended_search;
          }

          return erp5_form.render(form_options);
        })

        // render the search field
        .push(function () {
          return form_gadget.getDeclaredGadget("erp5_searchfield");
        })
        .push(function (search_gadget) {
          var search_options = {};
          // XXX not generic, fix later
          if (form_gadget.state.extended_search) {
            search_options.extended_search = form_gadget.state.extended_search;
          }
          return search_gadget.render(search_options);
        })

        // render the header
        .push(function () {
          var new_content_action = form_gadget.state.erp5_document._links.action_object_new_content_action,
            url_for_parameter_list = [
              {command: 'change', options: {page: "action"}},
              {command: 'display', options: {}},
              {command: 'change', options: {page: "export"}}
            ];

          if (new_content_action !== undefined) {
            url_for_parameter_list.push({command: 'change', options: {
              view: new_content_action.href,
              editable: true
            }});
          }

          return RSVP.all([
            calculatePageTitle(form_gadget, form_gadget.state.erp5_document),
            form_gadget.getUrlForList(url_for_parameter_list)
          ]);
        })
        .push(function (result_list) {
          var url_list = result_list[1];
          return form_gadget.updateHeader({
            panel_action: true,
            jump_url: "",
            fast_input_url: "",
            add_url: url_list[3] || '',
            actions_url: url_list[0],
            export_url: (
              form_gadget.state.erp5_document._links.action_object_jio_report ||
              form_gadget.state.erp5_document._links.action_object_jio_print ||
              form_gadget.state.erp5_document._links.action_object_jio_exchange
            ) ? url_list[2] : '',
            page_title: result_list[0],
            front_url: url_list[1],
            filter_action: true
          });
        });

    })

    .declareMethod('triggerSubmit', function triggerSubmit(options) {
      var gadget = this,
        extended_search = '',
        focus_on;
      if (options !== undefined) {
        focus_on = options.focus_on;
      }
      return gadget.getDeclaredGadget("erp5_searchfield")
        .push(function (search_gadget) {
          return search_gadget.getContent();
        })
        .push(function (result) {
          // Hardcoded field name
          extended_search = result.search;
          return gadget.getDeclaredGadget("erp5_form");
        })
        .push(function (form_gadget) {
          return form_gadget.getListboxInfo();
        })
        .push(function (result) {
          return gadget.renderEditorPanel("gadget_erp5_search_editor.html", {
            extended_search: extended_search,
            begin_from: result.begin_from,
            search_column_list: result.search_column_list,
            domain_list: result.domain_list,
            domain_dict: result.domain_dict,
            focus_on: focus_on
          });
        });
    }, {mutex: 'changestate'})

    .onEvent('submit', function submit() {
      var gadget = this;

      return gadget.getDeclaredGadget("erp5_searchfield")
        .push(function (search_gadget) {
          return search_gadget.getContent();
        })
        .push(function (data) {
          var options = {
            begin_from: undefined,
            // XXX Hardcoded
            field_listbox_begin_from: undefined
          };
          if (data.search) {
            options.extended_search = data.search;
          } else {
            options.extended_search = undefined;
          }

          return gadget.redirect({command: 'store_and_change', options: options});
        });

    }, false, true)

    // Handle listbox custom button
    .allowPublicAcquisition("getListboxSelectActionList", function getListboxSelectActionList() {
      return this.getTranslationList(['Include', 'Exclude'])
        .push(function (result_list) {
          return [{
            title: result_list[0],
            icon: 'eye',
            action: 'include'
          }, {
            title: result_list[1],
            icon: 'low-vision',
            action: 'exclude'
          }];
        });
    })

    .allowPublicAcquisition("triggerListboxSelectAction", function triggerListboxSelectAction(argument_list) {
      var action = argument_list[0],
        checked_uid_list = argument_list[1],
        unchecked_uid_list = argument_list[2],
        gadget = this,
        i,
        search_query,
        query_list = [];
      if ((action === 'include') || (action === 'exclude')) {
        if (checked_uid_list.length === 0) {
          // If nothing is checked, use all unchecked values (same as xhtml style)
          checked_uid_list = unchecked_uid_list;
        }
        if (checked_uid_list.length === 0) {
          // XXX Queries do not correctly handle empty uid list
          return gadget.redirect({
            command: 'reload'
          });
        }

        for (i = 0; i < checked_uid_list.length; i += 1) {
          query_list.push(new SimpleQuery({
            key: "catalog.uid",
            type: "simple",
            operator: (action === 'include') ? "=" : "!=",
            value: checked_uid_list[i]
          }));
        }
        if (gadget.state.extended_search) {
          search_query = QueryFactory.create(gadget.state.extended_search);
        }
        if (action === 'include') {
          // Lines must match the existing query and be one of the selected
          // line. Which means that is user change the query, one of the
          // selected line could disappear.
          if (search_query) {
            search_query = new ComplexQuery({
              operator: "AND",
              query_list: [
                new ComplexQuery({
                  operator: "OR",
                  query_list: query_list,
                  type: "complex"
                }),
                search_query
              ],
              type: "complex"
            });
          } else {
            search_query = new ComplexQuery({
              operator: "OR",
              query_list: query_list,
              type: "complex"
            });
          }

        } else {
          // Lines must match the existing query and must not be one of the
          // selected line.
          if (search_query) {
            query_list.push(search_query);
          }
          search_query = new ComplexQuery({
            operator: "AND",
            query_list: query_list,
            type: "complex"
          });
        }

        return gadget.redirect({
          command: 'store_and_change',
          options: {
            "extended_search": Query.objectToSearchText(search_query)
          }
        });
      }

      throw new Error('Unsupported triggerListboxSelectAction action: ' + action);
    });

}(window, rJS, RSVP, calculatePageTitle, SimpleQuery, ComplexQuery, Query,
  QueryFactory));