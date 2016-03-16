/*global window, rJS, RSVP, document*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (window, document, rJS, RSVP) {
  "use strict";
  function promiseEventListener(target, type, useCapture) {
    //////////////////////////
    // Resolve the promise as soon as the event is triggered
    // eventListener is removed when promise is cancelled/resolved/rejected
    //////////////////////////
    var handle_event_callback;

    function canceller() {
      target.removeEventListener(type, handle_event_callback, useCapture);
    }

    function resolver(resolve) {
      handle_event_callback = function (evt) {
        canceller();
        evt.stopPropagation();
        evt.preventDefault();
        resolve(evt);
        return false;
      };

      target.addEventListener(type, handle_event_callback, useCapture);
    }
    return new RSVP.Promise(resolver, canceller);
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var g = this,
        i,
        list_gadget = document.getElementsByClassName("gadget"),
        all_gadget,
        list = [],
        gadget_attributes = [],
        url,
        form = g.props.element.querySelector("form"),
        scope,
        value,
        key,
        tmp;
      for (i = 0; i < list_gadget.length; i += 1) {
        url = list_gadget[i].getAttribute("data-gadget-url");
        key = list_gadget[i].getAttribute("data-gadget-editable");
        value = list_gadget[i].getAttribute("data-gadget-value");
        //renderable 
        if (url !== undefined && url !== null) {
          tmp = {};
          scope = list_gadget[i].getAttribute("data-gadget-scope");
          list.push(g.getDeclaredGadget(scope));
          tmp.sandbox = list_gadget[i].getAttribute("data-gadget-sandbox");
          tmp.editable = key;
          tmp.key = key;
          tmp.value = value;
          gadget_attributes.push(tmp);
        }
      }
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all(list);
        })
        .push(function (results) {
          all_gadget = results;
          list = [];
          for (i = 0; i < gadget_attributes.length; i += 1) {
            if (gadget_attributes[i].sandbox === "iframe") {
              list.push(all_gadget[i].getElement());
            }
          }
          return RSVP.all(list);
        })
        .push(function (elements) {
          var iframe,
            j,
            sub_value,
            sub_key;
          list = [];
          for (i = 0, j = 0; i < gadget_attributes.length; i += 1) {
            if (all_gadget[i].render !== undefined) {
              sub_value = gadget_attributes[i].value;
              sub_key = gadget_attributes[i].key;
              list.push(
                all_gadget[i].render(
                  {
                    "key": sub_key,
                    "value": sub_value
                  }
                )
              );
            }
            if (gadget_attributes[i].sandbox === "iframe") {
              iframe = elements[j].querySelector('iframe');
              //xxx input field
              elements[j].parentNode.style.width = "100%";
              elements[j].parentNode.style.height = "100%";
              //xxx section div
              elements[j].style.width = "100%";
              elements[j].style.height = "100%";
              iframe.style.width = "100%";
              iframe.style.height = "100%";
              j += 1;
            }
          }
          return RSVP.all(list);
        })
        .push(function () {
          /*Do not use ajax call but submit an hidden form.
            So in this way, we can use form submit mecanisme
            provided by browser.
            if use ajax, we should get the return page manually
            which is difficult.
            The new hidden fields have been added with the 
            gadget values and the submit button which 
            has been activated (relation field image, save button, etc).
            This is done by listening the "click" event on the 
            submit/image button.
            After all, submit the form manually again.
          */
          var input_images =
            g.props.element.querySelectorAll("input[type='image']"),
            input_submits =
            g.props.element.querySelectorAll("button[type='submit']");
          list = [];
          if (input_images.length || input_submits.length) {
            list.push(promiseEventListener(g.props.element, "submit", false));
            for (i = 0; i < input_images.length; i += 1) {
              list.push(promiseEventListener(input_images[i], "click", false));
            }
            for (i = 0; i < input_submits.length; i += 1) {
              list.push(promiseEventListener(input_submits[i], "click", false));
            }
            return RSVP.any(list);
          }
          return promiseEventListener(g.props.element, "submit", false);
        })
        .push(function (evt) {
          var input,
            hidden_button,
            target;
          list = [];
          if (evt.type === "click") {
            input = document.createElement("input");
            input.setAttribute("type", "hidden");
            target = evt.currentTarget || evt.target;
            input.setAttribute("name", target.getAttribute("name"));
            form.appendChild(input);
          } else {
            hidden_button = g.props.element.querySelector(".hidden_button");
            hidden_button.setAttribute("type", "hidden");
          }
          for (i = 0; i < all_gadget.length; i += 1) {
            if (all_gadget[i].getContent !== undefined &&
                gadget_attributes[i].editable !== null) {
              list.push(all_gadget[i].getContent());
            }
          }
          return RSVP.all(list);
        })
        .push(function (all_content) {
          var input,
            name;
          for (i = 0; i < all_content.length; i += 1) {
            for (name in all_content[i]) {
              if (all_content[i].hasOwnProperty(name)) {
                input = document.createElement("input");
                input.setAttribute("type", "hidden");
                input.setAttribute("name", name);
                input.setAttribute("value", all_content[i][name]);
                form.appendChild(input);
              }
            }
          }
        })
        .push(function () {
          form.submit();
        });
    });
}(window, document, rJS, RSVP));