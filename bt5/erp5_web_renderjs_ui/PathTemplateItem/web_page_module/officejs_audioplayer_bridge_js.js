/*global rJS, jIO, console, RSVP, encodeURI, window */
/*jslint nomen: true*/
(function(rJS, jIO, window) {
    "use strict";
    rJS(window).ready(function(gadget) {
        // Initialize the gadget local parameters
        gadget.state_parameter_dict = {};
        gadget.save = {};
    }).declareMethod("createJio", function(jio_options) {
        this.state_parameter_dict.jio_storage = jIO.createJIO(jio_options);
        this.save = {};
    }).declareMethod("allDocs", function(options) {
        var storage = this.state_parameter_dict.jio_storage, that = this;
        if (that.save.data !== undefined) {
            return that.save;
        }
        return storage.allDocs(options).then(function(result) {
            if (options.save) {
                that.save = result;
            }
            return result;
        });
    }).declareMethod("get", function(param) {
        var storage = this.state_parameter_dict.jio_storage, result = this.save, length, i;
        if (result.data !== undefined) {
            length = result.data.rows.length;
            for (i = 0; i < length; i += 1) {
                if (result.data.rows[i].id === encodeURI(param._id) || result.data.rows[i].id === param._id) {
                    return {
                        data: {
                            title: result.data.rows[i].doc.title,
                            type: result.data.rows[i].doc.type
                        }
                    };
                }
            }
        }
        return storage.get.apply(storage, arguments);
    }).declareMethod("getAttachment", function() {
        var storage = this.state_parameter_dict.jio_storage;
        return storage.getAttachment.apply(storage, arguments).then(function(response) {
            return response.data;
        });
    }).declareMethod("putAttachment", function() {
        var storage = this.state_parameter_dict.jio_storage;
        return storage.putAttachment.apply(storage, arguments);
    }).declareMethod("post", function() {
        var storage = this.state_parameter_dict.jio_storage;
        return storage.post.apply(storage, arguments);
    }).declareMethod("remove", function() {
        var storage = this.state_parameter_dict.jio_storage;
        return storage.remove.apply(storage, arguments);
    }).declareMethod("removeAttachment", function() {
        var storage = this.state_parameter_dict.jio_storage;
        return storage.removeAttachment.apply(storage, arguments);
    }).declareMethod("put", function() {
        var storage = this.state_parameter_dict.jio_storage;
        return storage.put.apply(storage, arguments);
    });
})(rJS, jIO, window);