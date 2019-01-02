/*global window, rJS, RSVP, jIO, JSON, promiseEventListener, console,
 Math, ID3, FileAPIReader, dataReader, String, decodeURIComponent,
 DataView, escape */
/*jslint nomen: true*/
/*jslint bitwise: true*/
(function(window, jIO, rJS) {
    "use strict";
    var gk = rJS(window);
    function promiseId3(file) {
        var resolver;
        resolver = function(resolve) {
            ID3.loadTags(file.name, function() {
                var tags = ID3.getAllTags(file.name);
                resolve(tags);
            }, {
                tags: [ "artist", "title", "album", "year", "comment", "track", "genre", "lyrics", "picture" ],
                dataReader: new FileAPIReader(file)
            });
        };
        return new RSVP.Promise(resolver);
    }
    function unknown(str) {
        var ch = str.charAt(0), patrn = /[\u4E00-\u9FA5]|[\uFE30-\uFFA0]/gi;
        if (!patrn.exec(str)) {
            if (ch < "a" || ch > "z" || ch < "A" || ch > "Z") {
                return true;
            }
            if (ch < "0" || ch > "9") {
                return true;
            }
        }
        return false;
    }
    function exit(g) {
        return RSVP.Queue().push(function() {
            return g.plEnablePage();
        }).push(function() {
            return g.displayThisPage({
                page: "playlist"
            });
        }).push(function(url) {
            window.location = url;
        });
    }
    gk.declareAcquiredMethod("jio_post", "jio_post").declareAcquiredMethod("jio_putAttachment", "jio_putAttachment").declareAcquiredMethod("jio_remove", "jio_remove").declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash").declareAcquiredMethod("displayThisPage", "displayThisPage").declareAcquiredMethod("displayThisTitle", "displayThisTitle").declareAcquiredMethod("plEnablePage", "plEnablePage").declareAcquiredMethod("plDisablePage", "plDisablePage").declareAcquiredMethod("plGiveStorageType", "plGiveStorageType").declareMethod("render", function() {
        return this.displayThisTitle("upload");
    }).declareMethod("startService", function() {
        var g = this, input_context = g.__element.getElementsByTagName("input")[0], info_context = g.__element.getElementsByClassName("info")[0], queue, uploaded = 0, post, type = 0, length;
        info_context.innerHTML = "<ul>";
        post = function() {
            var now = new Date(), id, file;
            if (uploaded === length) {
                return;
            }
            file = input_context.files[uploaded];
            return promiseId3(file).then(function(tags) {
                var title = tags.title, artist = tags.artist, album = tags.album, year = tags.year, i, image, picture = "./unknown.jpg", base64String;
                if (tags.picture) {
                    image = tags.picture;
                    base64String = "";
                    for (i = 0; i < image.data.length; i += 1) {
                        base64String += String.fromCharCode(image.data[i]);
                    }
                    picture = "data:" + image.format + ";base64," + window.btoa(base64String);
                }
                if (title === undefined || unknown(title)) {
                    title = file.name;
                    artist = "unknown";
                    album = "unknown";
                    year = "unknown";
                }
                return g.jio_post({
                    title: title,
                    type: file.type,
                    format: file.type,
                    size: file.size,
                    artist: artist,
                    album: album,
                    year: year,
                    picture: picture,
                    modified: now.toUTCString(),
                    date: now.getFullYear() + "-" + (now.getMonth() + 1) + "-" + now.getDate()
                }, type);
            }).then(function(res) {
                id = res.id;
                return g.jio_putAttachment({
                    _id: res.id,
                    _attachment: "enclosure",
                    _blob: input_context.files[uploaded]
                }, type);
            }).then(function() {
                uploaded += 1;
                info_context.innerHTML += "<li>" + input_context.files[uploaded - 1].name + "  " + uploaded + "/" + length + "</li>";
                if (uploaded === length) {
                    return exit(g);
                }
                queue.push(post);
            }).fail(function(error) {
                if (!(error instanceof RSVP.CancellationError)) {
                    info_context.innerHTML += input_context.files[uploaded].name + " " + error.target.error.name;
                    //xxx
                    g.plEnablePage();
                    return g.jio_remove({
                        _id: id
                    });
                }
                document.getElementsByTagName("body")[0].textContent = JSON.stringify(error);
            });
        };
        queue = new RSVP.Queue();
        queue.push(function() {
            return g.plEnablePage();
        }).push(function() {
            return g.plGiveStorageType();
        }).push(function(param) {
            type = param;
            return promiseEventListener(input_context, "change", false);
        }).push(function() {
            return g.plDisablePage();
        }).push(function() {
            length = input_context.files.length;
            queue.push(post);
        });
        return queue;
    });
})(window, jIO, rJS);