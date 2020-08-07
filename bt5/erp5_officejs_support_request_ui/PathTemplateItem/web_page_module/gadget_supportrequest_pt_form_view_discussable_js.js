/*global window, rJS, RSVP, calculatePageTitle, FormData, URI, jIO, moment, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, calculatePageTitle, moment, Handlebars) {
  "use strict";
  var gadget_klass = rJS(window),
    comment_list_template_source = gadget_klass.__template_element.getElementById("template-document-list").innerHTML

  /**
   * french locale for momentjs, copied from https://momentjs.com/docs/
   */
  moment.locale('fr', {
      months : 'janvier_février_mars_avril_mai_juin_juillet_août_septembre_octobre_novembre_décembre'.split('_'),
      monthsShort : 'janv._févr._mars_avr._mai_juin_juil._août_sept._oct._nov._déc.'.split('_'),
      monthsParseExact : true,
      weekdays : 'dimanche_lundi_mardi_mercredi_jeudi_vendredi_samedi'.split('_'),
      weekdaysShort : 'dim._lun._mar._mer._jeu._ven._sam.'.split('_'),
      weekdaysMin : 'Di_Lu_Ma_Me_Je_Ve_Sa'.split('_'),
      weekdaysParseExact : true,
      longDateFormat : {
          LT : 'HH:mm',
          LTS : 'HH:mm:ss',
          L : 'DD/MM/YYYY',
          LL : 'D MMMM YYYY',
          LLL : 'D MMMM YYYY HH:mm',
          LLLL : 'dddd D MMMM YYYY HH:mm'
      },
      calendar : {
          sameDay : '[Aujourd’hui à] LT',
          nextDay : '[Demain à] LT',
          nextWeek : 'dddd [à] LT',
          lastDay : '[Hier à] LT',
          lastWeek : 'dddd [dernier à] LT',
          sameElse : 'L'
      },
      relativeTime : {
          future : 'dans %s',
          past : 'il y a %s',
          s : 'quelques secondes',
          m : 'une minute',
          mm : '%d minutes',
          h : 'une heure',
          hh : '%d heures',
          d : 'un jour',
          dd : '%d jours',
          M : 'un mois',
          MM : '%d mois',
          y : 'un an',
          yy : '%d ans'
      },
      dayOfMonthOrdinalParse : /\d{1,2}(er|e)/,
      ordinal : function (number) {
          return number + (number === 1 ? 'er' : 'e');
      },
      meridiemParse : /PD|MD/,
      isPM : function (input) {
          return input.charAt(0) === 'M';
      },
      // In case the meridiem units are not separated around 12, then implement
      // this function (look at locale/id.js for an example).
      // meridiemHour : function (hour, meridiem) {
      //     return /* 0-23 hour, given meridiem token and hour 1-12 */ ;
      // },
      meridiem : function (hours, minutes, isLower) {
          return hours < 12 ? 'PD' : 'MD';
      },
      week : {
          dow : 1, // Monday is the first day of the week.
          doy : 4  // Used to determine first week of the year.
      }
  });


  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")


    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('getDocumentUrl', function (raw_url) {
      var gadget = this;
      return gadget.jio_getAttachment(raw_url, "links")
        .push(function (links) {
          // try to find a preview action
          var page, i, view_actions = links._links.view;
          for (i = 0; i < view_actions.length; i += 1) {
            if (view_actions[i].name.indexOf('preview') !== -1 || view_actions[i].title === 'Preview') {
              page = view_actions[i].name;
              break;
            }
          }
          // if not found, fallback to the first view action
          if (page === undefined) {
            for (i = 0; i < view_actions.length; i += 1) {
              if (view_actions[i].name.indexOf('view') !== -1) {
                page = view_actions[i].name;
                break;
              }
            }
          }
          return gadget.getUrlFor({
            command: 'display_erp5_action_with_history',
            options: {
              jio_key: raw_url,
              page: page
            }
          });
        });
    })
    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
      return gadget.getElement()
        .push(function (element) {
          // Translate HTML page. We only translate and replace some the elements with
          // data-i18n-translate-element attribute, not to replace DOM elements with
          // event handler attached.
          function translateElement(e) {
            return gadget
              .translateHtml(e.innerHTML)
              .push(function (translatedHtml) {
                e.innerHTML = translatedHtml;
              });
          }
          return RSVP.all(
            Array.from(element.querySelectorAll('[data-i18n-translate-element]')).map(translateElement))
            .then(
              // Translate and compile the handlebar template for messages
              function () {
                return gadget
                  .translateHtml(comment_list_template_source)
                  .push(function (translatedTemplate) {
                    gadget.comment_list_template = Handlebars.compile(translatedTemplate);
                  });
              }
            );
        })
        .push(function () {
          return gadget.getSetting('hateoas_url')
        })
        .push(function (hateoas_url) {
          gadget.hateoas_url = hateoas_url;
        })
        .push(function () {
          var state_dict = {
            id: options.jio_key,
            view: options.view,
            editable: options.editable,
            erp5_document: options.erp5_document,
            form_definition: options.form_definition,
            erp5_form: options.erp5_form || {}
          };
          return gadget.changeState(state_dict);
        });
    })
    // editor gadget call this acquired method on Ctrl+S
    .declareMethod("triggerSubmit", function triggerSubmit(e) {
      return this.submitPostComment(e);
    })
    .onStateChange(function () {
      var gadget = this;
      // render the erp5 form
      return gadget.getDeclaredGadget("erp5_form")
        .push(function (erp5_form) {
          return gadget.getDeclaredGadget("editor")
            .push(function (editor) {
              return [editor, erp5_form];
            });
        })
        .push(function (gadgets) {
          var form_options = gadget.state.erp5_form,
            rendered_form = gadget.state.erp5_document._embedded._view,
            preferred_editor = rendered_form.your_preferred_editor.default,
            rendered_field,
            key,
            editor = gadgets[0],
            erp5_form = gadgets[1];
          // Remove all empty fields, and mark all others as non editable
          for (key in rendered_form) {
            if (rendered_form.hasOwnProperty(key) && (key[0] !== "_")) {
              rendered_field = rendered_form[key];
              if ((rendered_field.type !== "ListBox") && ((!rendered_field.default) || (rendered_field.hidden === 1) || (rendered_field.default.length === 0)
                   || (rendered_field.default.length === 1 && (!rendered_field.default[0])))) {
                delete rendered_form[key];
              } else {
                rendered_field.editable = 0;
              }
            }
          }

          form_options.erp5_document = gadget.state.erp5_document;
          form_options.form_definition = gadget.state.form_definition;
          form_options.view = gadget.state.view;
          return new RSVP.Queue()
            .push(
              function () {
                return RSVP.all([
                  erp5_form.render(form_options),
                  editor.render({
                    value: "",
                    key: "comment",
                    portal_type: "HTML Post",
                    editable: true,
                    editor: preferred_editor,
                    maximize: true
                  })]);
              }
            ).push(function () {
              // make our submit button editable
              var element = gadget.element.querySelector('input[type="submit"]');
              element.removeAttribute('disabled');
              element.classList.remove('ui-disabled');
            });
        })

        // render the header
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'change', options: {editable: true}}),
            gadget.getUrlFor({command: 'change', options: {page: "action"}}),
            gadget.getUrlFor({command: 'history_previous'}),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'}),
            gadget.getUrlFor({command: 'change', options: {page: "tab"}}),
            gadget.state.erp5_document._links.action_object_report_jio ?
                gadget.getUrlFor({command: 'change', options: {page: "export"}}) :
                "",
            calculatePageTitle(gadget, gadget.state.erp5_document)
          ]);
        })
        .push(function (all_result) {
          return gadget.updateHeader({
            edit_url: all_result[0],
            actions_url: all_result[1],
            selection_url: all_result[2],
            previous_url: all_result[3],
            next_url: all_result[4],
            tab_url: all_result[5],
            export_url: all_result[6],
            page_title: all_result[7]
          });
        })
        .push(function () {
          // set locale for momentjs
          return gadget.getSettingList(["selected_language",
            "default_selected_language"]
            ).push(function (lang_list) {
            moment.locale(lang_list[0] || lang_list[1]);
          });
        })
        .push(function () {
          return gadget.jio_getAttachment(
            'post_module',
            gadget.hateoas_url + gadget.options.jio_key + "/SupportRequest_getCommentPostListAsJson"
          );
        })
        .push(function (post_list) {
          function getPostWithLinkAndLocalDate(post) {
            post.date_formatted = moment(post.date).format('LLLL');
            post.date_relative = moment(post.date).fromNow();
            if (post.attachment_link === null) {
              return post;
            }
            return gadget.getDocumentUrl(post.attachment_link).push(
              function (attachment_link) {
                post.attachment_link = attachment_link;
                return post;
              }
            );
          }
          // build links with attachments and localized dates
          var queue_list = [], i = 0;
          for (i = 0; i < post_list.length; i += 1) {
            queue_list.push(getPostWithLinkAndLocalDate(post_list[i]));
          }
          return RSVP.all(queue_list);
        })
        .push(function (comment_list) {
          var comments = gadget.element.querySelector("#post_list");
          comments.innerHTML = gadget.comment_list_template({comments: comment_list});
        });
    })
    .declareJob('submitPostComment', function () {
      var gadget = this,
        submitButton = null,
        queue = null;

      return gadget.getDeclaredGadget("editor")
        .push(function (e) {
          return e.getContent();
        })
        .push(function (content) {
          if (content.comment === '') {
            return gadget.translate("Post content can not be empty!")
                .push(function (translated_message) {
                  return gadget.notifySubmitted({message: translated_message});
                })
          }

          submitButton = gadget.element.querySelector("input[type=submit]");
          submitButton.disabled = true;
          submitButton.classList.add("ui-disabled");

          function enableSubmitButton() {
            submitButton.disabled = false;
            submitButton.classList.remove("ui-disabled");
          }
          queue = gadget.translate("Posting comment").
            push(function (message_posting_comment) {
              return gadget.notifySubmitted({message: message_posting_comment})
            })
            .push(function () {
              var choose_file_html_element = gadget.element.querySelector('#attachment'),
                file_blob = choose_file_html_element.files[0],
                url = gadget.hateoas_url + "post_module/PostModule_createHTMLPostForSupportRequest",
                data = new FormData();
              data.append("follow_up", gadget.options.jio_key);
              data.append("predecessor", '');
              data.append("data", content.comment);
              data.append("file", file_blob);

              // reset the file upload, otherwise next comment would upload same file again
              choose_file_html_element.value = "";

              // XXX: Hack, call jIO.util.ajax directly to pass the file blob
              // Because the jio_putAttachment will call readBlobAsText, which
              // will broke the binary file. Call the jIO.util.ajax directly
              // will not touch the blob
              return jIO.util.ajax({
                "type": "POST",
                "url": url,
                "data": data,
                "xhrFields": {
                  withCredentials: true
                }
              });
            })
            .push(function () {
              return new RSVP.Queue().push(
                function(){
                  return gadget.translate("Comment added")
                }
              ).push(function (message_comment_added) {
                gadget.notifySubmitted({message: message_comment_added, status: "success"});
              }).push(function () {
                return gadget.redirect({command: 'reload'});
              });
            }, function (e) {
              enableSubmitButton();
              return gadget.notifySubmitted({message: "Error:" + e, status: "error"});
            });
          return queue;
        });
    })
    .onLoop(function () {
      // update relative time
      this.element.querySelectorAll("li>time").forEach(
        function (element) {
          element.textContent = moment(element.getAttribute('datetime')).fromNow();
        }
      );
    }, 5000)
    .onEvent('submit', function () {
      return this.submitPostComment();
    });
}(window, rJS, RSVP, calculatePageTitle, moment, Handlebars));
