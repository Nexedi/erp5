// Contains ERP5 UI's build javascript code

var ERP5UI = ( function () {

  function addOptionTagDict(dom, list) {
    $.each(list, function (index,value) {
      if (value.url!==undefined) {
        dom.append('<option value="' + value.url + '">'  + value.title + '</option>');
      }
      else {
          dom.append('<option disabled="disabled">-- '  + value.title + ' --</option>');
      }
    });
  }
  return {

    updateNavigationBox: function () {
      /*
       * Used by navigation_box gadget. Added here to reduce number of .js files.
       */
      $.ajax({
              url: "ERP5Site_getNavigationBoxActionList",
              dataType: "json",
              success: function (data) {
                        var module_dom = $('select[name="select_module"]'),
                            search_type_dom = $('select[name="field_your_search_portal_type"]'),
                            language_dom = $('select[name="select_language"]'),
                            favorite_dom = $('select[name="select_favorite"]');
                        ERP5Form.addOptionTagList(module_dom, data.module_list, "");
                        ERP5Form.addOptionTagList(search_type_dom, data.search_portal_type_list, "");
                        ERP5Form.addOptionTagDictList(language_dom, data.language_list);

                        // add global actions
                        addOptionTagDict(favorite_dom, data.favourite_dict.ordered_global_action_list);
                        // add user action
                        favorite_dom.append('<option disabled="disabled">-- User --</option>');
                        addOptionTagDict(favorite_dom, data.favourite_dict.user_action_list);
                     }
          });
    },

    updateContextBox: function () {
      /*
       * Used by context_box gadget. Added here to reduce number of .js files.
       */
      $.ajax({
              url: "ERP5Site_getContextBoxActionList",
              dataType: "json",
              success: function (data) {
                        var jump_dom = $('select[name="select_jump"]'),
                            action_dom = $('select[name="select_action"]');
                            console.log(data);
                        addOptionTagDict(jump_dom, data.object_jump_list);
                        addOptionTagDict(jump_dom, data.type_info_list);
                        addOptionTagDict(jump_dom, data.workflow_list);
                        addOptionTagDict(action_dom, data.visible_allowed_content_type_list);
                        addOptionTagDict(action_dom, data.document_template_list);
                        addOptionTagDict(action_dom, data.object_workflow_action_list);
                        addOptionTagDict(action_dom, data.object_action_list);
                        addOptionTagDict(action_dom, data.object_view_list);
                        addOptionTagDict(action_dom, data.folder_action_list);
                     }
          });
    }

}} ());



