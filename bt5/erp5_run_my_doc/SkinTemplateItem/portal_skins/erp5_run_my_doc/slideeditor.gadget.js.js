/*global window, document, rJS, console, RSVP, domsugar*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function () {
  "use strict";

  var DISPLAY_LIST = 'display_list',
    DISPLAY_SLIDE = 'display_slide',
    DIALOG_SLIDE = 'dialog_slide',
    DIALOG_COMMENT = 'dialog_comment',
    FORMBOX_SCOPE = 'formbox',
    TRANSLATABLE_WORD_LIST = [
      'Slides',
      'Edit',
      'New Slide',
      'Slide',
      'Delete',
      'Text',
      'Comments',
      'Previous',
      'List',
      'Next',
      'Chapter Title',
      'Type of Slide',
      'Slide Text',
      'Chapter',
      'Screenshot',
      'Illustration',
      'Code',
      'Master'
    ];

  ///////////////////////////////////////////////////
  // translation
  ///////////////////////////////////////////////////
  function getTranslationDict(gadget) {
    return gadget.getTranslationList(TRANSLATABLE_WORD_LIST)
      .push(function (word_list) {
        var result_dict = {},
          i;
        for (i = 0; i < TRANSLATABLE_WORD_LIST.length; i += 1) {
          result_dict[TRANSLATABLE_WORD_LIST[i]] = word_list[i];
        }
        return result_dict;
      });
  }

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
      );
    }
    return domsugar('h1', element_list);
  }

  function buildSlideButtonList(slide_dialog, translation_dict,
                                disable_previous, disable_next) {
    var button_list = [];
    button_list.push(
      domsugar('button', {
        type: 'button',
        'class': 'dialog-delete ui-icon-trash-o ui-btn-icon-left',
        text: translation_dict.Delete
      }),
      domsugar('button', {
        type: 'button',
        disabled: (slide_dialog === DIALOG_SLIDE),
        'class': 'dialog-slide ui-icon-file-image-o ui-btn-icon-left',
        text: translation_dict.Text
      }),
      domsugar('button', {
        type: 'button',
        disabled: (slide_dialog === DIALOG_COMMENT),
        'class': 'dialog-commenting ui-icon-comment ui-btn-icon-left',
        text: translation_dict.Comments
      }),
      domsugar('button', {
        type: 'button',
        disabled: disable_previous,
        'class': 'previous-btn ui-icon-backward ui-btn-icon-left',
        text: translation_dict.Previous
      }),
      domsugar('button', {
        type: 'button',
        'class': 'list-btn ui-icon-th ui-btn-icon-left',
        text: translation_dict.List
      }),
      domsugar('button', {
        type: 'button',
        disabled: disable_next,
        'class': 'next-btn ui-icon-forward ui-btn-icon-left',
        text: translation_dict.Next
      })
    );
    return button_list;
  }

  ///////////////////////////////////////////////////
  // Page view handling
  ///////////////////////////////////////////////////
  function getCKEditorJSON(translation_dict, key, value, title_html, type) {
    var ck_editor_json = {
      erp5_document: {
        "_embedded": {
          "_view": {
            "your_slide_content": {
              "title": translation_dict["Slide Text"],
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
    // Show chapter_title and slide_type inputs only during slide editing
    if (title_html !== null && type !== null) {

      ck_editor_json.erp5_document._embedded._view.your_chapter_title = {
        "title": translation_dict["Chapter Title"],
        "type": "StringField",
        "editable": 1,
        "required": 1,
        "key": "title_html",
        "value": title_html
      };

      ck_editor_json.erp5_document._embedded._view.your_slide_type = {
        "title": translation_dict["Type of Slide"],
        "type": "ListField",
        "editable": 1,
        "key": "type",
        items: [["", ""],
                      [translation_dict.Chapter, "chapter"],
                      [translation_dict.Screenshot, "screenshot"],
                      [translation_dict.Illustration, "illustration"],
                      [translation_dict.Code, "code"],
                      [translation_dict.Master, "master"]
                      ],
        value: type
      };

      ck_editor_json.form_definition.group_list = [
        ["left", [
          ["your_chapter_title"],
          ["your_slide_type"]
        ]]
      ].concat(ck_editor_json.form_definition.group_list);
    }

    return ck_editor_json;
  }

  function renderSlideDialog(gadget, translation_dict, slide_dialog,
                             is_updated) {
    var formbox,
      render_dict,
      slide_list = getSlideElementList(gadget.state.value),
      slide_dict = getSlideDictFromSlideElement(
        getSlideFromList(slide_list, gadget.state.display_index)
      ),
      queue;

    if (slide_dialog === DIALOG_SLIDE) {
      render_dict = getCKEditorJSON(
        translation_dict,
        "slide_html",
        slide_dict.slide_html,
        slide_dict.title_html,
        slide_dict.type
      );
    } else if (slide_dialog === DIALOG_COMMENT) {
      render_dict = getCKEditorJSON(
        translation_dict,
        "comment_html",
        slide_dict.comment_html,
        null,
        null
      );
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
        // Clone listbox header structure to reuse the css
        var header_element = domsugar('div', {'class': 'document_table'}, [
          domsugar('div', {'class': 'ui-table-header'}, [
            buildPageTitle(gadget, translation_dict.Slide),
            domsugar('null',
                     buildSlideButtonList(
                slide_dialog,
                translation_dict,
                gadget.state.display_index === 0,
                gadget.state.display_index === slide_list.length - 1
              ))
          ])
        ]);

        if (is_updated) {
          gadget.element.firstChild.replaceWith(header_element);
        } else {
          domsugar(gadget.element, [
            header_element,
            formbox.element
          ]);
        }
      });
  }

  function renderSlideList(gadget, translation_dict) {
    // Get the full HTML
    var header_element,
      section_list = getSlideElementList(gadget.state.value),
      draggable_element_list = [],
      i;

    // Clone listbox header structure to reuse the css
    header_element = domsugar('div', {'class': 'document_table'}, [
      domsugar('div', {'class': 'ui-table-header'}, [
        domsugar('h1', {text: section_list.length + ' ' +
                              translation_dict.Slides})
      ])
    ]);

    for (i = 0; i < section_list.length; i += 1) {
      draggable_element_list.push(domsugar('section', {
        draggable: true,
        'data-slide-index': i
      }, [
        domsugar('button', {type: 'button', text: translation_dict.Edit,
                 'class': 'display-slide ui-icon-pencil ui-btn-icon-left',
                 'data-slide-index': i}),
        domsugar('h1', {
          html: getSlideDictFromSlideElement(section_list[i]).title_html
        })
      ]));
    }
    // Add the "Add slide" button
    // div.appendChild(domsugar('section', {text: 'Add Slide'}));
    draggable_element_list.push(domsugar('section', [
      domsugar('button', {
        type: 'button',
        text: translation_dict['New Slide'],
        'class': 'display-new ui-icon-plus-circle ui-btn-icon-left'
      }),
      domsugar('h1', {
        text: translation_dict['New Slide']
      })
    ]));

    domsugar(gadget.element, [
      header_element,
      domsugar('div', {'class': 'slide_list'}, draggable_element_list)
    ]);
  }

  ///////////////////////////////////////////////////
  // Gadget
  ///////////////////////////////////////////////////
  rJS(window)
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")

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
        slide_dialog = gadget.state.slide_dialog,
        queue = getTranslationDict(gadget);

      if (display_step === DISPLAY_LIST) {
        return queue
          .push(function (translation_dict) {
            return renderSlideList(gadget, translation_dict);
          });
      }

      if (display_step === DISPLAY_SLIDE) {
        return queue
          .push(function (translation_dict) {
            return renderSlideDialog(
              gadget,
              translation_dict,
              slide_dialog,
              !(modification_dict.hasOwnProperty('display_step') ||
                modification_dict.hasOwnProperty('slide_dialog'))
            );
          });
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

      if (evt.target.className.indexOf("dialog-delete") !== -1) {
        return queue
          .push(function () {
            var slide_list = getSlideElementList(gadget.state.value);
            slide_list.splice(gadget.state.display_index, 1);
            return RSVP.all([
              gadget.changeState({
                value: slideListAsHTML(slide_list),
                display_step: DISPLAY_LIST
              }),
              gadget.notifyChange()
            ]);
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
      var closest_section = evt.target.closest('section');
      if (closest_section === null) {
        return;
      }
      evt.target.classList.add('drag');

      // Store index of the dragged slide
      evt.dataTransfer.effectAllowed = 'move';
      evt.dataTransfer.setData('application/x-dragged-slide',
                               evt.target.getAttribute('data-slide-index'));
    }, false, false)

    .onEvent("dragend", function (evt) {
      var closest_section = evt.target.closest('section');
      if (closest_section === null) {
        return;
      }
      evt.target.classList.remove('drag');
    }, false, false)

    .onEvent("dragover", function (evt) {
      var closest_section = evt.target.closest('section');
      if (closest_section === null) {
        return;
      }
      if (evt.preventDefault) {
        evt.preventDefault(); // Necessary. Allows us to drop.
      }
      evt.dataTransfer.dropEffect = 'move';
    }, false, false)

    .onEvent("dragenter", function (evt) {
      var closest_section = evt.target.closest('section');
      if (closest_section === null) {
        return;
      }

      // Provide a visual feedback to the user
      // Showing where the slide can be dropped
      if (closest_section.getAttribute('data-slide-index')) {
        closest_section.classList.add('over');
      }
    }, false, false)

    .onEvent("dragleave", function (evt) {
      //exits if mouse is indirectly over a section
      var closest_section = evt.relatedTarget.closest('section');
      if (closest_section !== null) {
        return;
      }
      evt.target.classList.remove('over');
    }, false, false)


    .onEvent("drop", function (evt) {
      var gadget = this,
        tag_name = evt.target.closest('section').tagName,
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
      if (source_index && evt.target.closest('section').getAttribute('data-slide-index')) {
        source_index = parseInt(
          source_index,
          10
        );
        destination_index = parseInt(
          evt.target.closest('section').getAttribute('data-slide-index'),
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