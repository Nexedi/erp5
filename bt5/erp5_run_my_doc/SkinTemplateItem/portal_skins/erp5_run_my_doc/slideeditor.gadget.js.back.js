/*global window, document, rJS, console, RSVP, domsugar*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function () {
  "use strict";

  function addSlide(gadget) {
    return gadget.getDeclaredGadget('formbox')
      .push(function (formbox) {
        return formbox.getContent();
      })
      .push(function (result) {
        console.log(gadget.state);
        console.log(result);
        var section = domsugar('section', {
          class: result.field_your_slide_type,
          html: result.field_your_slide_content
        });
        section.insertBefore(
          domsugar('h1', {html: result.field_your_chapter_title}),
          section.firstChild
        );
        section.appendChild(domsugar(null, [
          domsugar('details', {open: "true", html: result.field_your_text_content})
        ]));
        gadget.state.value += section.outerHTML;
/*
        $('input[name="field_your_upload_image"]', addSlideIframeContents).click(function() {updateUploadImageInput(addSlideIframeContents);});
        $('select[name="field_your_slide_type"]', addSlideIframeContents).change(function() {updateImageInput(addSlideIframeContents);});
        var submit_button = $("#dialog_submit_button", addSlideIframeContents).click(function(){
          var section = document.createElement("section");
          var className = $('select[name="field_your_slide_type"]', addSlideIframeContents).val();
          $(section).addClass(className.toLowerCase());
          var title = document.createElement("h1");
          $(title).html($('input[name="field_your_chapter_title"]', addSlideIframeContents).val());
          var details = document.createElement("details");
          $(details).attr("open", "true")
          $(details).html($('textarea[name="field_your_text_content"]', addSlideIframeContents).val());
          $(section).append($(title));
          var image_id = "";
          var isScreenshot = className == 'Screenshot';
          
          // Append a new slide, update HTML Code
          function appendSection(){
            $(section).append($('textarea[name="field_your_slide_content"]', addSlideIframeContents).val());
            $(section).append($(details));
            var isTested = $('input[name="field_your_tested"]', addSlideIframeContents).attr('checked');
            if((isTested == 'checked' || isTested) && (image_id != "")){
              var test = createTest();
              appendTestLine(test, "selectAndWait", "name=select_module", "label=Test Pages");
              appendTestLine(test, "verifyTextPresent", "Test Pages", "");            
              if(isScreenshot){
                appendTestLine(test, "captureEntirePageScreenshot", image_id, "");
              }
              $(section).append(test);
            } 
            slideList.append($(section));
            var i = 0;
            if ($('#list > .edit_slide_button').length > 0) {
              var i = parseInt($('#list > .edit_slide_button').filter(':last').attr('id').split('_')[2]) + 1;
            }
            appendSlideButtons(section, i);
            $('#remove_slide_' + i).click(function() {removeClick(this);});
            $('#edit_slide_' + i).click(function() {editClick(this);});
            $(section).hover(function() {slideHover(this);}, function(){slideOut(this);}).mousedown(function() {slideOut(this);});
            updateTextContent();
          }
          if(isScreenshot || className == 'Illustration') {
            image = createNewImageTag(addSlideIframeContents);
            image_id = "";
            if (!isUrl(image.attr('src'))) {
              image_id = image.attr('src');
            }
            $(section).append(image);
          }
          appendSection();
*/
      });
  }

  function renderNewSlideDialog(gadget) {
    var formbox;
    return gadget.declareGadget('gadget_erp5_form.html', {
      scope: 'formbox'
    })
      .push(function (result) {
        formbox = result;
        return formbox.render({
          erp5_document: {"_embedded": {"_view": {
            "your_chapter_title": {
              "title": "XXX Chapter Title",
              "type": "StringField",
              "editable": 1,
              "required": 1,
              "key": "field_your_chapter_title"
            },
            "your_slide_type": {
              "title": "XXX Type of Slide",
              "type": "ListField",
              "editable": 1,
              "key": "field_your_slide_type",
              items: [["", ""],
                      ["Chapter", "Chapter"],
                      ["Screenshot", "Screenshot"],
                      ["Illustration", "Illustration"],
                      ["Code", "Code"],
                      ["Master", "Master"]
                     ]
            },
            "your_slide_content": {
              "title": "XXX Slide Text",
              "type": "GadgetField",
              "url": "gadget_editor.html",
              "renderjs_extra": '{"portal_type": "Web Page", "content_type": "text/html", "editor": "fck_editor", "maximize": true}',
              "editable": 1,
              "key": "field_your_slide_content"
            },
            "your_text_content": {
              "title": "XXX Text",
              "type": "GadgetField",
              "url": "gadget_editor.html",
              "renderjs_extra": '{"portal_type": "Web Page", "content_type": "text/html", "editor": "fck_editor", "maximize": true}',
              "editable": 1,
              "key": "field_your_text_content"
            },
            "your_tested": {
              "title": "XXX Does it Contain a Test?",
              "type": "CheckBoxField",
              "editable": 1,
              "key": "field_your_tested",
              "default": "eee",
              "required": 0,
              "hidden": 0
            },
            "listbox_test_result": {
              "column_list": [
                ['title', 'Title'],
                ['string_index', 'Result']
              ],
              "show_anchor": 0,
              "default_params": {},
              "editable": 1,
              "editable_column_list": [],
              "key": "field_listbox_test_result",
              "lines": 5,
              "list_method": "portal_catalog",
              "query": "urn:jio:allDocs?query=portal_type%3A%22Test%20Result%22",
              "portal_type": ["Test Result"],
              "search_column_list": [],
              "sort_column_list": [],
              "sort": [],
              "title": "Latest Test Results",
              "type": "ListBox"
            }
          }},
            "_links": {
              "type": {
                // form_list display portal_type in header
                name: ""
              }
            }},
          form_definition: {
            group_list: [
              ["left",
                 [["your_chapter_title"],
                  ["your_slide_type"],
                  ["your_slide_content"],
                  ["your_text_content"],
                  ["your_tested"]
                  ]
               /*
              ],
              [
                "bottom",
                [["listbox_test_result"]]
                */
              ]
            ]
          }
        });
      })
      .push(function () {
        domsugar(gadget.element, [
          'taboulet 2',
          formbox.element,
          domsugar('button', {type: "button", text: "Add", class: "add-slide"})
        ]);
      });
    // Instanciate form box
    // Show
  }

  function renderSlideList(gadget) {
    // Get the full HTML
    var text_content = gadget.state.value,
      div = domsugar('div', {class: 'slide_list', html: text_content});
    // Add the "Add slide" button
    // div.appendChild(domsugar('section', {text: 'Add Slide'}));
    div.appendChild(domsugar('section', [
      domsugar('button', {type: 'button', text: 'Add slide',
                          class: 'display-new'})
    ]));

    console.log(text_content);
    domsugar(gadget.element, [div]);
  }

  rJS(window)
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareJob("deferNotifyChange", function () {
      // Ensure error will be correctly handled
      return this.notifyChange();
    })

    .setState({
      display_step: 'display_list',//'display_list',
      display_index: null
    })


    .declareMethod('render', function (options) {
      return this.changeState({
        key: options.key,
        value: options.value || "",
        editable: options.editable === undefined ? true : options.editable
      });
    })

    .declareMethod('getContent', function () {
      var result = {};
      if (this.state.editable) {
        result[this.state.key] = this.state.value;
      }
      console.log('getcontent', result);
      return result;
    })

    .onStateChange(function () {
      var gadget = this,
        display_step = gadget.state.display_step;

      if (display_step === 'display_list') {
        return renderSlideList(gadget);
      }

      if (display_step === 'display_new_slide') {
        return renderNewSlideDialog(gadget);
      }

      // Ease developper work by raising for not handled cases
      throw new Error('Unhandled display step: ' + display_step);
    })

    .onEvent("click", function (evt) {
      // Only handle click on BUTTON and IMG element
      var gadget = this,
        tag_name = evt.target.tagName,
        state_dict;

      if (tag_name !== 'BUTTON') {
        return;
      }

      if (evt.target.className.indexOf("display-new") !== -1) {
        return gadget.changeState({
          display_step: 'display_new_slide'
        });
      }

      if (evt.target.className.indexOf("add-slide") !== -1) {
        return addSlide(gadget)
          .push(function () {
            return gadget.changeState({
              display_step: 'display_list'
            });
          });
      }

      throw new Error('Unhandled button: ' + evt.target.textContent);
    }, false, false);


}());