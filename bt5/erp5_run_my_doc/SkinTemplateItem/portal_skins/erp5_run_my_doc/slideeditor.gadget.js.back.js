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
    // Convert to an Array so that array methods can be used to reorder slides
    return Array.prototype.slice.call(domsugar('div', {
      'class': 'slide_list',
      html: presentation_html
    }).querySelectorAll(':scope > section'));
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
    slide = slide.cloneNode(true);

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

    return result;
  }

  function slideListAsHTML(slide_list) {
    var i,
      result = '';
    for (i = 0; i < slide_list.length; i += 1) {
      result += slide_list[i].outerHTML;
    }
    return result;
  }

  function updateSlideDict(presentation_html, value_dict, slide_index) {
    var slide_list = getSlideElementList(presentation_html),
      slide = getSlideFromList(slide_list, slide_index),
      slide_dict = getSlideDictFromSlideElement(slide),
      i,
      class_string,
      key;

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
    slide.innerHTML = '<h1>' + slide_dict.title_html + '</h1>' +
                      '<details>' + slide_dict.comment_html + '</details>' +
                      slide_dict.slide_html;

    return slideListAsHTML(slide_list);
  }

  ///////////////////////////////////////////////////
  // Page view handling
  ///////////////////////////////////////////////////
  function buildPageTitle(gadget, title_translation) {
    var element_list = [title_translation];
    if (gadget.state.display_index !== null) {
      element_list.push(
        ' ' + (gadget.state.display_index + 1)
        // domsugar('label', {'class': 'page-number',
        //                    text: gadget.state.display_index})
      );
    }
    return domsugar('div', {'class': 'camera-header'}, [
      domsugar('h4', element_list)
    ]);
  }

  function buildSlideButtonList(slide_dialog, disable_previous, disable_next) {
    var button_list = [];
    button_list.push(
      domsugar('button', {
        type: 'button',
        disabled: (slide_dialog === DIALOG_METADATA),
        'class': 'dialog-metadata ui-icon-info-circle ui-btn-icon-left',
        text: 'Metadata'
      }),
      domsugar('button', {
        type: 'button',
        disabled: (slide_dialog === DIALOG_SLIDE),
        'class': 'dialog-slide ui-icon-file-image-o ui-btn-icon-left',
        text: 'Text'
      }),
      domsugar('button', {
        type: 'button',
        disabled: (slide_dialog === DIALOG_COMMENT),
        'class': 'dialog-commenting ui-icon-comment ui-btn-icon-left',
        text: 'Comments'
      }),
      domsugar('button', {
        type: 'button',
        disabled: disable_previous,
        'class': 'previous-btn ui-icon-backward ui-btn-icon-left',
        text: 'Previous'
      }),
      domsugar('button', {
        type: 'button',
        'class': 'list-btn ui-icon-th ui-btn-icon-left',
        text: 'List'
      }),
      domsugar('button', {
        type: 'button',
        disabled: disable_next,
        'class': 'next-btn ui-icon-forward ui-btn-icon-left',
        text: 'Next'
      })
    );
    return button_list;
  }

  ///////////////////////////////////////////////////
  // Page view handling
  ///////////////////////////////////////////////////
  function getCKEditorJSON(key, value) {
    return {
      erp5_document: {
        "_embedded": {
          "_view": {
            "your_slide_content": {
              "title": "XXX Slide Text",
              "type": "GadgetField",
              "url": "gadget_editor.html",
              "renderjs_extra": JSON.stringify({
                "portal_type": "Web Page",
                "content_type": "text/html",
                "editor": "fck_editor",
                "maximize": true
              }),
              "editable": 1,
              "key": key,
              "default": value
            }
          }
        },
        "_links": {
          "type": {
            // form_list display portal_type in header
            name: ""
          }
        }
      },
      form_definition: {
        group_list: [
          ["bottom", [["your_slide_content"]]]
        ]
      }
    };
  }

  function getMetadataJSON(title_html, type) {
    return {
      erp5_document: {
        "_embedded": {
          "_view": {
            "your_chapter_title": {
              "title": "XXX Chapter Title",
              "type": "StringField",
              "editable": 1,
              "required": 1,
              "key": "title_html",
              "value": title_html
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
              value: type
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
          }
        },
        "_links": {
          "type": {
            // form_list display portal_type in header
            name: ""
          }
        }
      },
      form_definition: {
        group_list: [
          ["left", [
            ["your_chapter_title"],
            ["your_slide_type"]
            // ["your_tested"]
          ]]
        ]
      }
    };

  }

  function renderSlideDialog(gadget, slide_dialog, is_updated) {
    var formbox,
      render_dict,
      slide_list = getSlideElementList(gadget.state.value),
      slide_dict = getSlideDictFromSlideElement(
        getSlideFromList(slide_list, gadget.state.display_index)
      ),
      queue;

    if (slide_dialog === DIALOG_SLIDE) {
      render_dict = getCKEditorJSON(
        "slide_html",
        slide_dict.slide_html
      );
    } else if (slide_dialog === DIALOG_COMMENT) {
      render_dict = getCKEditorJSON(
        "comment_html",
        slide_dict.comment_html
      );
    } else if (slide_dialog === DIALOG_METADATA) {
      render_dict = getMetadataJSON(slide_dict.title_html, slide_dict.type);
    } else {
      // Ease developper work by raising for not handled cases
      throw new Error('Unhandled dialog: ' + slide_dialog);
    }

    if (is_updated) {
      queue = gadget.getDeclaredGadget(FORMBOX_SCOPE);
    } else {
      queue = gadget.declareGadget('gadget_erp5_form.html', {
        scope: FORMBOX_SCOPE
      });
    }

    return queue
      .push(function (result) {
        formbox = result;
        return formbox.render(render_dict);
      })
      .push(function () {
        if (is_updated) {
          gadget.element.firstChild.replaceWith(
            buildPageTitle(gadget, 'Slide')
          );
          domsugar(gadget.element.querySelector('div.edit-picture'),
                   {'class': 'edit-picture'},
                   buildSlideButtonList(
              slide_dialog,
              gadget.state.display_index === 0,
              gadget.state.display_index === slide_list.length - 1
            ));
        } else {
          domsugar(gadget.element, [
            buildPageTitle(gadget, 'Slide'),
            domsugar('div', {'class': 'edit-picture'},
                     buildSlideButtonList(
                slide_dialog,
                gadget.state.display_index === 0,
                gadget.state.display_index === slide_list.length - 1
              )),
            formbox.element
          ]);
        }
      });
  }

  function renderSlideList(gadget) {
    // Get the full HTML
    var text_content = gadget.state.value,
      div = domsugar('div', {'class': 'slide_list', html: text_content}),
      section_list = div.querySelectorAll(':scope > section'),
      i;
    for (i = 0; i < section_list.length; i += 1) {
      section_list[i].draggable = true;
      section_list[i].setAttribute('data-slide-index', i);
      section_list[i].appendChild(
        domsugar('button', {type: 'button', text: 'XXX Edit',
                 'class': 'display-slide',
                 'data-slide-index': i})
      );
    }
    // Add the "Add slide" button
    // div.appendChild(domsugar('section', {text: 'Add Slide'}));
    div.appendChild(domsugar('section', [
      domsugar('button', {type: 'button', text: 'XXX Add slide',
                          'class': 'display-new'})
    ]));

    domsugar(gadget.element, [div]);
  }

  ///////////////////////////////////////////////////
  // Gadget
  ///////////////////////////////////////////////////
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
      var gadget = this,
        display_step = gadget.state.display_step,
        queue;

      // First, check if the current display contains a dialog
      // and modify the slide as expected
      if (display_step === DISPLAY_SLIDE) {
        // Save the slide modification
        queue = gadget.getDeclaredGadget(FORMBOX_SCOPE)
          .push(function (formbox_gadget) {
            return formbox_gadget.getContent();
          })
          .push(function (formbox_content_dict) {
            gadget.state.value = updateSlideDict(
              gadget.state.value,
              formbox_content_dict,
              gadget.state.display_index
            );
          });
      } else if ([DISPLAY_LIST].indexOf(display_step) !== -1) {
        queue = new RSVP.Queue();
      } else {
        throw new Error('Display form not handled: ' + display_step);
      }

      return queue
        .push(function () {
          var result = {};
          if (gadget.state.editable) {
            result[gadget.state.key] = gadget.state.value;
          }
          return result;
        });
    }, {mutex: 'statechange'})

    .onStateChange(function (modification_dict) {
      var gadget = this,
        display_step = gadget.state.display_step,
        slide_dialog = gadget.state.slide_dialog;

      if (display_step === DISPLAY_LIST) {
        return renderSlideList(gadget);
      }

      if (display_step === DISPLAY_SLIDE) {
        return renderSlideDialog(
          gadget,
          slide_dialog,
          !(modification_dict.hasOwnProperty('display_step') ||
            modification_dict.hasOwnProperty('slide_dialog'))
        );
      }

      // Ease developper work by raising for not handled cases
      throw new Error('Unhandled display step: ' + display_step);
    })

    .onEvent("click", function (evt) {
      // Only handle click on BUTTON and IMG element
      var gadget = this,
        tag_name = evt.target.tagName,
        queue;

      if (tag_name !== 'BUTTON') {
        return;
      }

      // Always get content to ensure the possible displayed form
      // is checked and content propagated to the gadget state value
      queue = gadget.getContent();

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
              display_index: parseInt(
                evt.target.getAttribute('data-slide-index'),
                10
              ),
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

      throw new Error('Unhandled button: ' + evt.target.textContent);
    }, false, false)

    ///////////////////////////////////////////////////
    // Drag / drop management
    ///////////////////////////////////////////////////
    .onEvent("dragstart", function (evt) {
      var tag_name = evt.target.tagName;
      if (tag_name !== 'SECTION') {
        return;
      }
      // Store index of the dragged slide
      evt.target.classList.add('drag');

      evt.dataTransfer.effectAllowed = 'move';
      evt.dataTransfer.setData('application/x-dragged-slide',
                               evt.target.getAttribute('data-slide-index'));
    }, false, false)

    .onEvent("dragend", function (evt) {
      var tag_name = evt.target.tagName;
      if (tag_name !== 'SECTION') {
        return;
      }
      evt.target.classList.remove('drag');
    }, false, false)

    .onEvent("dragover", function (evt) {
      var tag_name = evt.target.tagName;
      if (tag_name !== 'SECTION') {
        return;
      }
      if (evt.preventDefault) {
        evt.preventDefault(); // Necessary. Allows us to drop.
      }
      evt.dataTransfer.dropEffect = 'move';
    }, false, false)

    .onEvent("dragenter", function (evt) {
      var tag_name = evt.target.tagName;
      if (tag_name !== 'SECTION') {
        return;
      }

      // Provide a visual feedback to the user
      // Showing where the slide can be dropped
      if (evt.target.getAttribute('data-slide-index')) {
        evt.target.classList.add('over');
      }
    }, false, false)

    .onEvent("dragleave", function (evt) {
      var tag_name = evt.target.tagName;
      if (tag_name !== 'SECTION') {
        return;
      }
      evt.target.classList.remove('over');
    }, false, false)

    .onEvent("drop", function (evt) {
      var gadget = this,
        tag_name = evt.target.tagName,
        slide_list,
        source_index,
        destination_index;

      if (tag_name !== 'SECTION') {
        return;
      }

      if (evt.preventDefault) {
        evt.preventDefault(); // Necessary. Allows us to drop.
      }

      // Remove the over class
      evt.target.classList.remove('over');

      source_index = evt.dataTransfer.getData('application/x-dragged-slide');
      if (source_index && evt.target.getAttribute('data-slide-index')) {
        source_index = parseInt(
          source_index,
          10
        );
        destination_index = parseInt(
          evt.target.getAttribute('data-slide-index'),
          10
        );

        slide_list = getSlideElementList(gadget.state.value);
        if (source_index !== destination_index) {
          slide_list.splice(
            destination_index,
            0,
            slide_list.splice(source_index, 1)[0]
          );
          return RSVP.all([
            gadget.changeState({value: slideListAsHTML(slide_list)}),
            gadget.notifyChange()
          ]);
        }
      }
    }, false, false);


}());