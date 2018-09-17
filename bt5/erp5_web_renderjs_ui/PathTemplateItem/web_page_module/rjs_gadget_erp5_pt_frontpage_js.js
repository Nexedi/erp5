/*global window, rJS, jIO, RSVP, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
(function (window, rJS, jIO, RSVP, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    card_list_template_source = gadget_klass.__template_element
                         .getElementById("card-list-template")
                         .innerHTML,
    card_list_template = Handlebars.compile(card_list_template_source);

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translate", "translate")
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
        query: '(parent_uid:"0" AND meta_type:"ERP5 Folder" AND id:"%_module")',
        limit: 1000
      })
        .push(function (result_list) {
          // ERP5 catalog can't sort by translated property
          // Sort manually with jIO
          var data_rows = [],
            i,
            len = result_list.data.total_rows;
          for (i = 0; i < len; i += 1) {
            // queries do not accept null value
            result_list.data.rows[i].value
                                       .business_application_translated_title =
              result_list.data.rows[i].value
                            .business_application_translated_title || '';
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
              command: 'display_stored_state',
              options: {jio_key: document_list[i].id}
            });
          }
          // Add global url calculation
          url_dict_list.push({command: 'display'});
          // Add change language url calculation
          url_dict_list.push({command: 'display', options: {page: 'language'}});
          return RSVP.all([
            document_list,
            gadget.translate('Others'),
            gadget.getUrlForList(url_dict_list)
          ]);
        })
        .push(function (result_list) {
          var document_list = result_list[0],
            translated_other_title = result_list[1],
            url_list = result_list[2],
            len = document_list.length,
            i,
            card_list = [],
            module_list = [],
            other_module_list = [],
            current_business_application_title = '';

          function pushNewCard() {
            if (module_list) {
              if (current_business_application_title === '') {
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
          pushNewCard();
          if (other_module_list.length) {
            card_list.push({
              business_application_translated_title: translated_other_title,
              module_list: other_module_list
            });
          }
          gadget.element.querySelector('ul').innerHTML = card_list_template({
            card_list: card_list
          });

          return gadget.updateHeader({
            page_title: 'Modules',
            page_icon: 'puzzle-piece',
            front_url: url_list[i],
            language_url: url_list[i + 1]
          });
        });
    });

}(window, rJS, jIO, RSVP, Handlebars));