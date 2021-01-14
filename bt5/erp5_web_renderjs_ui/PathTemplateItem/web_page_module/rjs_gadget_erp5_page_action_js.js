/*global window, rJS, RSVP, domsugar, calculatePageTitle, ensureArray, console */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, domsugar, calculatePageTitle, ensureArray) {
  "use strict";

  function generateSection(title, icon, view_list) {
    var i,
      dom_list = [];
    for (i = 0; i < view_list.length; i += 1) {
      dom_list.push(domsugar('li', [domsugar('a', {
        href: view_list[i].link,
        text: view_list[i].title
      })]));
    }

    return domsugar(null, [
      domsugar('section', {class: 'ui-content-header-plain'}, [
        domsugar('h3', [
          domsugar('span', {class: 'ui-icon ui-icon-' + icon, html: '&nbsp;'}),
          title
        ])
      ]),
      domsugar('ul', {class: 'document-listview'}, dom_list)
    ]);

  }

  function genericFunctionToMergeActions(gadget, links, group_mapping, editable_mapping) {
    var i, group,
      action_type,
      url_mapping = {};

    for (group in group_mapping) {
      if (group_mapping.hasOwnProperty(group)) {
        if (!url_mapping.hasOwnProperty(group)) {
          url_mapping[group] = [];
        }
        for (i = 0; i < group_mapping[group].length; i += 1) {
          url_mapping[group].push({
            command: 'display_with_history_and_cancel',
            options: {
              jio_key: gadget.state.jio_key,
              view: group_mapping[group][i].href,
              editable: editable_mapping[group],
              title: group_mapping[group][i].title
            }
          });
        }
        action_type = group + "_raw";
        if (links.hasOwnProperty(action_type)) {
          for (i = 0; i < links[action_type].length; i += 1) {
              if (links[action_type][i].href) {
                url_mapping[group].push(links[action_type][i]);
              }
            }
          }
      }
    }
    return url_mapping;
  }
  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    /** Render only transforms its arguments and passes them to mutex-protected onStateChange

    options:
      jio_key: {string} currently viewed document (e.g. foo/1)
      page: {string} selected page (always "tab" for page_tab)
      view: {string} always "view"
      selection, history, selection_index
    */
    .declareMethod("render", function (options) {
      return this.changeState({
        jio_key: options.jio_key,
        editable: options.editable,
        view: options.view
      });
    })

    .onStateChange(function () {
      var gadget = this,
        erp5_document,
        url_mapping,
        group_list,
        raw_list;

      // Get the whole view as attachment because actions can change based on
      // what view we are at. If no view available than fallback to "links".
      return gadget.jio_getAttachment(gadget.state.jio_key, gadget.state.view || "links")
        .push(function (jio_attachment) {
          erp5_document = jio_attachment;
          raw_list = ensureArray(erp5_document._links.action_object_development_mode_jump_raw);

          var i, j,
            group_mapping,
            icon_mapping,
            editable_mapping,
            url_for_kw_list = [];

          group_mapping = {
            action_workflow: ensureArray(erp5_document._links.action_workflow),
            action_object_jio_action: ensureArray(erp5_document._links.action_object_jio_action)
              .concat(ensureArray(erp5_document._links.action_object_jio_button))
              .concat(ensureArray(erp5_document._links.action_object_jio_fast_input)),
            action_object_clone_action: ensureArray(erp5_document._links.action_object_clone_action),
            action_object_delete_action: ensureArray(erp5_document._links.action_object_delete_action)
          }

          url_mapping = genericFunctionToMergeActions(gadget,
            erp5_document._links,
            group_mapping, {
              action_object_clone_action: true,
          });

          group_list = [
            url_mapping.action_workflow, 'random',
            url_mapping.action_object_jio_action, 'gear',
            url_mapping.action_object_clone_action, 'clone',
            url_mapping.action_object_delete_action, 'trash-o'
          ];

          for (i = 0; i < group_list.length; i += 2) {
            for (j = 0; j < group_list[i].length; j += 1) {
              url_for_kw_list.push(group_list[i][j]);
            }
          }

          // Developer mode
          for (i = 0; i < raw_list.length; i += 1) {
            url_for_kw_list.push({
              command: 'raw',
              options: {
                url: raw_list[i].href
              }
            });
          }

          url_for_kw_list.push({command: 'cancel_dialog_with_history'});

          return RSVP.hash({
            url_list: gadget.getUrlForList(url_for_kw_list),
            translation_list: gadget.getTranslationList(['Workflows', 'Actions', 'Clone', 'Delete', 'Developer Mode']),
            page_title: calculatePageTitle(gadget, erp5_document)
          });
        })

        .push(function (result_dict) {
          var i,
            j,
            k = 0,
            dom_list = [],
            raw_action_list = [],
            link_list;

          for (i = 0; i < group_list.length; i += 2) {
            link_list = [];
            for (j = 0; j < group_list[i].length; j += 1) {
              link_list.push({
                title: group_list[i][j].title,
                link: result_dict.url_list[k]
              });
              k += 1;
            }
            dom_list.push(
              generateSection(result_dict.translation_list[i / 2], group_list[i + 1], link_list)
            );

          }
          for (i = 0; i < raw_list.length; i += 1) {
            raw_action_list.push({
              title: raw_list[i].title,
              link: result_dict.url_list[k]
            });
            k += 1;
          }

          if (raw_action_list.length > 0) {
            dom_list.push(generateSection(result_dict.translation_list[4], 'plane', raw_action_list));
          }

          domsugar(gadget.element, dom_list);

          return gadget.updateHeader({
            back_url: result_dict.url_list[result_dict.url_list.length - 1],
            page_title: result_dict.page_title
          });
        });
    })
    .declareMethod("triggerSubmit", function () {
      return;
    });

}(window, rJS, RSVP, domsugar, calculatePageTitle, ensureArray));
