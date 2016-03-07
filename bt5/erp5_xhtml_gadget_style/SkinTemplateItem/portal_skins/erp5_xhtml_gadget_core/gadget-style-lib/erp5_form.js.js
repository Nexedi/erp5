/*
  Form field renderer.
  Note: This is an ERP5 form implementation for the moment.
*/

var ERP5Form = ( function () {
  
  var CURRENT_FORM_ID = "";
  
  return {

          // elements marked with this class can be serialized to server
          SERIALIZE_ABLE_CLASS_NAME: "serialize-able",

          getCurrentFormId: function () {
                            /* Get current form ID (return hard coded one for now) */
                            return CURRENT_FORM_ID;
          },

          setCurrentFormId: function (form_id) {
                            /* Set current form ID (return hard coded one for now) */
                            CURRENT_FORM_ID = form_id;
          },

          getFieldId: function(field_id) {
                      /* Generate local form field id */
                      return "field_" + field_id;
          },

          updateField: function (dom, field_dict) {
                      /* General purpose field updater */
                      var editable;
                      editable = Boolean(field_dict.editable);
                      if (editable){
                        dom.val(field_dict.value);}
                      else{
                        // if field is not editable just show its value
                        dom.replaceWith(field_dict.value);
                      }
          },

          addOptionTagList: function (select_dom, item_list, field_value) {
                      /*
                      * Update select like dom element
                      */
                      $.each(item_list, function (index, value){
                          if(value[1]===field_value) {
                            select_dom.append('<option selected value="' + value[1] + '">'  + value[0] + '</option>');
                          }
                          else {
                            select_dom.append('<option value="' + value[1] + '">'  + value[0] + '</option>');
                          }
                        });
          },

          addOptionTagDictList: function (select_dom, item_list) {
                      /*
                      * Update select like dom element now using dict in this format:
                      * [{'selected': True, 'id': 'en', 'title': 'English'}, 
                      *  {'selected': False, 'id': 'fr', 'title': 'French'}]
                      */
                      $.each(item_list, function (index, value){
                          if(value.selected===true) {
                            select_dom.append('<option selected value="' + value.id + '">'  + value.title + '</option>');
                          }
                          else {
                            select_dom.append('<option value="' + value.id + '">'  + value.title + '</option>');
                          }
                        });
          },

          BaseInputField: function (field_id, field_dict) {
                      /* HTML based input field */
                      var dom, display_width;
                      dom = $("[name=" + this.getFieldId(field_id) + "]");
                      this.updateField(dom, field_dict);
                      display_width = field_dict.display_width;
                      if (display_width){
                        dom.attr("size", display_width);}
                      return dom;
          },

          EditorField: function (field_id, field_dict) {
                      /* HTML based input field */
                      var dom;
                      dom = $("#" + this.getFieldId(field_id));
                      this.updateField(dom, field_dict);
                      return dom;
          },

          ListField: function (field_id, field_dict) {
                      /* Select field */
                      var field_value, select_dom;
                      field_value = field_dict.value;
                      select_dom = $("select[name=" + this.getFieldId(field_id) + "]");
                      this.addOptionTagList(select_dom, field_dict.items, field_value);
                      return select_dom;
          },

          ParallelListField: function (field_id, field_dict) {
                      /* mutiple select fields */
                      var tag_name = "subfield_field_" + field_id + "_default",
                          initial_select_dom = $("select[name="+ tag_name + "\\:list]"),
                          gadget = initial_select_dom.parent("div[data-gadget]"),
                          new_select_id;
                      // render first value in initial select box
                      ERP5Form.addOptionTagList(initial_select_dom, field_dict.items, field_dict.value[0]);

                      // render all other elements
                      $.each(field_dict.value, function (index, index_value) {
                        if (index !== 0) {
                          // we need to create dynamically a select box for all element except first
                          new_select_id = 'parallel_' + field_id + index;
                          gadget.append('<br/><select class="serialize-able" name=' + tag_name + ':list ' + 'id=' + new_select_id + '></select>');
                          ERP5Form.addOptionTagList($("#"+new_select_id), field_dict.items, index_value);
                        }
                      });

                      // add a new select with all values under main one with already selected 
                      if (field_dict.value.length > 0) {
                        // we need to add another select if initial one is empty
                        new_select_id = 'parallel_last' + field_id;
                        gadget.append('<br/><select class="dynamic serialize-able" name=' + tag_name + ':list ' + 'id=' + new_select_id + '></select>');
                        ERP5Form.addOptionTagList($("#"+new_select_id), field_dict.items, '');
                      }
                      return initial_select_dom;
          },

          CheckBoxField: function (field_id, field_dict) {
                      /* CheckBoxField field */
                      var checked, checkbox_dom;
                      checked = Boolean(field_dict.value);
                      checkbox_dom = $("input[name=" + this.getFieldId(field_id) + "]");
                      if (checked) {
                          checkbox_dom.attr('checked', true);
                      }
                      return checkbox_dom;
          },

          TextAreaField: function (field_id, field_dict) {
                      /* TextArea field */
                      return this.BaseInputField(field_id, field_dict);
          },

          StringField: function (field_id, field_dict) {
                      /* String field */
                      return this.BaseInputField(field_id, field_dict);
          },

          IntegerField: function (field_id, field_dict) {
                      /* Int field */
                      return this.BaseInputField(field_id, field_dict);
          },

          PasswordField: function (field_id, field_dict) {
                      /* PasswordField field */
                      return this.BaseInputField(field_id, field_dict);
          },

          DateTimeField: function (field_id, field_dict) {
                      /* DateTimeField field */
                      var date, dom, date_format;
                      dom = $("[name=" + this.getFieldId(field_id) + "]");
                      date = field_dict.value;
                      date_format = field_dict['format'];
                      if (date_format==="dmy") {
                        // XXX: support more formats
                        date_format = 'dd/mm/yy';
                      }
                      date = new Date(date);
                      dom.datepicker({ dateFormat: date_format});
                      dom.datepicker('setDate', date);
                      return dom;
          },

          EmailField: function (field_id, field_dict) {
                      /* Email field */
                      return this.BaseInputField(field_id, field_dict);
          },

          FloatField: function (field_id, field_dict) {
                      /* Float field */
                      return this.BaseInputField(field_id, field_dict);
          },

          FormBox: function (field_id, field_dict) {
                      /* FormBox field */
                      // XXX: implement it to read all values and render properly
                      return this.BaseInputField(field_id, field_dict);
          },

          RelationStringField: function (field_id, field_dict) {
                      /* Relation field */
                      return this.BaseInputField(field_id, field_dict);
          },

          MultiRelationStringField: function (field_id, field_dict) {
                      /* MultiRelationStringField field */
                      // XXX: support multiple values
                      return this.BaseInputField(field_id, field_dict);
          },

          ImageField:  function (field_id, field_dict) {
                      /* Image field */
                      var dom;
                      dom = $("img[name=" + this.getFieldId(field_id) + "]");
                      // XXX: image field should return details like quality, etc ...
                      dom.attr("src", field_dict.value + "?quality=75.0&display=thumbnail&format=png");
          },

          ListBox:  function (field_id, field_dict) {
                      /*
                       * Listbox field rendered at server
                       */
                      var listbox_id, navigation_id, listbox_table, current_form_id, listbox_dict,
                          listbox_data_url, colModel, column_title_list;
                      listbox_id = "field_" + field_id;
                      navigation_id = listbox_id + "_pager";
                      listbox_table = $("#"+listbox_id + "_table");
                      current_form_id = this.getCurrentFormId();
                      listbox_dict = field_dict.listbox;
                      listbox_data_url = listbox_dict.listbox_data_url;
                      $("#" + listbox_id + "_field").html(listbox_dict["listbox_html"]);
                      return;
          },

          ListBoxJavaScript:  function (field_id, field_dict) {
                      /*
                       * Listbox field rendered entirely at client side using jqgrid plugin
                       */
                      var listbox_id, navigation_id, listbox_table, current_form_id, listbox_dict,
                          listbox_data_url, colModel, column_title_list;
                      listbox_id = "field_" + field_id;
                      navigation_id = listbox_id + "_pager";
                      listbox_table = $("#"+listbox_id);
                      current_form_id = this.getCurrentFormId();
                      listbox_dict = field_dict.listbox;
                      listbox_data_url = listbox_dict.listbox_data_url;
                      colModel = [];
                      column_title_list = [];
                      $.each(listbox_dict.columns,
                              function(i, value){
                                var index, title, column;
                                index = value[0];
                                title = value[1];
                                column_title_list.push(title);
                                column = {'name': index,
                                          'index': index,
                                          'width': 185,
                                          'align': 'left'};
                                colModel.push(column);
                      });

                      listbox_table.jqGrid({url:listbox_data_url + '?form_id=' + current_form_id + '&amps;listbox_id=' + field_id,
                                    datatype: "json",
                                    colNames:  column_title_list,
                                    colModel: colModel,
                                    rowNum: listbox_dict.lines,
                                    pager: '#'+navigation_id,
                                    sortname: 'id',
                                    viewrecords: true,
                                    sortorder: "desc",
                                    loadError : function(xhr, textStatus, errorThrown)  {
                                                  // XXX: handle better than just alert.
                                                  alert("Error occurred during getting data from server.");
                                                  },
                                    cmTemplate: {sortable:false}, // XXX: until we get list of sortable columns from server
                                    caption: field_dict.title});
                      listbox_table.jqGrid('navGrid', '#'+navigation_id, {edit:false,add:false,del:false});
                      return listbox_table;
          },

          update: function(data) {
                      /* Update form values */
                      $.each(data.form_data,
                            function(field_id, field_dict){
                                var type=field_dict.type,
                                    dom;
                                if(ERP5Form.hasOwnProperty(type)){
                                  dom = ERP5Form[type](field_id, field_dict);
                                }

                                // add a class that these fields are editable so asJSON
                                // can serialize for for sending to server
                                if (dom!==undefined && dom!==null && field_dict.editable){
                                  dom.addClass(ERP5Form.SERIALIZE_ABLE_CLASS_NAME);
                                }

                                // mark required fields visually
                                if (field_dict.required){
                                  //dom.parent().parent().parent().children("label").css("font-weight", "bold");}
                                  dom.parent().parent().parent().addClass("required-field");
                                }

                              });
          },

          save: function(){
                      /* save form to server*/
                      var form_value_dict, converted_value;
                      form_value_dict = {};
                      $("." + ERP5Form.SERIALIZE_ABLE_CLASS_NAME).each(function(index){
                        // DOM can change values, i.e. alter checkbox (on / off)
                        var element = $(this),
                            name = element.attr("name"),
                            value = element.val(),
                            type = element.attr("type"),
                            element_class = element.attr("class");

                        if (type === "checkbox") {
                          value = element.is(":checked");
                          if (value === true) {
                            converted_value=1;
                          }
                          if (value === false) {
                            converted_value=0;
                          }
                          value = converted_value;
                        }
                        if (element_class.indexOf("hasDatepicker") !== -1) {
                            // backend codes expects that date object is represented by
                            // three separate request parameters so created them here.
                            // XXX: we assume format is dd/mm/YYYY so read it from DateTimeGadget for this field
                            // which means we now must be able get hold of gadget and read it from there where
                            // fist it should be initialized!)
                            form_value_dict["subfield_" + name + "_year"] = value.substr(6,4);
                            form_value_dict["subfield_" + name + "_month"] = value.substr(3,2);
                            form_value_dict["subfield_" + name + "_day"] = value.substr(0,2);
                        }

                        // XXX: how to handle file uploads ?

                        // some values end with :list and we need to collect them all
                        if (/:list$/.test(name)) {
                          if (form_value_dict[name] === undefined) {
                            // init it
                            form_value_dict[name] = [];
                            //console.log("init", name);
                          }
                          form_value_dict[name].push(value);
                          //console.log("set", name, form_value_dict[name]);
                        }
                        else {
                          // single value
                          form_value_dict[name] = value;
                        }
                      });
                      //console.log(form_value_dict);

                      // add form_id as we need to know structure we're saving at server side
                      form_value_dict.form_id = ERP5Form.getCurrentFormId();

                      // validation happens at server side
                      $.ajax({url:'Form_save',
                              data: form_value_dict,
                              dataType: "json",
                              // it's important for Zope to have traditional way of encoding an URL
                              traditional: 1,
                              success: function (data) {
                                var field_errors;
                                field_errors = data.field_errors;
                                if (field_errors!==undefined){
                                  //console.log(field_errors);
                                  $.each(field_errors, function(index, value){
                                      var dom, field;
                                      dom = $("[name=" + ERP5Form.getFieldId(index) + "]");
                                      dom.addClass("validation-failed");
                                      field = dom.parent().parent();
                                      if (field.children("span.error").length > 0){
                                        // just update message
                                        field.children("span.error").html(value);}
                                      else{
                                        // no validation error message exists
                                        field.append('<span class="error">' + value + '</span>');}
                                    }
                                  );}
                                else{
                                  // validation OK at server side
                                  $("span.error").each(function(index) {
                                    // delete validation messages
                                    var element;
                                    element = $(this);
                                    element.remove();
                                    // XXX: remove all rendered in red input classes
                                    $(".validation-failed").each(function () {
                                      $(this).removeClass("validation-failed");
                                    });
                                  });
                                  // show a fading portal_status_message
                                  RenderJs.GadgetIndex.getGadgetById('portal_status_message').showMessage("Saved", 1000);
                                }
                              }});
          },

        onTabClickHandler: function (form_id) {
          /*
           * When a tab gets clicked change url (part after '#') so router can detect
            change and load proper gadget.
            This function preserves all URL arguments.
          */
          window.location = window.location.toString().split('#')[0] + '#/'+form_id + '/';
          return false;
        },

        openFormInTabbularGadget: function (container_id, form_id) {
          /*
          * Open a new tab containing an ERP5 form using RenderJs's TabbularGadget API.
          */
          if (RenderJs.GadgetIndex.getGadgetById('gadget-' + form_id) === undefined) {
            // do not load already existing tab gadget
            RenderJs.TabbularGadget.addNewTabGadget(
              container_id,
              'gadget-' + form_id,
              form_id + '/Form_asRenderJSGadget',
              'ERP5Form.update',
              'Form_asJSON?form_id=' + form_id);
            RenderJs.TabbularGadget.toggleVisibility($('#' + form_id));
            ERP5Form.setCurrentFormId(form_id);
            // when all gadgets are loaded adjust left and right side of forms to have same height
            RenderJs.bindReady(function () {
              setTimeout(function() {
                var left_height = $('fieldset.left').height(),
                    right_height = $('fieldset.right').height();
                  if (right_height <= left_height) {
                    $('fieldset.right').height(left_height);
                  }
                  else {
                    $('fieldset.left').height(right_height);
                  }
                }, 500);
            });
          }
        }

  };} ());
