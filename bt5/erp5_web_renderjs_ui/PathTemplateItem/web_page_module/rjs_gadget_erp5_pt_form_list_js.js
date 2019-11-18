/*global window, rJS, renderFormViewHeader, renderFormListHeader,
         SimpleQuery, ComplexQuery,
         Query, QueryFactory, ensureArray, triggerListboxClipboardAction,
         declareGadgetClassCanHandleListboxClipboardAction*/
/*jslint nomen: true, indent: 2, maxerr: 3, continue: true */
(function (window, rJS, renderFormViewHeader, renderFormListHeader,
           SimpleQuery, ComplexQuery,
           Query, QueryFactory, ensureArray, triggerListboxClipboardAction,
           declareGadgetClassCanHandleListboxClipboardAction) {
  "use strict";

  function updateSearchQueryFromSelection(extended_search, checked_uid_list,
                                          key, to_include) {
    var i,
      search_query,
      query_list = [];

    for (i = 0; i < checked_uid_list.length; i += 1) {
      query_list.push(new SimpleQuery({
        key: key,
        type: "simple",
        operator: to_include ? "=" : "!=",
        value: checked_uid_list[i]
      }));
    }
    if (extended_search) {
      search_query = QueryFactory.create(extended_search);
    }
    if (to_include) {
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
    return Query.objectToSearchText(search_query);
  }

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
    .declareAcquiredMethod("isDesktopMedia", "isDesktopMedia")

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
          var renderHeader;
          if (form_gadget.state.jio_key.indexOf('/') !== -1) {
            // If form list is used on a non module/tool document, display header
            // list form_view
            renderHeader = renderFormViewHeader;
          } else {
            renderHeader = renderFormListHeader;
          }
          return renderHeader(form_gadget, form_gadget.state.jio_key,
                              form_gadget.state.view,
                              form_gadget.state.erp5_document, true);
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

          return gadget.redirect({
            command: 'store_and_change',
            options: options
          }, true);
        });

    }, false, true)

    // Handle listbox custom button
    .allowPublicAcquisition("getListboxSelectActionList", function getListboxSelectActionList() {
      var gadget = this;
      return gadget.getTranslationList(['Include', 'Exclude'])
        .push(function (translation_list) {
          var result_list = [{
            title: translation_list[0],
            icon: 'eye',
            action: 'include'
          }, {
            title: translation_list[1],
            icon: 'low-vision',
            action: 'exclude'
          }],
            action_list = ensureArray(gadget.state.erp5_document._links.action_object_list_action || []),
            i,
            icon;

          for (i = 0; i < action_list.length; i += 1) {
            if (action_list[i].name === 'delete_document_list') {
              continue;
            }
            if (action_list[i].name === 'paste_document_list') {
              continue;
            }
            if (action_list[i].name === 'mass_workflow_jio') {
              icon = 'random';
            } else {
              icon = 'star';
            }
            result_list.unshift({
              title: action_list[i].title,
              icon: icon,
              action: action_list[i].name
            });
          }
          return result_list;
        });
    })

    .allowPublicAcquisition("triggerListboxSelectAction", function triggerListboxSelectAction(argument_list) {
      var action = argument_list[0],
        checked_uid_list = argument_list[1],
        unchecked_uid_list = argument_list[2],
        gadget = this;
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

        return gadget.redirect({
          command: 'store_and_change',
          options: {
            "extended_search": updateSearchQueryFromSelection(
              gadget.state.extended_search,
              checked_uid_list,
              'catalog.uid',
              (action === 'include')
            )
          }
        }, true);
      }

      if ((action !== 'delete_document_list') &&
          (action !== 'paste_document_list')) {
        return triggerListboxClipboardAction.apply(this, [argument_list]);
      }

      throw new Error('Unsupported triggerListboxSelectAction action: ' + action);
    });

  declareGadgetClassCanHandleListboxClipboardAction(rJS(window));

}(window, rJS, renderFormViewHeader, renderFormListHeader, SimpleQuery,
  ComplexQuery, Query,
  QueryFactory, ensureArray, triggerListboxClipboardAction,
  declareGadgetClassCanHandleListboxClipboardAction));