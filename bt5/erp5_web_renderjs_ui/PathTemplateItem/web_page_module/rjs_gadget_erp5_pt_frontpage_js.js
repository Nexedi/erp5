/*global window, rJS, jIO, RSVP, domsugar */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
(function (window, rJS, jIO, RSVP, domsugar) {
  "use strict";

  function generateCardList(element, card_list) {
    var i,
      len = card_list.length,
      card,
      dom_list = [],
      sub_dom_list,
      len2,
      j;

    for (i = 0; i < len; i += 1) {
      card = card_list[i];

      len2 = card.module_list.length;
      sub_dom_list = [];
      for (j = 0; j < len2; j += 1) {
        sub_dom_list.push(domsugar('li', [
          domsugar('a', {
            href: card.module_list[j].link,
            text: card.module_list[j].translated_title
          })
        ]));
      }
      dom_list.push(domsugar('li', [
        domsugar('h2', {text: card.business_application_translated_title}),
        domsugar('ul', sub_dom_list)
      ]));
    }
    domsugar(element, dom_list);
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    .declareMethod('triggerSubmit', function () {
      return;
    })
    .declareMethod('render', function renderHeader() {
      var gadget = this,
        select_list = ['translated_title',
                       'business_application_translated_title', 'id'];
      // First, get the list of modules
      return gadget.jio_allDocs({
        select_list: select_list,
        query: 'module_id:%',
        limit: 1000
      })
        .push(function (result_list) {
          // ERP5 catalog can't sort by translated property
          // Sort manually with jIO
          var data_rows = [],
            i,
            len = result_list.data.total_rows;
          for (i = 0; i < len; i += 1) {
            result_list.data.rows[i].value.id =
              result_list.data.rows[i].id;
            data_rows.push(result_list.data.rows[i].value);
          }

          return jIO.QueryFactory.create('')
            .exec(data_rows,
                  {query: '', select_list: select_list,
                   sort_on: [['business_application_translated_title',
                              'ascending'],
                             ['translated_title', 'ascending']]});
        })
        .push(function (document_list) {
          var url_dict_list = [],
            i,
            len = document_list.length;
          // Calculate all module's urls
          for (i = 0; i < len; i += 1) {
            url_dict_list.push({
              command: 'push_history_stored_state',
              options: {jio_key: document_list[i].id}
            });
          }
          // Add global url calculation
          url_dict_list.push({command: 'display'});
          return RSVP.all([
            document_list,
            gadget.getTranslationList(['Others', 'Tools']),
            gadget.getUrlForList(url_dict_list)
          ]);
        })
        .push(function (result_list) {
          var document_list = result_list[0],
            translated_other_title = result_list[1][0],
            translated_tool_title = result_list[1][1],
            url_list = result_list[2],
            len = document_list.length,
            i,
            card_list = [],
            module_list = [],
            other_module_list = [],
            tool_list = [],
            current_business_application_title = '';

          function pushNewCard() {
            if (module_list) {
              if (!current_business_application_title) {
                other_module_list = module_list;
              } else {
                card_list.push({
                  business_application_translated_title:
                    current_business_application_title,
                  module_list: module_list
                });
              }
            }
          }

          for (i = 0; i < len; i += 1) {
            // Inject the module url into the document
            document_list[i].link = url_list[i];
            // Tools do not have any business application
            // Workaround this limitation
            if (document_list[i].id.indexOf('portal_') === 0) {
              tool_list.push(document_list[i]);
            } else {
              // Create card if needed
              if (document_list[i].business_application_translated_title !==
                  current_business_application_title) {
                pushNewCard();
                module_list = [];
                current_business_application_title =
                  document_list[i].business_application_translated_title;
              }
              module_list.push(document_list[i]);
            }
          }
          pushNewCard();
          if (other_module_list.length) {
            card_list.push({
              business_application_translated_title: translated_other_title,
              module_list: other_module_list
            });
          }
          if (tool_list.length) {
            card_list.push({
              business_application_translated_title: translated_tool_title,
              module_list: tool_list
            });
          }

          generateCardList(gadget.element.querySelector('ul'), card_list);

          return gadget.updateHeader({
            page_title: 'Modules',
            page_icon: 'puzzle-piece',
            front_url: url_list[i]
          });
        });
    });

}(window, rJS, jIO, RSVP, domsugar));