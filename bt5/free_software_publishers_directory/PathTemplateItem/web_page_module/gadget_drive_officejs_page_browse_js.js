/*globals window, rJS, RSVP, jIO, loopEventListener, document */
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, rJS, RSVP, jIO, loopEventListener, document) {
  "use strict";

  var gadget_klass = rJS(window);

  gadget_klass
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    .declareAcquiredMethod("redirect", "redirect")

    .declareMethod("parse", function (text) {
      //XXX use jison here instead of parsing manually
      var command,
        args = text.split(' '),
        index;
      // command is the first token
      command = args.shift();

      /* begin from the end because removing some values from the list
         while looping */
      for (index = args.length ; index > 0 ; index --) {
        // remove emply strings from argument list
        if (args[index] === '') {
          args.splice(index, 1);
        }
      }
      return {command: command, args: args};
    })

    .declareMethod("browse", function (command, args) {
      var gadget = this,
        requireSingleArgError = new Error(
          'This command requires one argument.'
        );

      function absolutePosition(current, requested) {
        var pos;
        if (requested.startsWith('/')) {
          pos = '/' + requested;
        } else {
          pos = current + '/' + requested;
        }
        return pos.replace(/\/+/g, '/');
      }
      // if command given: proceed

      if (command) {
        try {
          switch (command) {
          case 'cd':
            if (args.length === 1) {
              return gadget.redirect({
                position: absolutePosition(gadget.props.currentPosition,
                                           args[0] + '/')
              });
            }
            throw requireSingleArgError;

          case 'vim':
          case 'vi':
            if (args.length === 1) {
              return gadget.redirect({
                page: 'edit',
                resource: absolutePosition(gadget.props.currentPosition,
                                           args[0]),
                back: gadget.props.currentPosition
              });
            }
            throw requireSingleArgError;
          case 'share':
            if (args.length === 1) {
              return gadget.jio_getAttachment(absolutePosition(
                gadget.props.currentPosition,
                args[0]
              ), 'enclosure')
                .push(function (resp) {
                  return jIO.util.readBlobAsDataURL(resp);
                })
                .push(function (e) {
                  gadget.props.element.querySelector('.output').textContent = e.target.result;
                });
            }
            throw requireSingleArgError;
          default:
            throw new Error('Unknown command: ' + command);
          }
        } catch (e) {
          gadget.props.element.querySelector('.error').textContent = e.name +
                                                                     ": " +
                                                                     e.message;
        }
      }
    })

    .declareMethod("render", function (options) {
      var gadget = this,
        ul = gadget.props.element.querySelector('ul');

      // redirect to root if no position given
      if (!options.position) {
        return gadget.redirect({
          position: '/'
        });
      }
      gadget.props.currentPosition = options.position;
      gadget.props.element.querySelector('input').value = '';

      // clean previous ul children
      while (ul.hasChildNodes()) {
        ul.removeChild(ul.firstChild);
      }
      return gadget.jio_allDocs({id: options.position})
        .push(function (all) {
          var key,
            li,
            id,
            liContent,
            resourceName;
          for (key in all.data.rows) {
            if (all.data.rows.hasOwnProperty(key)) {
              id = all.data.rows[key].value.id;
              li = document.createElement('li');
              resourceName = document.createTextNode(id);

              if (id.endsWith('.txt') || id.endsWith('.js') ||
                  id.endsWith('.html') || id.endsWith('.py') ||
                  id.endsWith('_js')) {
                liContent = document.createElement('a');

                liContent.setAttribute('href', '#page=edit&resource=' +
                                       [options.position, id].join('/') +
                                       '&back=' + options.position);
                liContent.appendChild(resourceName);
              } else {
                liContent = resourceName;
              }
              li.appendChild(liContent);
              ul.appendChild(li);
            }
          }
        });
    })

    .declareService(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return loopEventListener(
            gadget.props.element.querySelector('form'),
            'submit',
            true,
            function () {
              var input = gadget.props.element.querySelector('input');
              return gadget.parse(input.value)
                .push(function (fullCommand) {
                  var args = fullCommand.args,
                    command = fullCommand.command;
                  gadget.browse(command, args);
                });
            }
          );
        });
    });

}(window, rJS, RSVP, jIO, loopEventListener, document));