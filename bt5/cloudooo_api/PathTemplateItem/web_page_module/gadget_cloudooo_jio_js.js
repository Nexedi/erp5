/*global window, rJS, jIO, FormData, XMLHttpRequestProgressEvent, UriTemplate,
  URI, location, RSVP */
/*jslint  nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, jIO, URI, RSVP) {
  "use strict";

  // jIO call wrapper for redirection to authentication page if needed
  function wrapJioCall(gadget, method_name, argument_list) {
    var storage = gadget.state_parameter_dict.jio_storage;
    return storage[method_name].apply(storage, argument_list)
      .push(undefined, function (error) {
        if (error.target !== undefined && error.target.status === 401) {
          if (gadget.state_parameter_dict.jio_storage_name === "ERP5") {
            return gadget.redirect({ page: "login" });
          }
          if (gadget.state_parameter_dict.jio_storage_name === "DAV") {
            var regexp = /^Nayookie login_url=(http[s]?:\/\/[\/\-\[\]{}()*+=:?&.,\\\^$|#\s\w%]+)$/,
              auth_page = error.target.getResponseHeader('WWW-Authenticate'),
              site;
            if (regexp.test(auth_page)) {
              site = UriTemplate.parse(
                regexp.exec(auth_page)[1]
              ).expand({back_url: window.location.href,
                        origin: window.location.protocol + '//' +
                                window.location.host});
              return gadget.redirect({ toExternal: true, url: site});
            }
          }
        }
        throw error;
      });
  }

  function isFormatInAvailableFormatList(gadget, id, format) {
    return gadget.get(id)
      .push(function (data) {
        var available_format_list = data.available_format_list,
          i,
          i_len;
        for (i = 0, i_len = available_format_list.length; i < i_len; i += 1) {
          if (available_format_list[i] === format) {
            return true;
          }
        }
        return false;
      });
  }

  function getjIOActionLink(gadget, id, action_id) {
    return wrapJioCall(gadget, 'getAttachment', [id, 'links', {format: "json"}])
      .push(function (result) {
        var i, i_len, links;
        links = result._links.action_object_jio_action;
        if (links.hasOwnProperty("length")) {
          for (i = 0, i_len = links.length; i < i_len; i += 1) {
            if (links[i].name === action_id) {
              return links[i];
            }
          }
        } else {
          if (links.name === action_id) {
            return links;
          }
        }
        return undefined;
      });
  }

  rJS(window)

    .ready(function (gadget) {
      // Initialize the gadget local parameters
      gadget.state_parameter_dict = {};
      gadget.props = {};
    })

    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")

    .declareMethod('createJio', function (jio_options) {
      var gadget = this;
      gadget.props.url = (new URI("hateoas"))
            .absoluteTo(location.href)
            .toString();
      if (jio_options === undefined) {
        jio_options = {
          type: "erp5",
          url: gadget.props.url,
          default_view_reference: "jio_view"
        };
      }
      this.state_parameter_dict.jio_storage = jIO.createJIO(jio_options);
      return this.getSetting("jio_storage_name")
        .push(function (jio_storage_name) {
          gadget.state_parameter_dict.jio_storage_name = jio_storage_name;
        });
    })
    .declareMethod('allDocs', function () {
      return wrapJioCall(this, 'allDocs', arguments);
    })
    .declareMethod('allAttachments', function () {
      return wrapJioCall(this, 'allAttachments', arguments);
    })
    .declareMethod('get', function () {
      return wrapJioCall(this, 'get', arguments);
    })
    .declareMethod('put', function () {
      return wrapJioCall(this, 'put', arguments);
    })
    .declareMethod('post', function () {
      return wrapJioCall(this, 'post', arguments);
    })
    .declareMethod('remove', function () {
      return wrapJioCall(this, 'remove', arguments);
    })
    .declareMethod('getAttachment', function (id, name, options) {
      /*
      So far the name of the attachment is either the format you need,
      either the path or reference of the part you need.
      XXX This might change as the part (eg: an image) might be an other document
      instead of an attachment. The we should get as a property of the document the list
      of related document needed by this document.
      XXX We also need a way to pass options to the converter, such as the quality,
      the size....
      */
      /*template(docmod/1{?format,quality,truc,truc}).tructruc(format='jpg')*/
      /*name = "jpg&quality=45"*/
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return isFormatInAvailableFormatList(gadget, id, name);
        })
        .push(function (is_format_available) {
          var action_id;
          if (is_format_available) {
            action_id = 'jio_get_converted_element';
          } else {
            action_id = 'jio_get_related_document_value';
          }
          /* 
          Get the url of the action from ERP5 it is provided in a 
          template format for uri-template 
          */
          return getjIOActionLink(gadget, id, action_id);
        })
        .push(function (action) {
          return wrapJioCall(gadget, 'getAttachment',
            [
              id,
              UriTemplate.parse(action.href)
                .expand(
                  {
                    hateoas: gadget.props.url,
                    format: name,
                    name: name
                    /* **kw */
                  }
                ),
              options
            ]);
        });
    })
    .declareMethod('putAttachment', function (id, name, file) {
      var gadget = this,
        result = {},
        action;
      /* Enclosure is the name of the main data */
      if (name === "enclosure") {
        return RSVP.Queue()
          .push(function () {
            return getjIOActionLink(gadget, id, "jio_file_upload");
          })
          .push(function (result) {
            action = result;
            return jIO.util.readBlobAsDataURL(file);
          })
          .push(function (evt) {
            result = {
              file: {
                file_name: file.name,
                url: evt.target.result
              }
            };
            return wrapJioCall(gadget, 'putAttachment', [
              id,
              UriTemplate.parse(action.href)
                .expand(
                  {
                    hateoas: gadget.props.url
                  }
                ),
              JSON.stringify(result)
            ]);
          });
      }
      /* 

      Here handle other documents

      Images of a OOodocument can be added as Embedded File of the
      document. eg: media/image1.png should be identified as the embedded file
      with the id: 'media_image1.png'. getAttachment as is can already handle this
      case, here some code needs to be add to create/update the embedded file
      if it doesn't exists

      */
    })
    .declareMethod('removeAttachment', function () {
      return wrapJioCall(this, 'removeAttachment', arguments);
    })
    .declareMethod('repair', function () {
      return wrapJioCall(this, 'repair', arguments);
    });

}(window, rJS, jIO, URI, RSVP));