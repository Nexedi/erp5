<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts63959149.87</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>formplugin.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*!\n
 * jQuery Form Plugin\n
 * version: 3.29.0-2013.03.22\n
 * @requires jQuery v1.5 or later\n
 *\n
 * Examples and documentation at: http://malsup.com/jquery/form/\n
 * Project repository: https://github.com/malsup/form\n
 * Dual licensed under the MIT and GPL licenses:\n
 *    http://malsup.github.com/mit-license.txt\n
 *    http://malsup.github.com/gpl-license-v2.txt\n
 */\n
/*global ActiveXObject alert */\n
;(function($) {\n
"use strict";\n
\n
/*\n
    Usage Note:\n
    -----------\n
    Do not use both ajaxSubmit and ajaxForm on the same form.  These\n
    functions are mutually exclusive.  Use ajaxSubmit if you want\n
    to bind your own submit handler to the form.  For example,\n
\n
    $(document).ready(function() {\n
        $(\'#myForm\').on(\'submit\', function(e) {\n
            e.preventDefault(); // <-- important\n
            $(this).ajaxSubmit({\n
                target: \'#output\'\n
            });\n
        });\n
    });\n
\n
    Use ajaxForm when you want the plugin to manage all the event binding\n
    for you.  For example,\n
\n
    $(document).ready(function() {\n
        $(\'#myForm\').ajaxForm({\n
            target: \'#output\'\n
        });\n
    });\n
\n
    You can also use ajaxForm with delegation (requires jQuery v1.7+), so the\n
    form does not have to exist when you invoke ajaxForm:\n
\n
    $(\'#myForm\').ajaxForm({\n
        delegation: true,\n
        target: \'#output\'\n
    });\n
\n
    When using ajaxForm, the ajaxSubmit function will be invoked for you\n
    at the appropriate time.\n
*/\n
\n
/**\n
 * Feature detection\n
 */\n
var feature = {};\n
feature.fileapi = $("<input type=\'file\'/>").get(0).files !== undefined;\n
feature.formdata = window.FormData !== undefined;\n
\n
/**\n
 * ajaxSubmit() provides a mechanism for immediately submitting\n
 * an HTML form using AJAX.\n
 */\n
$.fn.ajaxSubmit = function(options) {\n
    /*jshint scripturl:true */\n
\n
    // fast fail if nothing selected (http://dev.jquery.com/ticket/2752)\n
    if (!this.length) {\n
        log(\'ajaxSubmit: skipping submit process - no element selected\');\n
        return this;\n
    }\n
\n
    var method, action, url, $form = this;\n
\n
    if (typeof options == \'function\') {\n
        options = { success: options };\n
    }\n
\n
    method = this.attr(\'method\');\n
    action = this.attr(\'action\');\n
    url = (typeof action === \'string\') ? $.trim(action) : \'\';\n
    url = url || window.location.href || \'\';\n
    if (url) {\n
        // clean url (don\'t include hash vaue)\n
        url = (url.match(/^([^#]+)/)||[])[1];\n
    }\n
\n
    options = $.extend(true, {\n
        url:  url,\n
        success: $.ajaxSettings.success,\n
        type: method || \'GET\',\n
        iframeSrc: /^https/i.test(window.location.href || \'\') ? \'javascript:false\' : \'about:blank\'\n
    }, options);\n
\n
    // hook for manipulating the form data before it is extracted;\n
    // convenient for use with rich editors like tinyMCE or FCKEditor\n
    var veto = {};\n
    this.trigger(\'form-pre-serialize\', [this, options, veto]);\n
    if (veto.veto) {\n
        log(\'ajaxSubmit: submit vetoed via form-pre-serialize trigger\');\n
        return this;\n
    }\n
\n
    // provide opportunity to alter form data before it is serialized\n
    if (options.beforeSerialize && options.beforeSerialize(this, options) === false) {\n
        log(\'ajaxSubmit: submit aborted via beforeSerialize callback\');\n
        return this;\n
    }\n
\n
    var traditional = options.traditional;\n
    if ( traditional === undefined ) {\n
        traditional = $.ajaxSettings.traditional;\n
    }\n
\n
    var elements = [];\n
    var qx, a = this.formToArray(options.semantic, elements);\n
    if (options.data) {\n
        options.extraData = options.data;\n
        qx = $.param(options.data, traditional);\n
    }\n
\n
    // give pre-submit callback an opportunity to abort the submit\n
    if (options.beforeSubmit && options.beforeSubmit(a, this, options) === false) {\n
        log(\'ajaxSubmit: submit aborted via beforeSubmit callback\');\n
        return this;\n
    }\n
\n
    // fire vetoable \'validate\' event\n
    this.trigger(\'form-submit-validate\', [a, this, options, veto]);\n
    if (veto.veto) {\n
        log(\'ajaxSubmit: submit vetoed via form-submit-validate trigger\');\n
        return this;\n
    }\n
\n
    var q = $.param(a, traditional);\n
    if (qx) {\n
        q = ( q ? (q + \'&\' + qx) : qx );\n
    }\n
    if (options.type.toUpperCase() == \'GET\') {\n
        options.url += (options.url.indexOf(\'?\') >= 0 ? \'&\' : \'?\') + q;\n
        options.data = null;  // data is null for \'get\'\n
    }\n
    else {\n
        options.data = q; // data is the query string for \'post\'\n
    }\n
\n
    var callbacks = [];\n
    if (options.resetForm) {\n
        callbacks.push(function() { $form.resetForm(); });\n
    }\n
    if (options.clearForm) {\n
        callbacks.push(function() { $form.clearForm(options.includeHidden); });\n
    }\n
\n
    // perform a load on the target only if dataType is not provided\n
    if (!options.dataType && options.target) {\n
        var oldSuccess = options.success || function(){};\n
        callbacks.push(function(data) {\n
            var fn = options.replaceTarget ? \'replaceWith\' : \'html\';\n
            $(options.target)[fn](data).each(oldSuccess, arguments);\n
        });\n
    }\n
    else if (options.success) {\n
        callbacks.push(options.success);\n
    }\n
\n
    options.success = function(data, status, xhr) { // jQuery 1.4+ passes xhr as 3rd arg\n
        var context = options.context || this ;    // jQuery 1.4+ supports scope context\n
        for (var i=0, max=callbacks.length; i < max; i++) {\n
            callbacks[i].apply(context, [data, status, xhr || $form, $form]);\n
        }\n
    };\n
\n
    // are there files to upload?\n
\n
    // [value] (issue #113), also see comment:\n
    // https://github.com/malsup/form/commit/588306aedba1de01388032d5f42a60159eea9228#commitcomment-2180219\n
    var fileInputs = $(\'input[type=file]:enabled[value!=""]\', this);\n
\n
    var hasFileInputs = fileInputs.length > 0;\n
    var mp = \'multipart/form-data\';\n
    var multipart = ($form.attr(\'enctype\') == mp || $form.attr(\'encoding\') == mp);\n
\n
    var fileAPI = feature.fileapi && feature.formdata;\n
    log("fileAPI :" + fileAPI);\n
    var shouldUseFrame = (hasFileInputs || multipart) && !fileAPI;\n
\n
    var jqxhr;\n
\n
    // options.iframe allows user to force iframe mode\n
    // 06-NOV-09: now defaulting to iframe mode if file input is detected\n
    if (options.iframe !== false && (options.iframe || shouldUseFrame)) {\n
        // hack to fix Safari hang (thanks to Tim Molendijk for this)\n
        // see:  http://groups.google.com/group/jquery-dev/browse_thread/thread/36395b7ab510dd5d\n
        if (options.closeKeepAlive) {\n
            $.get(options.closeKeepAlive, function() {\n
                jqxhr = fileUploadIframe(a);\n
            });\n
        }\n
        else {\n
            jqxhr = fileUploadIframe(a);\n
        }\n
    }\n
    else if ((hasFileInputs || multipart) && fileAPI) {\n
        jqxhr = fileUploadXhr(a);\n
    }\n
    else {\n
        jqxhr = $.ajax(options);\n
    }\n
\n
    $form.removeData(\'jqxhr\').data(\'jqxhr\', jqxhr);\n
\n
    // clear element array\n
    for (var k=0; k < elements.length; k++)\n
        elements[k] = null;\n
\n
    // fire \'notify\' event\n
    this.trigger(\'form-submit-notify\', [this, options]);\n
    return this;\n
\n
    // utility fn for deep serialization\n
    function deepSerialize(extraData){\n
        var serialized = $.param(extraData).split(\'&\');\n
        var len = serialized.length;\n
        var result = [];\n
        var i, part;\n
        for (i=0; i < len; i++) {\n
            // #252; undo param space replacement\n
            serialized[i] = serialized[i].replace(/\\+/g,\' \');\n
            part = serialized[i].split(\'=\');\n
            // #278; use array instead of object storage, favoring array serializations\n
            result.push([decodeURIComponent(part[0]), decodeURIComponent(part[1])]);\n
        }\n
        return result;\n
    }\n
\n
     // XMLHttpRequest Level 2 file uploads (big hat tip to francois2metz)\n
    function fileUploadXhr(a) {\n
        var formdata = new FormData();\n
\n
        for (var i=0; i < a.length; i++) {\n
            formdata.append(a[i].name, a[i].value);\n
        }\n
\n
        if (options.extraData) {\n
            var serializedData = deepSerialize(options.extraData);\n
            for (i=0; i < serializedData.length; i++)\n
                if (serializedData[i])\n
                    formdata.append(serializedData[i][0], serializedData[i][1]);\n
        }\n
\n
        options.data = null;\n
\n
        var s = $.extend(true, {}, $.ajaxSettings, options, {\n
            contentType: false,\n
            processData: false,\n
            cache: false,\n
            type: method || \'POST\'\n
        });\n
\n
        if (options.uploadProgress) {\n
            // workaround because jqXHR does not expose upload property\n
            s.xhr = function() {\n
                var xhr = jQuery.ajaxSettings.xhr();\n
                if (xhr.upload) {\n
                    xhr.upload.addEventListener(\'progress\', function(event) {\n
                        var percent = 0;\n
                        var position = event.loaded || event.position; /*event.position is deprecated*/\n
                        var total = event.total;\n
                        if (event.lengthComputable) {\n
                            percent = Math.ceil(position / total * 100);\n
                        }\n
                        options.uploadProgress(event, position, total, percent);\n
                    }, false);\n
                }\n
                return xhr;\n
            };\n
        }\n
\n
        s.data = null;\n
            var beforeSend = s.beforeSend;\n
            s.beforeSend = function(xhr, o) {\n
                o.data = formdata;\n
                if(beforeSend)\n
                    beforeSend.call(this, xhr, o);\n
        };\n
        return $.ajax(s);\n
    }\n
\n
    // private function for handling file uploads (hat tip to YAHOO!)\n
    function fileUploadIframe(a) {\n
        var form = $form[0], el, i, s, g, id, $io, io, xhr, sub, n, timedOut, timeoutHandle;\n
        var useProp = !!$.fn.prop;\n
        var deferred = $.Deferred();\n
\n
        if (a) {\n
            // ensure that every serialized input is still enabled\n
            for (i=0; i < elements.length; i++) {\n
                el = $(elements[i]);\n
                if ( useProp )\n
                    el.prop(\'disabled\', false);\n
                else\n
                    el.removeAttr(\'disabled\');\n
            }\n
        }\n
\n
        s = $.extend(true, {}, $.ajaxSettings, options);\n
        s.context = s.context || s;\n
        id = \'jqFormIO\' + (new Date().getTime());\n
        if (s.iframeTarget) {\n
            $io = $(s.iframeTarget);\n
            n = $io.attr(\'name\');\n
            if (!n)\n
                 $io.attr(\'name\', id);\n
            else\n
                id = n;\n
        }\n
        else {\n
            $io = $(\'<iframe name="\' + id + \'" src="\'+ s.iframeSrc +\'" />\');\n
            $io.css({ position: \'absolute\', top: \'-1000px\', left: \'-1000px\' });\n
        }\n
        io = $io[0];\n
\n
\n
        xhr = { // mock object\n
            aborted: 0,\n
            responseText: null,\n
            responseXML: null,\n
            status: 0,\n
            statusText: \'n/a\',\n
            getAllResponseHeaders: function() {},\n
            getResponseHeader: function() {},\n
            setRequestHeader: function() {},\n
            abort: function(status) {\n
                var e = (status === \'timeout\' ? \'timeout\' : \'aborted\');\n
                log(\'aborting upload... \' + e);\n
                this.aborted = 1;\n
\n
                try { // #214, #257\n
                    if (io.contentWindow.document.execCommand) {\n
                        io.contentWindow.document.execCommand(\'Stop\');\n
                    }\n
                }\n
                catch(ignore) {}\n
\n
                $io.attr(\'src\', s.iframeSrc); // abort op in progress\n
                xhr.error = e;\n
                if (s.error)\n
                    s.error.call(s.context, xhr, e, status);\n
                if (g)\n
                    $.event.trigger("ajaxError", [xhr, s, e]);\n
                if (s.complete)\n
                    s.complete.call(s.context, xhr, e);\n
            }\n
        };\n
\n
        g = s.global;\n
        // trigger ajax global events so that activity/block indicators work like normal\n
        if (g && 0 === $.active++) {\n
            $.event.trigger("ajaxStart");\n
        }\n
        if (g) {\n
            $.event.trigger("ajaxSend", [xhr, s]);\n
        }\n
\n
        if (s.beforeSend && s.beforeSend.call(s.context, xhr, s) === false) {\n
            if (s.global) {\n
                $.active--;\n
            }\n
            deferred.reject();\n
            return deferred;\n
        }\n
        if (xhr.aborted) {\n
            deferred.reject();\n
            return deferred;\n
        }\n
\n
        // add submitting element to data if we know it\n
        sub = form.clk;\n
        if (sub) {\n
            n = sub.name;\n
            if (n && !sub.disabled) {\n
                s.extraData = s.extraData || {};\n
                s.extraData[n] = sub.value;\n
                if (sub.type == "image") {\n
                    s.extraData[n+\'.x\'] = form.clk_x;\n
                    s.extraData[n+\'.y\'] = form.clk_y;\n
                }\n
            }\n
        }\n
\n
        var CLIENT_TIMEOUT_ABORT = 1;\n
        var SERVER_ABORT = 2;\n
\n
        function getDoc(frame) {\n
            var doc = frame.contentWindow ? frame.contentWindow.document : frame.contentDocument ? frame.contentDocument : frame.document;\n
            return doc;\n
        }\n
\n
        // Rails CSRF hack (thanks to Yvan Barthelemy)\n
        var csrf_token = $(\'meta[name=csrf-token]\').attr(\'content\');\n
        var csrf_param = $(\'meta[name=csrf-param]\').attr(\'content\');\n
        if (csrf_param && csrf_token) {\n
            s.extraData = s.extraData || {};\n
            s.extraData[csrf_param] = csrf_token;\n
        }\n
\n
        // take a breath so that pending repaints get some cpu time before the upload starts\n
        function doSubmit() {\n
            // make sure form attrs are set\n
            var t = $form.attr(\'target\'), a = $form.attr(\'action\');\n
\n
            // update form attrs in IE friendly way\n
            form.setAttribute(\'target\',id);\n
            if (!method) {\n
                form.setAttribute(\'method\', \'POST\');\n
            }\n
            if (a != s.url) {\n
                form.setAttribute(\'action\', s.url);\n
            }\n
\n
            // ie borks in some cases when setting encoding\n
            if (! s.skipEncodingOverride && (!method || /post/i.test(method))) {\n
                $form.attr({\n
                    encoding: \'multipart/form-data\',\n
                    enctype:  \'multipart/form-data\'\n
                });\n
            }\n
\n
            // support timout\n
            if (s.timeout) {\n
                timeoutHandle = setTimeout(function() { timedOut = true; cb(CLIENT_TIMEOUT_ABORT); }, s.timeout);\n
            }\n
\n
            // look for server aborts\n
            function checkState() {\n
                try {\n
                    var state = getDoc(io).readyState;\n
                    log(\'state = \' + state);\n
                    if (state && state.toLowerCase() == \'uninitialized\')\n
                        setTimeout(checkState,50);\n
                }\n
                catch(e) {\n
                    log(\'Server abort: \' , e, \' (\', e.name, \')\');\n
                    cb(SERVER_ABORT);\n
                    if (timeoutHandle)\n
                        clearTimeout(timeoutHandle);\n
                    timeoutHandle = undefined;\n
                }\n
            }\n
\n
            // add "extra" data to form if provided in options\n
            var extraInputs = [];\n
            try {\n
                if (s.extraData) {\n
                    for (var n in s.extraData) {\n
                        if (s.extraData.hasOwnProperty(n)) {\n
                           // if using the $.param format that allows for multiple values with the same name\n
                           if($.isPlainObject(s.extraData[n]) && s.extraData[n].hasOwnProperty(\'name\') && s.extraData[n].hasOwnProperty(\'value\')) {\n
                               extraInputs.push(\n
                               $(\'<input type="hidden" name="\'+s.extraData[n].name+\'">\').val(s.extraData[n].value)\n
                                   .appendTo(form)[0]);\n
                           } else {\n
                               extraInputs.push(\n
                               $(\'<input type="hidden" name="\'+n+\'">\').val(s.extraData[n])\n
                                   .appendTo(form)[0]);\n
                           }\n
                        }\n
                    }\n
                }\n
\n
                if (!s.iframeTarget) {\n
                    // add iframe to doc and submit the form\n
                    $io.appendTo(\'body\');\n
                    if (io.attachEvent)\n
                        io.attachEvent(\'onload\', cb);\n
                    else\n
                        io.addEventListener(\'load\', cb, false);\n
                }\n
                setTimeout(checkState,15);\n
\n
                try {\n
                    form.submit();\n
                } catch(err) {\n
                    // just in case form has element with name/id of \'submit\'\n
                    var submitFn = document.createElement(\'form\').submit;\n
                    submitFn.apply(form);\n
                }\n
            }\n
            finally {\n
                // reset attrs and remove "extra" input elements\n
                form.setAttribute(\'action\',a);\n
                if(t) {\n
                    form.setAttribute(\'target\', t);\n
                } else {\n
                    $form.removeAttr(\'target\');\n
                }\n
                $(extraInputs).remove();\n
            }\n
        }\n
\n
        if (s.forceSync) {\n
            doSubmit();\n
        }\n
        else {\n
            setTimeout(doSubmit, 10); // this lets dom updates render\n
        }\n
\n
        var data, doc, domCheckCount = 50, callbackProcessed;\n
\n
        function cb(e) {\n
            if (xhr.aborted || callbackProcessed) {\n
                return;\n
            }\n
            try {\n
                doc = getDoc(io);\n
            }\n
            catch(ex) {\n
                log(\'cannot access response document: \', ex);\n
                e = SERVER_ABORT;\n
            }\n
            if (e === CLIENT_TIMEOUT_ABORT && xhr) {\n
                xhr.abort(\'timeout\');\n
                deferred.reject(xhr, \'timeout\');\n
                return;\n
            }\n
            else if (e == SERVER_ABORT && xhr) {\n
                xhr.abort(\'server abort\');\n
                deferred.reject(xhr, \'error\', \'server abort\');\n
                return;\n
            }\n
\n
            if (!doc || doc.location.href == s.iframeSrc) {\n
                // response not received yet\n
                if (!timedOut)\n
                    return;\n
            }\n
            if (io.detachEvent)\n
                io.detachEvent(\'onload\', cb);\n
            else\n
                io.removeEventListener(\'load\', cb, false);\n
\n
            var status = \'success\', errMsg;\n
            try {\n
                if (timedOut) {\n
                    throw \'timeout\';\n
                }\n
\n
                var isXml = s.dataType == \'xml\' || doc.XMLDocument || $.isXMLDoc(doc);\n
                log(\'isXml=\'+isXml);\n
                if (!isXml && window.opera && (doc.body === null || !doc.body.innerHTML)) {\n
                    if (--domCheckCount) {\n
                        // in some browsers (Opera) the iframe DOM is not always traversable when\n
                        // the onload callback fires, so we loop a bit to accommodate\n
                        log(\'requeing onLoad callback, DOM not available\');\n
                        setTimeout(cb, 250);\n
                        return;\n
                    }\n
                    // let this fall through because server response could be an empty document\n
                    //log(\'Could not access iframe DOM after mutiple tries.\');\n
                    //throw \'DOMException: not available\';\n
                }\n
\n
                //log(\'response detected\');\n
                var docRoot = doc.body ? doc.body : doc.documentElement;\n
                xhr.responseText = docRoot ? docRoot.innerHTML : null;\n
                xhr.responseXML = doc.XMLDocument ? doc.XMLDocument : doc;\n
                if (isXml)\n
                    s.dataType = \'xml\';\n
                xhr.getResponseHeader = function(header){\n
                    var headers = {\'content-type\': s.dataType};\n
                    return headers[header];\n
                };\n
                // support for XHR \'status\' & \'statusText\' emulation :\n
                if (docRoot) {\n
                    xhr.status = Number( docRoot.getAttribute(\'status\') ) || xhr.status;\n
                    xhr.statusText = docRoot.getAttribute(\'statusText\') || xhr.statusText;\n
                }\n
\n
                var dt = (s.dataType || \'\').toLowerCase();\n
                var scr = /(json|script|text)/.test(dt);\n
                if (scr || s.textarea) {\n
                    // see if user embedded response in textarea\n
                    var ta = doc.getElementsByTagName(\'textarea\')[0];\n
                    if (ta) {\n
                        xhr.responseText = ta.value;\n
                        // support for XHR \'status\' & \'statusText\' emulation :\n
                        xhr.status = Number( ta.getAttribute(\'status\') ) || xhr.status;\n
                        xhr.statusText = ta.getAttribute(\'statusText\') || xhr.statusText;\n
                    }\n
                    else if (scr) {\n
                        // account for browsers injecting pre around json response\n
                        var pre = doc.getElementsByTagName(\'pre\')[0];\n
                        var b = doc.getElementsByTagName(\'body\')[0];\n
                        if (pre) {\n
                            xhr.responseText = pre.textContent ? pre.textContent : pre.innerText;\n
                        }\n
                        else if (b) {\n
                            xhr.responseText = b.textContent ? b.textContent : b.innerText;\n
                        }\n
                    }\n
                }\n
                else if (dt == \'xml\' && !xhr.responseXML && xhr.responseText) {\n
                    xhr.responseXML = toXml(xhr.responseText);\n
                }\n
\n
                try {\n
                    data = httpData(xhr, dt, s);\n
                }\n
                catch (err) {\n
                    status = \'parsererror\';\n
                    xhr.error = errMsg = (err || status);\n
                }\n
            }\n
            catch (err) {\n
                log(\'error caught: \',err);\n
                status = \'error\';\n
                xhr.error = errMsg = (err || status);\n
            }\n
\n
            if (xhr.aborted) {\n
                log(\'upload aborted\');\n
                status = null;\n
            }\n
\n
            if (xhr.status) { // we\'ve set xhr.status\n
                status = (xhr.status >= 200 && xhr.status < 300 || xhr.status === 304) ? \'success\' : \'error\';\n
            }\n
\n
            // ordering of these callbacks/triggers is odd, but that\'s how $.ajax does it\n
            if (status === \'success\') {\n
                if (s.success)\n
                    s.success.call(s.context, data, \'success\', xhr);\n
                deferred.resolve(xhr.responseText, \'success\', xhr);\n
                if (g)\n
                    $.event.trigger("ajaxSuccess", [xhr, s]);\n
            }\n
            else if (status) {\n
                if (errMsg === undefined)\n
                    errMsg = xhr.statusText;\n
                if (s.error)\n
                    s.error.call(s.context, xhr, status, errMsg);\n
                deferred.reject(xhr, \'error\', errMsg);\n
                if (g)\n
                    $.event.trigger("ajaxError", [xhr, s, errMsg]);\n
            }\n
\n
            if (g)\n
                $.event.trigger("ajaxComplete", [xhr, s]);\n
\n
            if (g && ! --$.active) {\n
                $.event.trigger("ajaxStop");\n
            }\n
\n
            if (s.complete)\n
                s.complete.call(s.context, xhr, status);\n
\n
            callbackProcessed = true;\n
            if (s.timeout)\n
                clearTimeout(timeoutHandle);\n
\n
            // clean up\n
            setTimeout(function() {\n
                if (!s.iframeTarget)\n
                    $io.remove();\n
                xhr.responseXML = null;\n
            }, 100);\n
        }\n
\n
        var toXml = $.parseXML || function(s, doc) { // use parseXML if available (jQuery 1.5+)\n
            if (window.ActiveXObject) {\n
                doc = new ActiveXObject(\'Microsoft.XMLDOM\');\n
                doc.async = \'false\';\n
                doc.loadXML(s);\n
            }\n
            else {\n
                doc = (new DOMParser()).parseFromString(s, \'text/xml\');\n
            }\n
            return (doc && doc.documentElement && doc.documentElement.nodeName != \'parsererror\') ? doc : null;\n
        };\n
        var parseJSON = $.parseJSON || function(s) {\n
            /*jslint evil:true */\n
            return window[\'eval\'](\'(\' + s + \')\');\n
        };\n
\n
        var httpData = function( xhr, type, s ) { // mostly lifted from jq1.4.4\n
\n
            var ct = xhr.getResponseHeader(\'content-type\') || \'\',\n
                xml = type === \'xml\' || !type && ct.indexOf(\'xml\') >= 0,\n
                data = xml ? xhr.responseXML : xhr.responseText;\n
\n
            if (xml && data.documentElement.nodeName === \'parsererror\') {\n
                if ($.error)\n
                    $.error(\'parsererror\');\n
            }\n
            if (s && s.dataFilter) {\n
                data = s.dataFilter(data, type);\n
            }\n
            if (typeof data === \'string\') {\n
                if (type === \'json\' || !type && ct.indexOf(\'json\') >= 0) {\n
                    data = parseJSON(data);\n
                } else if (type === "script" || !type && ct.indexOf("javascript") >= 0) {\n
                    $.globalEval(data);\n
                }\n
            }\n
            return data;\n
        };\n
\n
        return deferred;\n
    }\n
};\n
\n
/**\n
 * ajaxForm() provides a mechanism for fully automating form submission.\n
 *\n
 * The advantages of using this method instead of ajaxSubmit() are:\n
 *\n
 * 1: This method will include coordinates for <input type="image" /> elements (if the element\n
 *    is used to submit the form).\n
 * 2. This method will include the submit element\'s name/value data (for the element that was\n
 *    used to submit the form).\n
 * 3. This method binds the submit() method to the form for you.\n
 *\n
 * The options argument for ajaxForm works exactly as it does for ajaxSubmit.  ajaxForm merely\n
 * passes the options argument along after properly binding events for submit elements and\n
 * the form itself.\n
 */\n
$.fn.ajaxForm = function(options) {\n
    options = options || {};\n
    options.delegation = options.delegation && $.isFunction($.fn.on);\n
\n
    // in jQuery 1.3+ we can fix mistakes with the ready state\n
    if (!options.delegation && this.length === 0) {\n
        var o = { s: this.selector, c: this.context };\n
        if (!$.isReady && o.s) {\n
            log(\'DOM not ready, queuing ajaxForm\');\n
            $(function() {\n
                $(o.s,o.c).ajaxForm(options);\n
            });\n
            return this;\n
        }\n
        // is your DOM ready?  http://docs.jquery.com/Tutorials:Introducing_$(document).ready()\n
        log(\'terminating; zero elements found by selector\' + ($.isReady ? \'\' : \' (DOM not ready)\'));\n
        return this;\n
    }\n
\n
    if ( options.delegation ) {\n
        $(document)\n
            .off(\'submit.form-plugin\', this.selector, doAjaxSubmit)\n
            .off(\'click.form-plugin\', this.selector, captureSubmittingElement)\n
            .on(\'submit.form-plugin\', this.selector, options, doAjaxSubmit)\n
            .on(\'click.form-plugin\', this.selector, options, captureSubmittingElement);\n
        return this;\n
    }\n
\n
    return this.ajaxFormUnbind()\n
        .bind(\'submit.form-plugin\', options, doAjaxSubmit)\n
        .bind(\'click.form-plugin\', options, captureSubmittingElement);\n
};\n
\n
// private event handlers\n
function doAjaxSubmit(e) {\n
    /*jshint validthis:true */\n
    var options = e.data;\n
    if (!e.isDefaultPrevented()) { // if event has been canceled, don\'t proceed\n
        e.preventDefault();\n
        $(this).ajaxSubmit(options);\n
    }\n
}\n
\n
function captureSubmittingElement(e) {\n
    /*jshint validthis:true */\n
    var target = e.target;\n
    var $el = $(target);\n
    if (!($el.is("[type=submit],[type=image]"))) {\n
        // is this a child element of the submit el?  (ex: a span within a button)\n
        var t = $el.closest(\'[type=submit]\');\n
        if (t.length === 0) {\n
            return;\n
        }\n
        target = t[0];\n
    }\n
    var form = this;\n
    form.clk = target;\n
    if (target.type == \'image\') {\n
        if (e.offsetX !== undefined) {\n
            form.clk_x = e.offsetX;\n
            form.clk_y = e.offsetY;\n
        } else if (typeof $.fn.offset == \'function\') {\n
            var offset = $el.offset();\n
            form.clk_x = e.pageX - offset.left;\n
            form.clk_y = e.pageY - offset.top;\n
        } else {\n
            form.clk_x = e.pageX - target.offsetLeft;\n
            form.clk_y = e.pageY - target.offsetTop;\n
        }\n
    }\n
    // clear form vars\n
    setTimeout(function() { form.clk = form.clk_x = form.clk_y = null; }, 100);\n
}\n
\n
\n
// ajaxFormUnbind unbinds the event handlers that were bound by ajaxForm\n
$.fn.ajaxFormUnbind = function() {\n
    return this.unbind(\'submit.form-plugin click.form-plugin\');\n
};\n
\n
/**\n
 * formToArray() gathers form element data into an array of objects that can\n
 * be passed to any of the following ajax functions: $.get, $.post, or load.\n
 * Each object in the array has both a \'name\' and \'value\' property.  An example of\n
 * an array for a simple login form might be:\n
 *\n
 * [ { name: \'username\', value: \'jresig\' }, { name: \'password\', value: \'secret\' } ]\n
 *\n
 * It is this array that is passed to pre-submit callback functions provided to the\n
 * ajaxSubmit() and ajaxForm() methods.\n
 */\n
$.fn.formToArray = function(semantic, elements) {\n
    var a = [];\n
    if (this.length === 0) {\n
        return a;\n
    }\n
\n
    var form = this[0];\n
    var els = semantic ? form.getElementsByTagName(\'*\') : form.elements;\n
    if (!els) {\n
        return a;\n
    }\n
\n
    var i,j,n,v,el,max,jmax;\n
    for(i=0, max=els.length; i < max; i++) {\n
        el = els[i];\n
        n = el.name;\n
        if (!n) {\n
            continue;\n
        }\n
\n
        if (semantic && form.clk && el.type == "image") {\n
            // handle image inputs on the fly when semantic == true\n
            if(!el.disabled && form.clk == el) {\n
                a.push({name: n, value: $(el).val(), type: el.type });\n
                a.push({name: n+\'.x\', value: form.clk_x}, {name: n+\'.y\', value: form.clk_y});\n
            }\n
            continue;\n
        }\n
\n
        v = $.fieldValue(el, true);\n
        if (v && v.constructor == Array) {\n
            if (elements)\n
                elements.push(el);\n
            for(j=0, jmax=v.length; j < jmax; j++) {\n
                a.push({name: n, value: v[j]});\n
            }\n
        }\n
        else if (feature.fileapi && el.type == \'file\' && !el.disabled) {\n
            if (elements)\n
                elements.push(el);\n
            var files = el.files;\n
            if (files.length) {\n
                for (j=0; j < files.length; j++) {\n
                    a.push({name: n, value: files[j], type: el.type});\n
                }\n
            }\n
            else {\n
                // #180\n
                a.push({ name: n, value: \'\', type: el.type });\n
            }\n
        }\n
        else if (v !== null && typeof v != \'undefined\') {\n
            if (elements)\n
                elements.push(el);\n
            a.push({name: n, value: v, type: el.type, required: el.required});\n
        }\n
    }\n
\n
    if (!semantic && form.clk) {\n
        // input type==\'image\' are not found in elements array! handle it here\n
        var $input = $(form.clk), input = $input[0];\n
        n = input.name;\n
        if (n && !input.disabled && input.type == \'image\') {\n
            a.push({name: n, value: $input.val()});\n
            a.push({name: n+\'.x\', value: form.clk_x}, {name: n+\'.y\', value: form.clk_y});\n
        }\n
    }\n
    return a;\n
};\n
\n
/**\n
 * Serializes form data into a \'submittable\' string. This method will return a string\n
 * in the format: name1=value1&amp;name2=value2\n
 */\n
$.fn.formSerialize = function(semantic) {\n
    //hand off to jQuery.param for proper encoding\n
    return $.param(this.formToArray(semantic));\n
};\n
\n
/**\n
 * Serializes all field elements in the jQuery object into a query string.\n
 * This method will return a string in the format: name1=value1&amp;name2=value2\n
 */\n
$.fn.fieldSerialize = function(successful) {\n
    var a = [];\n
    this.each(function() {\n
        var n = this.name;\n
        if (!n) {\n
            return;\n
        }\n
        var v = $.fieldValue(this, successful);\n
        if (v && v.constructor == Array) {\n
            for (var i=0,max=v.length; i < max; i++) {\n
                a.push({name: n, value: v[i]});\n
            }\n
        }\n
        else if (v !== null && typeof v != \'undefined\') {\n
            a.push({name: this.name, value: v});\n
        }\n
    });\n
    //hand off to jQuery.param for proper encoding\n
    return $.param(a);\n
};\n
\n
/**\n
 * Returns the value(s) of the element in the matched set.  For example, consider the following form:\n
 *\n
 *  <form><fieldset>\n
 *      <input name="A" type="text" />\n
 *      <input name="A" type="text" />\n
 *      <input name="B" type="checkbox" value="B1" />\n
 *      <input name="B" type="checkbox" value="B2"/>\n
 *      <input name="C" type="radio" value="C1" />\n
 *      <input name="C" type="radio" value="C2" />\n
 *  </fieldset></form>\n
 *\n
 *  var v = $(\'input[type=text]\').fieldValue();\n
 *  // if no values are entered into the text inputs\n
 *  v == [\'\',\'\']\n
 *  // if values entered into the text inputs are \'foo\' and \'bar\'\n
 *  v == [\'foo\',\'bar\']\n
 *\n
 *  var v = $(\'input[type=checkbox]\').fieldValue();\n
 *  // if neither checkbox is checked\n
 *  v === undefined\n
 *  // if both checkboxes are checked\n
 *  v == [\'B1\', \'B2\']\n
 *\n
 *  var v = $(\'input[type=radio]\').fieldValue();\n
 *  // if neither radio is checked\n
 *  v === undefined\n
 *  // if first radio is checked\n
 *  v == [\'C1\']\n
 *\n
 * The successful argument controls whether or not the field element must be \'successful\'\n
 * (per http://www.w3.org/TR/html4/interact/forms.html#successful-controls).\n
 * The default value of the successful argument is true.  If this value is false the value(s)\n
 * for each element is returned.\n
 *\n
 * Note: This method *always* returns an array.  If no valid value can be determined the\n
 *    array will be empty, otherwise it will contain one or more values.\n
 */\n
$.fn.fieldValue = function(successful) {\n
    for (var val=[], i=0, max=this.length; i < max; i++) {\n
        var el = this[i];\n
        var v = $.fieldValue(el, successful);\n
        if (v === null || typeof v == \'undefined\' || (v.constructor == Array && !v.length)) {\n
            continue;\n
        }\n
        if (v.constructor == Array)\n
            $.merge(val, v);\n
        else\n
            val.push(v);\n
    }\n
    return val;\n
};\n
\n
/**\n
 * Returns the value of the field element.\n
 */\n
$.fieldValue = function(el, successful) {\n
    var n = el.name, t = el.type, tag = el.tagName.toLowerCase();\n
    if (successful === undefined) {\n
        successful = true;\n
    }\n
\n
    if (successful && (!n || el.disabled || t == \'reset\' || t == \'button\' ||\n
        (t == \'checkbox\' || t == \'radio\') && !el.checked ||\n
        (t == \'submit\' || t == \'image\') && el.form && el.form.clk != el ||\n
        tag == \'select\' && el.selectedIndex == -1)) {\n
            return null;\n
    }\n
\n
    if (tag == \'select\') {\n
        var index = el.selectedIndex;\n
        if (index < 0) {\n
            return null;\n
        }\n
        var a = [], ops = el.options;\n
        var one = (t == \'select-one\');\n
        var max = (one ? index+1 : ops.length);\n
        for(var i=(one ? index : 0); i < max; i++) {\n
            var op = ops[i];\n
            if (op.selected) {\n
                var v = op.value;\n
                if (!v) { // extra pain for IE...\n
                    v = (op.attributes && op.attributes[\'value\'] && !(op.attributes[\'value\'].specified)) ? op.text : op.value;\n
                }\n
                if (one) {\n
                    return v;\n
                }\n
                a.push(v);\n
            }\n
        }\n
        return a;\n
    }\n
    return $(el).val();\n
};\n
\n
/**\n
 * Clears the form data.  Takes the following actions on the form\'s input fields:\n
 *  - input text fields will have their \'value\' property set to the empty string\n
 *  - select elements will have their \'selectedIndex\' property set to -1\n
 *  - checkbox and radio inputs will have their \'checked\' property set to false\n
 *  - inputs of type submit, button, reset, and hidden will *not* be effected\n
 *  - button elements will *not* be effected\n
 */\n
$.fn.clearForm = function(includeHidden) {\n
    return this.each(function() {\n
        $(\'input,select,textarea\', this).clearFields(includeHidden);\n
    });\n
};\n
\n
/**\n
 * Clears the selected form elements.\n
 */\n
$.fn.clearFields = $.fn.clearInputs = function(includeHidden) {\n
    var re = /^(?:color|date|datetime|email|month|number|password|range|search|tel|text|time|url|week)$/i; // \'hidden\' is not in this list\n
    return this.each(function() {\n
        var t = this.type, tag = this.tagName.toLowerCase();\n
        if (re.test(t) || tag == \'textarea\') {\n
            this.value = \'\';\n
        }\n
        else if (t == \'checkbox\' || t == \'radio\') {\n
            this.checked = false;\n
        }\n
        else if (tag == \'select\') {\n
            this.selectedIndex = -1;\n
        }\n
\t\telse if (t == "file") {\n
\t\t\tif (/MSIE/.test(navigator.userAgent)) {\n
\t\t\t\t$(this).replaceWith($(this).clone(true));\n
\t\t\t} else {\n
\t\t\t\t$(this).val(\'\');\n
\t\t\t}\n
\t\t}\n
        else if (includeHidden) {\n
            // includeHidden can be the value true, or it can be a selector string\n
            // indicating a special test; for example:\n
            //  $(\'#myForm\').clearForm(\'.special:hidden\')\n
            // the above would clean hidden inputs that have the class of \'special\'\n
            if ( (includeHidden === true && /hidden/.test(t)) ||\n
                 (typeof includeHidden == \'string\' && $(this).is(includeHidden)) )\n
                this.value = \'\';\n
        }\n
    });\n
};\n
\n
/**\n
 * Resets the form data.  Causes all form elements to be reset to their original value.\n
 */\n
$.fn.resetForm = function() {\n
    return this.each(function() {\n
        // guard against an input with the name of \'reset\'\n
        // note that IE reports the reset function as an \'object\'\n
        if (typeof this.reset == \'function\' || (typeof this.reset == \'object\' && !this.reset.nodeType)) {\n
            this.reset();\n
        }\n
    });\n
};\n
\n
/**\n
 * Enables or disables any matching elements.\n
 */\n
$.fn.enable = function(b) {\n
    if (b === undefined) {\n
        b = true;\n
    }\n
    return this.each(function() {\n
        this.disabled = !b;\n
    });\n
};\n
\n
/**\n
 * Checks/unchecks any matching checkboxes or radio buttons and\n
 * selects/deselects and matching option elements.\n
 */\n
$.fn.selected = function(select) {\n
    if (select === undefined) {\n
        select = true;\n
    }\n
    return this.each(function() {\n
        var t = this.type;\n
        if (t == \'checkbox\' || t == \'radio\') {\n
            this.checked = select;\n
        }\n
        else if (this.tagName.toLowerCase() == \'option\') {\n
            var $sel = $(this).parent(\'select\');\n
            if (select && $sel[0] && $sel[0].type == \'select-one\') {\n
                // deselect all other options\n
                $sel.find(\'option\').selected(false);\n
            }\n
            this.selected = select;\n
        }\n
    });\n
};\n
\n
// expose debug var\n
$.fn.ajaxSubmit.debug = false;\n
\n
// helper fn for console logging\n
function log() {\n
    if (!$.fn.ajaxSubmit.debug)\n
        return;\n
    var msg = \'[jquery.form] \' + Array.prototype.join.call(arguments,\'\');\n
    if (window.console && window.console.log) {\n
        window.console.log(msg);\n
    }\n
    else if (window.opera && window.opera.postError) {\n
        window.opera.postError(msg);\n
    }\n
}\n
\n
})(jQuery);

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>39528</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>formplugin.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
