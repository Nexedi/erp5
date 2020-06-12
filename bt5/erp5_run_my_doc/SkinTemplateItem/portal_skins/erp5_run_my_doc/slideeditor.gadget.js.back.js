/*global window, document, rJS, console, RSVP, domsugar*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function () {
  "use strict";

  var DISPLAY_LIST = 'display_list',
    DISPLAY_SLIDE = 'display_slide',
    DIALOG_SLIDE = 'dialog_slide',
    DIALOG_COMMENT = 'dialog_comment',
    DIALOG_METADATA = 'dialog_metadata',
    FORMBOX_SCOPE = 'formbox';

  ///////////////////////////////////////////////////
  // Slide format handling
  ///////////////////////////////////////////////////
  function getSlideElementList(presentation_html) {
    return domsugar('div', {
      'class': 'slide_list',
      html: presentation_html
    }).querySelectorAll(':scope > section');
  }

  function getSlideFromList(slide_list, slide_index) {
    // Get the section corresponding to the slide
    if (slide_list.length <= slide_index) {
      throw new Error('No slide: ' + slide_index);
    }
    return slide_list[slide_index];
  }

  function getSlideDictFromSlideElement(slide) {
    var h1,
      details,
      result = {
        type: '',
        title_html: '',
        comment_html: '',
        slide_html: ''
      };

    // Clone the slide,
    // as we will remove the h1/details to calculate the content
    console.log(slide);

    slide = slide.cloneNode(true);
    console.log(slide);
    // console.log(slide.outerHTML);
    // XXX drop img handling for now
    // As it seems it was a hack to allow image upload
    // which is not working anymore in xhtml style

    // Get the first h1 tag
    h1 = slide.querySelector(':scope > h1');
    if (h1 !== null) {
      result.title_html = h1.innerHTML;
      slide.removeChild(h1);
    }

    // Get the slide type
    if (slide.classList.length !== 0) {
      result.type = slide.classList[0];//.toUpperCase();
    }

    // XXX drop test management
    // No idea what it is for now

    // Get the comment
    details = slide.querySelector(':scope > details');
    if (details !== null) {
      result.comment_html = details.innerHTML;
      slide.removeChild(details);
    }

    // Finally, extract the slide
    result.slide_html = slide.innerHTML;

    console.log('slide_dict', result);
    return result;
  }

  function getSlideDict(presentation_html, slide_index) {
    var slide_list = getSlideElementList(presentation_html);
    return getSlideDictFromSlideElement(getSlideFromList(slide_list, slide_index));
  }

  function updateSlideDict(presentation_html, value_dict, slide_index) {
    var slide_list = getSlideElementList(presentation_html),
      slide = getSlideFromList(slide_list, slide_index),
      slide_dict = getSlideDictFromSlideElement(slide),
      i,
      result = '',
      class_string,
      key;

    console.log("XXX", slide_dict, value_dict);
    // Hack: remove keys sent to erp5
    delete value_dict['default_type:int'];
    for (key in value_dict) {
      if (value_dict.hasOwnProperty(key)) {
        if (!slide_dict.hasOwnProperty(key)) {
          throw new Error('Unknown slide property: ' + key);
        }
        slide_dict[key] = value_dict[key];
      }
    }

    class_string = slide_dict.type;
    for (i = 1; i < slide.classList.length; i += 1) {
      class_string += ' ' + slide.classList[i];
    }
    slide.className = class_string;
    slide.innerHTML = '<h1>' + slide_dict.title_html + '</h1>' + '<details>' + slide_dict.comment_html + '</details>' + slide_dict.slide_html;
    console.log(slide);
    for (i = 0; i < slide_list.length; i += 1) {
      result += slide_list[i].outerHTML;
    }
    return result;
  }

  ///////////////////////////////////////////////////
  // Page view handling
  ///////////////////////////////////////////////////
  function buildPageTitle(gadget, title_translation) {
    var element_list = [title_translation];
    if (gadget.state.display_index !== null) {
      element_list.push(
        ' ' + (gadget.state.display_index + 1)
        // domsugar('label', {'class': 'page-number', text: gadget.state.display_index})
      );
    }
    return domsugar('div', {'class': 'camera-header'}, [
      domsugar('h4', element_list)
    ]);
  }

  function buildSlideButtonList(gadget) {
    var button_list = [];
    button_list.push(
      domsugar('button', {
        type: 'button',
        'class': 'dialog-metadata ui-icon-fast-forward ui-btn-icon-left',
        text: 'Metadata'
      }),
      domsugar('button', {
        type: 'button',
        'class': 'dialog-slide ui-icon-fast-forward ui-btn-icon-left',
        text: 'Text'
      }),
      domsugar('button', {
        type: 'button',
        'class': 'dialog-comment ui-icon-fast-forward ui-btn-icon-left',
        text: 'Comments'
      }),
      domsugar('button', {
        type: 'button',
        disabled: (gadget.state.display_index === 0),
        'class': 'previous-btn ui-icon-fast-forward ui-btn-icon-left',
        text: 'Previous'
      }),
      domsugar('button', {
        type: 'button',
        'class': 'list-btn ui-icon-fast-forward ui-btn-icon-left',
        text: 'List'
      }),
      domsugar('button', {
        type: 'button',
        'class': 'next-btn ui-icon-fast-forward ui-btn-icon-left',
        text: 'Next'
      })
    );
    return button_list;
  }

  function renderCommentDialog(gadget) {
    var formbox;

    return gadget.declareGadget('gadget_erp5_form.html', {
      scope: FORMBOX_SCOPE
    })
      .push(function (result) {
        formbox = result;
        return formbox.render({
          erp5_document: {"_embedded": {"_view": {

            "your_slide_content": {
              "title": "XXX Slide Text",
              "type": "GadgetField",
              "url": "gadget_editor.html",
              "renderjs_extra": '{"portal_type": "Web Page", "content_type": "text/html", "editor": "fck_editor", "maximize": true}',
              "editable": 1,
              "key": "comment_html",
              "default": getSlideDict(gadget.state.value, gadget.state.display_index).comment_html//slide.querySelector('details').innerHTML
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
              ["bottom",
                 [["your_slide_content"]
                  ]
              ]
            ]
          }
        });
      })
      .push(function () {
        domsugar(gadget.element, [
          buildPageTitle(gadget, 'Slide'),
          formbox.element,
          domsugar('div', {'class': 'edit-picture'}, buildSlideButtonList(gadget)),
          // domsugar('button', {type: "button", text: "Add", class: "add-slide"})
        ]);
      });
  }


  function renderSlideDialog(gadget) {
    var formbox;

    return gadget.declareGadget('gadget_erp5_form.html', {
      scope: FORMBOX_SCOPE
    })
      .push(function (result) {
        formbox = result;
        return formbox.render({
          erp5_document: {"_embedded": {"_view": {

            "your_slide_content": {
              "title": "XXX Slide Text",
              "type": "GadgetField",
              "url": "gadget_editor.html",
              "renderjs_extra": '{"portal_type": "Web Page", "content_type": "text/html", "editor": "fck_editor", "maximize": true}',
              "editable": 1,
              "key": "slide_html",
              "default": getSlideDict(gadget.state.value, gadget.state.display_index).slide_html//slide.querySelector('details').innerHTML
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
              ["bottom",
                 [["your_slide_content"]
                  ]
              ]
            ]
          }
        });
      })
      .push(function () {
        domsugar(gadget.element, [
          buildPageTitle(gadget, 'Slide'),
          formbox.element,
          domsugar('div', {'class': 'edit-picture'}, buildSlideButtonList(gadget)),
          // domsugar('button', {type: "button", text: "Add", class: "add-slide"})
        ]);
      });
  }

  function renderMetadataDialog(gadget) {
    var formbox;

    return gadget.declareGadget('gadget_erp5_form.html', {
      scope: FORMBOX_SCOPE
    })
      .push(function (result) {
        formbox = result;
        var slide_dict = getSlideDict(gadget.state.value, gadget.state.display_index);
        return formbox.render({
          erp5_document: {"_embedded": {"_view": {
            "your_chapter_title": {
              "title": "XXX Chapter Title",
              "type": "StringField",
              "editable": 1,
              "required": 1,
              "key": "title_html",
              "value": slide_dict.title_html
            },
            "your_slide_type": {
              "title": "XXX Type of Slide",
              "type": "ListField",
              "editable": 1,
              "key": "type",
              items: [["", ""],
                      ["Chapter", "chapter"],
                      ["Screenshot", "screenshot"],
                      ["Illustration", "illustration"],
                      ["Code", "code"],
                      ["Master", "master"]
                     ],
              value: slide_dict.type
              /*
            },
            "your_tested": {
              "title": "XXX Does it Contain a Test?",
              "type": "CheckBoxField",
              "editable": 1,
              "key": "field_your_tested",
              "default": "eee",
              "required": 0,
              "hidden": 0
              */
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
                  // ["your_tested"]
                  ]
              ]
            ]
          }
        });

      })
      .push(function () {
        domsugar(gadget.element, [
          buildPageTitle(gadget, 'Slide'),
          formbox.element,
          domsugar('div', {'class': 'edit-picture'}, buildSlideButtonList(gadget)),
          // domsugar('button', {type: "button", text: "Add", class: "add-slide"})
        ]);
      });
  }

  ///////////////////////////////////////////////////
  // Page view handling
  ///////////////////////////////////////////////////
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

  function renderSlideList(gadget) {
    // Get the full HTML
    var text_content = gadget.state.value,
      div = domsugar('div', {class: 'slide_list', html: text_content}),
      section_list = div.querySelectorAll(':scope > section'),
      i;
    for (i = 0; i < section_list.length; i += 1) {
      section_list[i].appendChild(
        domsugar('button', {type: 'button', text: 'XXX Edit',
                 class: 'display-slide',
                 'data-slide-index': i})
      );
    }
    // Add the "Add slide" button
    // div.appendChild(domsugar('section', {text: 'Add Slide'}));
    div.appendChild(domsugar('section', [
      domsugar('button', {type: 'button', text: 'XXX Add slide',
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
      display_step: DISPLAY_LIST,
      display_index: null,
      slide_dialog: null
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

    .onStateChange(function (modification_dict) {
      var gadget = this,
        display_step = gadget.state.display_step,
        slide_dialog = gadget.state.slide_dialog;

      if (display_step === DISPLAY_LIST) {
        return renderSlideList(gadget);
      }
/*
      if (display_step === 'display_new_slide') {
        return renderNewSlideDialog(gadget);
      }
*/

      if (display_step === DISPLAY_SLIDE) {
        if (slide_dialog === DIALOG_SLIDE) {
          return renderSlideDialog(gadget, modification_dict.hasOwnProperty('display_step'));
        }
        if (slide_dialog === DIALOG_COMMENT) {
          return renderCommentDialog(gadget, modification_dict.hasOwnProperty('display_step'));
        }
        if (slide_dialog === DIALOG_METADATA) {
          return renderMetadataDialog(gadget, modification_dict.hasOwnProperty('display_step'));
        }
        // Ease developper work by raising for not handled cases
        throw new Error('Unhandled dialog: ' + slide_dialog);
      }

      // Ease developper work by raising for not handled cases
      throw new Error('Unhandled display step: ' + display_step);
    })

    .onEvent("click", function (evt) {
      // Only handle click on BUTTON and IMG element
      var gadget = this,
        tag_name = evt.target.tagName,
        state_dict,
        queue,
        display_step = gadget.state.display_step,
        slide_dialog = gadget.state.slide_dialog;

      if (tag_name !== 'BUTTON') {
        return;
      }

      // First, check if the current display contains a dialog
      // and modify the slide as expected
      if (display_step === DISPLAY_SLIDE) {
        // Save the slide modification
        // XXX Protect with the onstatechange mutex
        queue = gadget.getDeclaredGadget(FORMBOX_SCOPE)
          .push(function (formbox_gadget) {
            return formbox_gadget.getContent();
          })
          .push(function (formbox_content_dict) {
            gadget.state.value = updateSlideDict(gadget.state.value, formbox_content_dict, gadget.state.display_index);
            // console.log(formbox_content_dict);
            // throw new Error('Dialog not handled: ' + slide_dialog + formbox_content_dict);
          });
      } else if ([DISPLAY_LIST].indexOf(display_step) === -1) {
        throw new Error('Display form not handled: ' + display_step);
      } else {
        queue = new RSVP.Queue();
      }

      // Actions from slide list

      // Actions from a slide dialog
      if (evt.target.className.indexOf("next-btn") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              display_index: gadget.state.display_index + 1
            });
          });
      }

      if (evt.target.className.indexOf("previous-btn") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              display_index: gadget.state.display_index - 1
            });
          });
      }

      if (evt.target.className.indexOf("list-btn") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              display_step: DISPLAY_LIST
            });
          });
      }

      if (evt.target.className.indexOf("display-slide") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              display_step: DISPLAY_SLIDE,
              display_index: parseInt(evt.target.getAttribute('data-slide-index'), 10),
              slide_dialog: gadget.state.slide_dialog || DIALOG_SLIDE
            });
          });
      }

      if (evt.target.className.indexOf("dialog-metadata") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              slide_dialog: DIALOG_METADATA
            });
          });
      }

      if (evt.target.className.indexOf("dialog-comment") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              slide_dialog: DIALOG_COMMENT
            });
          });
      }

      if (evt.target.className.indexOf("dialog-slide") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              slide_dialog: DIALOG_SLIDE
            });
          });
      }

      if (evt.target.className.indexOf("display-new") !== -1) {
        // XXX add <section><h1></h1><details></details></section>
        // XXX notifyChange
        return queue
          .push(function () {
            return gadget.changeState({
              display_index: getSlideElementList(gadget.state.value).length,
              display_step: DISPLAY_SLIDE,
              slide_dialog: gadget.state.slide_dialog || DIALOG_SLIDE,
              value: gadget.state.value + "<section></section>"
            });
          });
      }

/*
      if (evt.target.className.indexOf("add-slide") !== -1) {
        return addSlide(gadget)
          .push(function () {
            return gadget.changeState({
              display_step: 'display_list'
            });
          });
      }
*/
      throw new Error('Unhandled button: ' + evt.target.textContent);
    }, false, false);


}());