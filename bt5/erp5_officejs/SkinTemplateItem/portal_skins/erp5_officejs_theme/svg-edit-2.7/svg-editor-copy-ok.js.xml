<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts40515059.57</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>svg-editor-copy-ok.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAI=</string> </persistent>
            </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>160351</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="2" aka="AAAAAAAAAAI=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals globalStorage, widget, svgEditor, svgedit, canvg, DOMParser, FileReader, jQuery, $ */\n
/*jslint vars: true, eqeq: true, todo: true, forin: true, continue: true, regexp: true */\n
/*\n
 * svg-editor.js\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Alexis Deveria\n
 * Copyright(c) 2010 Pavol Rusnak\n
 * Copyright(c) 2010 Jeff Schiller\n
 * Copyright(c) 2010 Narendra Sisodiya\n
 *\n
 */\n
\n
// Dependencies:\n
// 1) units.js\n
// 2) browser.js\n
// 3) svgcanvas.js\n
\n
/*\n
TO-DOS\n
1. JSDoc\n
*/\n
\n
(function() {\n
\n
\tif (window.svgEditor) {\n
\t\treturn;\n
\t}\n
\twindow.svgEditor = (function($) {\n
\t\tvar editor = {};\n
\t\t// EDITOR PROPERTIES: (defined below)\n
\t\t//\t\tcurPrefs, curConfig, canvas, storage, uiStrings\n
\t\t//\n
\t\t// STATE MAINTENANCE PROPERTIES\n
\t\teditor.tool_scale = 1; // Dependent on icon size, so no need to make configurable?\n
\t\teditor.langChanged = false;\n
\t\teditor.showSaveWarning = false;\n
\t\teditor.storagePromptClosed = false; // For use with ext-storage.js\n
\n
\t\tvar svgCanvas, urldata,\n
\t\t\tisReady = false,\n
\t\t\tcallbacks = [],\n
\t\t\tcustomHandlers = {},\n
\t\t\t/**\n
\t\t\t* PREFS AND CONFIG\n
\t\t\t*/\n
\t\t\t// The iteration algorithm for defaultPrefs does not currently support array/objects\n
\t\t\tdefaultPrefs = {\n
\t\t\t\t// EDITOR OPTIONS (DIALOG)\n
\t\t\t\tlang: \'\', // Default to "en" if locale.js detection does not detect another language\n
\t\t\t\ticonsize: \'\', // Will default to \'s\' if the window height is smaller than the minimum height and \'m\' otherwise\n
\t\t\t\tbkgd_color: \'#FFF\',\n
\t\t\t\tbkgd_url: \'\',\n
\t\t\t\t// DOCUMENT PROPERTIES (DIALOG)\n
\t\t\t\timg_save: \'embed\',\n
\t\t\t\t// ALERT NOTICES\n
\t\t\t\t// Only shows in UI as far as alert notices, but useful to remember, so keeping as pref\n
\t\t\t\tsave_notice_done: false,\n
\t\t\t\texport_notice_done: false\n
\t\t\t},\n
\t\t\tcurPrefs = {},\n
\t\t\t// Note: The difference between Prefs and Config is that Prefs\n
\t\t\t//   can be changed in the UI and are stored in the browser,\n
\t\t\t//   while config cannot\n
\t\t\tcurConfig = {\n
\t\t\t\t// We do not put on defaultConfig to simplify object copying\n
\t\t\t\t//   procedures (we obtain instead from defaultExtensions)\n
\t\t\t\textensions: []\n
\t\t\t},\n
\t\t\tdefaultExtensions = [\n
\t\t\t\t\'ext-overview_window.js\',\n
\t\t\t\t\'ext-markers.js\',\n
\t\t\t\t\'ext-connector.js\',\n
\t\t\t\t\'ext-eyedropper.js\',\n
\t\t\t\t\'ext-shapes.js\',\n
\t\t\t\t\'ext-imagelib.js\',\n
\t\t\t\t\'ext-grid.js\',\n
\t\t\t\t\'ext-polygon.js\',\n
\t\t\t\t\'ext-star.js\',\n
\t\t\t\t\'ext-panning.js\',\n
\t\t\t\t\'ext-storage.js\'\n
\t\t\t],\n
\t\t\tdefaultConfig = {\n
\t\t\t\t// Todo: svgcanvas.js also sets and checks: show_outside_canvas, selectNew; add here?\n
\t\t\t\t// Change the following to preferences and add pref controls to the UI (e.g., initTool, wireframe, showlayers)?\n
\t\t\t\tcanvasName: \'default\',\n
\t\t\t\tcanvas_expansion: 3,\n
\t\t\t\tinitFill: {\n
\t\t\t\t\tcolor: \'FF0000\', // solid red\n
\t\t\t\t\topacity: 1\n
\t\t\t\t},\n
\t\t\t\tinitStroke: {\n
\t\t\t\t\twidth: 5,\n
\t\t\t\t\tcolor: \'000000\', // solid black\n
\t\t\t\t\topacity: 1\n
\t\t\t\t},\n
\t\t\t\tinitOpacity: 1,\n
\t\t\t\tcolorPickerCSS: null,\n
\t\t\t\tinitTool: \'select\',\n
\t\t\t\twireframe: false,\n
\t\t\t\tshowlayers: false,\n
\t\t\t\tno_save_warning: false,\n
\t\t\t\t// PATH CONFIGURATION\n
\t\t\t\t// The following path configuration items are disallowed in the URL (as should any future path configurations)\n
\t\t\t\timgPath: \'images/\',\n
\t\t\t\tlangPath: \'locale/\',\n
\t\t\t\textPath: \'extensions/\',\n
\t\t\t\tjGraduatePath: \'jgraduate/images/\',\n
\t\t\t\t// DOCUMENT PROPERTIES\n
\t\t\t\t// Change the following to a preference (already in the Document Properties dialog)?\n
\t\t\t\tdimensions: [640, 480],\n
\t\t\t\t// EDITOR OPTIONS\n
\t\t\t\t// Change the following to preferences (already in the Editor Options dialog)?\n
\t\t\t\tgridSnapping: false,\n
\t\t\t\tgridColor: \'#000\',\n
\t\t\t\tbaseUnit: \'px\',\n
\t\t\t\tsnappingStep: 10,\n
\t\t\t\tshowRulers: true,\n
\t\t\t\t// URL BEHAVIOR CONFIGURATION\n
\t\t\t\tpreventAllURLConfig: false,\n
\t\t\t\tpreventURLContentLoading: false,\n
\t\t\t\t// EXTENSION CONFIGURATION (see also preventAllURLConfig)\n
\t\t\t\tlockExtensions: false, // Disallowed in URL setting\n
\t\t\t\tnoDefaultExtensions: false, // noDefaultExtensions can only be meaningfully used in config.js or in the URL\n
\t\t\t\t// EXTENSION-RELATED (GRID)\n
\t\t\t\tshowGrid: false, // Set by ext-grid.js\n
\t\t\t\t// EXTENSION-RELATED (STORAGE)\n
\t\t\t\tnoStorageOnLoad: false, // Some interaction with ext-storage.js; prevent even the loading of previously saved local storage\n
\t\t\t\tforceStorage: false, // Some interaction with ext-storage.js; strongly discouraged from modification as it bypasses user privacy by preventing them from choosing whether to keep local storage or not\n
\t\t\t\temptyStorageOnDecline: false // Used by ext-storage.js; empty any prior storage if the user declines to store\n
\t\t\t},\n
\t\t\t/**\n
\t\t\t* LOCALE\n
\t\t\t* @todo Can we remove now that we are always loading even English? (unless locale is set to null)\n
\t\t\t*/\n
\t\t\tuiStrings = editor.uiStrings = {\n
\t\t\t\tcommon: {\n
\t\t\t\t\tok: \'OK\',\n
\t\t\t\t\tcancel: \'Cancel\',\n
\t\t\t\t\tkey_up: \'Up\',\n
\t\t\t\t\tkey_down: \'Down\',\n
\t\t\t\t\tkey_backspace: \'Backspace\',\n
\t\t\t\t\tkey_del: \'Del\'\n
\t\t\t\t},\n
\t\t\t\t// This is needed if the locale is English, since the locale strings are not read in that instance.\n
\t\t\t\tlayers: {\n
\t\t\t\t\tlayer: \'Layer\'\n
\t\t\t\t},\n
\t\t\t\tnotification: {\n
\t\t\t\t\tinvalidAttrValGiven: \'Invalid value given\',\n
\t\t\t\t\tnoContentToFitTo: \'No content to fit to\',\n
\t\t\t\t\tdupeLayerName: \'There is already a layer named that!\',\n
\t\t\t\t\tenterUniqueLayerName: \'Please enter a unique layer name\',\n
\t\t\t\t\tenterNewLayerName: \'Please enter the new layer name\',\n
\t\t\t\t\tlayerHasThatName: \'Layer already has that name\',\n
\t\t\t\t\tQmoveElemsToLayer: \'Move selected elements to layer \\\'%s\\\'?\',\n
\t\t\t\t\tQwantToClear: \'Do you want to clear the drawing?\\nThis will also erase your undo history!\',\n
\t\t\t\t\tQwantToOpen: \'Do you want to open a new file?\\nThis will also erase your undo history!\',\n
\t\t\t\t\tQerrorsRevertToSource: \'There were parsing errors in your SVG source.\\nRevert back to original SVG source?\',\n
\t\t\t\t\tQignoreSourceChanges: \'Ignore changes made to SVG source?\',\n
\t\t\t\t\tfeatNotSupported: \'Feature not supported\',\n
\t\t\t\t\tenterNewImgURL: \'Enter the new image URL\',\n
\t\t\t\t\tdefsFailOnSave: \'NOTE: Due to a bug in your browser, this image may appear wrong (missing gradients or elements). It will however appear correct once actually saved.\',\n
\t\t\t\t\tloadingImage: \'Loading image, please wait...\',\n
\t\t\t\t\tsaveFromBrowser: \'Select \\\'Save As...\\\' in your browser to save this image as a %s file.\',\n
\t\t\t\t\tnoteTheseIssues: \'Also note the following issues: \',\n
\t\t\t\t\tunsavedChanges: \'There are unsaved changes.\',\n
\t\t\t\t\tenterNewLinkURL: \'Enter the new hyperlink URL\',\n
\t\t\t\t\terrorLoadingSVG: \'Error: Unable to load SVG data\',\n
\t\t\t\t\tURLloadFail: \'Unable to load from URL\',\n
\t\t\t\t\tretrieving: \'Retrieving \\\'%s\\\' ...\'\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\tfunction loadSvgString (str, callback) {\n
\t\t\tvar success = svgCanvas.setSvgString(str) !== false;\n
\t\t\tcallback = callback || $.noop;\n
\t\t\tif (success) {\n
\t\t\t\tcallback(true);\n
\t\t\t} else {\n
\t\t\t\t$.alert(uiStrings.notification.errorLoadingSVG, function() {\n
\t\t\t\t\tcallback(false);\n
\t\t\t\t});\n
\t\t\t}\n
\t\t}\n
\n
\t\t/**\n
\t\t* EXPORTS\n
\t\t*/\n
\t\t\n
\t\t/**\n
\t\t* Store and retrieve preferences\n
\t\t* @param {string} key The preference name to be retrieved or set\n
\t\t* @param {string} [val] The value. If the value supplied is missing or falsey, no change to the preference will be made.\n
\t\t* @returns {string} If val is missing or falsey, the value of the previously stored preference will be returned.\n
\t\t* @todo Can we change setting on the jQuery namespace (onto editor) to avoid conflicts?\n
\t\t* @todo Review whether any remaining existing direct references to\n
\t\t*\tgetting curPrefs can be changed to use $.pref() getting to ensure\n
\t\t*\tdefaultPrefs fallback (also for sake of allowInitialUserOverride); specifically, bkgd_color could be changed so that\n
\t\t*\tthe pref dialog has a button to auto-calculate background, but otherwise uses $.pref() to be able to get default prefs\n
\t\t*\tor overridable settings\n
\t\t*/\n
\t\t$.pref = function (key, val) {\n
\t\t\tif (val) {\n
\t\t\t\tcurPrefs[key] = val;\n
\t\t\t\teditor.curPrefs = curPrefs; // Update exported value\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\treturn (key in curPrefs) ? curPrefs[key] : defaultPrefs[key];\n
\t\t};\n
\t\t\n
\t\t/**\n
\t\t* EDITOR PUBLIC METHODS\n
\t\t* @todo Sort these methods per invocation order, ideally with init at the end\n
\t\t* @todo Prevent execution until init executes if dependent on it?\n
\t\t*/\n
\n
\t\t/**\n
\t\t* Where permitted, sets canvas and/or defaultPrefs based on previous\n
\t\t*\tstorage. This will override URL settings (for security reasons) but\n
\t\t*\tnot config.js configuration (unless initial user overriding is explicitly\n
\t\t*\tpermitted there via allowInitialUserOverride).\n
\t\t* @todo Split allowInitialUserOverride into allowOverrideByURL and\n
\t\t*\tallowOverrideByUserStorage so config.js can disallow some\n
\t\t*\tindividual items for URL setting but allow for user storage AND/OR\n
\t\t*\tchange URL setting so that it always uses a different namespace,\n
\t\t*\tso it won\'t affect pre-existing user storage (but then if users saves\n
\t\t*\tthat, it will then be subject to tampering\n
\t\t*/\n
\t\teditor.loadContentAndPrefs = function () {\n
\t\t\tif (!curConfig.forceStorage && (curConfig.noStorageOnLoad || !document.cookie.match(/(?:^|;\\s*)store=(?:prefsAndContent|prefsOnly)/))) {\n
\t\t\t\treturn;\n
\t\t\t}\n
\n
\t\t\t// LOAD CONTENT\n
\t\t\tif (\'localStorage\' in window && // Cookies do not have enough available memory to hold large documents\n
\t\t\t\t(curConfig.forceStorage || (!curConfig.noStorageOnLoad && document.cookie.match(/(?:^|;\\s*)store=prefsAndContent/)))\n
\t\t\t) {\n
\t\t\t\tvar name = \'svgedit-\' + curConfig.canvasName;\n
\t\t\t\tvar cached = window.localStorage.getItem(name);\n
\t\t\t\tif (cached) {\n
\t\t\t\t\teditor.loadFromString(cached);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\t// LOAD PREFS\n
\t\t\tvar key, storage = false;\n
\t\t\t// var host = location.hostname,\n
\t\t\t//\tonWeb = host && host.indexOf(\'.\') >= 0;\n
\n
\t\t\t// Some FF versions throw security errors here\n
\t\t\ttry {\n
\t\t\t\tif (window.localStorage) { // && onWeb removed so Webkit works locally\n
\t\t\t\t\tstorage = localStorage;\n
\t\t\t\t}\n
\t\t\t} catch(err) {}\n
\t\t\teditor.storage = storage;\n
\n
\t\t\tfor (key in defaultPrefs) {\n
\t\t\t\tif (defaultPrefs.hasOwnProperty(key)) { // It\'s our own config, so we don\'t need to iterate up the prototype chain\n
\t\t\t\t\tvar storeKey = \'svg-edit-\' + key;\n
\t\t\t\t\tif (storage) {\n
\t\t\t\t\t\tvar val = storage.getItem(storeKey);\n
\t\t\t\t\t\tif (val) {\n
\t\t\t\t\t\t\tdefaultPrefs[key] = String(val); // Convert to string for FF (.value fails in Webkit)\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\telse if (window.widget) {\n
\t\t\t\t\t\tdefaultPrefs[key] = widget.preferenceForKey(storeKey);\n
\t\t\t\t\t}\n
\t\t\t\t\telse {\n
\t\t\t\t\t\tvar result = document.cookie.match(new RegExp(\'(?:^|;\\\\s*)\' + storeKey + \'=([^;]+)\'));\n
\t\t\t\t\t\tdefaultPrefs[key] = result ? decodeURIComponent(result[1]) : \'\';\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t};\n
\n
\t\t/**\n
\t\t* Allows setting of preferences or configuration (including extensions).\n
\t\t* @param {object} opts The preferences or configuration (including extensions)\n
\t\t* @param {object} [cfgCfg] Describes configuration which applies to the particular batch of supplied options\n
\t\t* @param {boolean} [cfgCfg.allowInitialUserOverride=false] Set to true if you wish\n
\t\t*\tto allow initial overriding of settings by the user via the URL\n
\t\t*\t(if permitted) or previously stored preferences (if permitted);\n
\t\t*\tnote that it will be too late if you make such calls in extension\n
\t\t*\tcode because the URL or preference storage settings will\n
\t\t*   have already taken place.\n
\t\t* @param {boolean} [cfgCfg.overwrite=true] Set to false if you wish to\n
\t\t*\tprevent the overwriting of prior-set preferences or configuration\n
\t\t*\t(URL settings will always follow this requirement for security\n
\t\t*\treasons, so config.js settings cannot be overridden unless it\n
\t\t*\texplicitly permits via "allowInitialUserOverride" but extension config\n
\t\t*\tcan be overridden as they will run after URL settings). Should\n
\t\t*   not be needed in config.js.\n
\t\t*/\n
\t\teditor.setConfig = function (opts, cfgCfg) {\n
\t\t\tcfgCfg = cfgCfg || {};\n
\t\t\tfunction extendOrAdd (cfgObj, key, val) {\n
\t\t\t\tif (cfgObj[key] && typeof cfgObj[key] === \'object\') {\n
\t\t\t\t\t$.extend(true, cfgObj[key], val);\n
\t\t\t\t}\n
\t\t\t\telse {\n
\t\t\t\t\tcfgObj[key] = val;\n
\t\t\t\t}\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\t$.each(opts, function(key, val) {\n
\t\t\t\tif (opts.hasOwnProperty(key)) {\n
\t\t\t\t\t// Only allow prefs defined in defaultPrefs\n
\t\t\t\t\tif (defaultPrefs.hasOwnProperty(key)) {\n
\t\t\t\t\t\tif (cfgCfg.overwrite === false && (\n
\t\t\t\t\t\t\tcurConfig.preventAllURLConfig ||\n
\t\t\t\t\t\t\tcurPrefs.hasOwnProperty(key)\n
\t\t\t\t\t\t)) {\n
\t\t\t\t\t\t\treturn;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tif (cfgCfg.allowInitialUserOverride === true) {\n
\t\t\t\t\t\t\tdefaultPrefs[key] = val;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\telse {\n
\t\t\t\t\t\t\t$.pref(key, val);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\telse if (key === \'extensions\') {\n
\t\t\t\t\t\tif (cfgCfg.overwrite === false &&\n
\t\t\t\t\t\t\t(curConfig.preventAllURLConfig || curConfig.lockExtensions)\n
\t\t\t\t\t\t) {\n
\t\t\t\t\t\t\treturn;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tcurConfig.extensions = curConfig.extensions.concat(val); // We will handle any dupes later\n
\t\t\t\t\t}\n
\t\t\t\t\t// Only allow other curConfig if defined in defaultConfig\n
\t\t\t\t\telse if (defaultConfig.hasOwnProperty(key)) {\n
\t\t\t\t\t\tif (cfgCfg.overwrite === false && (\n
\t\t\t\t\t\t\tcurConfig.preventAllURLConfig ||\n
\t\t\t\t\t\t\tcurConfig.hasOwnProperty(key)\n
\t\t\t\t\t\t)) {\n
\t\t\t\t\t\t\treturn;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t// Potentially overwriting of previously set config\n
\t\t\t\t\t\tif (curConfig.hasOwnProperty(key)) {\n
\t\t\t\t\t\t\tif (cfgCfg.overwrite === false) {\n
\t\t\t\t\t\t\t\treturn;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\textendOrAdd(curConfig, key, val);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\telse {\n
\t\t\t\t\t\t\tif (cfgCfg.allowInitialUserOverride === true) {\n
\t\t\t\t\t\t\t\textendOrAdd(defaultConfig, key, val);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\telse {\n
\t\t\t\t\t\t\t\tif (defaultConfig[key] && typeof defaultConfig[key] === \'object\') {\n
\t\t\t\t\t\t\t\t\tcurConfig[key] = {};\n
\t\t\t\t\t\t\t\t\t$.extend(true, curConfig[key], val); // Merge properties recursively, e.g., on initFill, initStroke objects\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\telse {\n
\t\t\t\t\t\t\t\t\tcurConfig[key] = val;\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t});\n
\t\t\teditor.curConfig = curConfig; // Update exported value\n
\t\t};\n
\n
\t\t/**\n
\t\t* @param {object} opts Extension mechanisms may call setCustomHandlers with three functions: opts.open, opts.save, and opts.exportImage\n
\t\t* opts.open\'s responsibilities are:\n
\t\t*\t- invoke a file chooser dialog in \'open\' mode\n
\t\t*\t- let user pick a SVG file\n
\t\t*\t- calls setCanvas.setSvgString() with the string contents of that file\n
\t\t*  opts.save\'s responsibilities are:\n
\t\t*\t- accept the string contents of the current document\n
\t\t*\t- invoke a file chooser dialog in \'save\' mode\n
\t\t*\t- save the file to location chosen by the user\n
\t\t*  opts.exportImage\'s responsibilities (with regard to the object it is supplied in its 2nd argument) are:\n
\t\t*\t- inform user of any issues supplied via the "issues" property\n
\t\t*\t- convert the "svg" property SVG string into an image for export;\n
\t\t*\t\tutilize the properties "type" (currently \'PNG\', \'JPEG\', \'BMP\',\n
\t\t*\t\t\'WEBP\'), "mimeType", and "quality" (for \'JPEG\' and \'WEBP\'\n
\t\t*\t\ttypes) to determine the proper output.\n
\t\t*/\n
\t\teditor.setCustomHandlers = function (opts) {\n
\t\t\teditor.ready(function() {\n
\t\t\t\tif (opts.open) {\n
\t\t\t\t\t$(\'#tool_open > input[type="file"]\').remove();\n
\t\t\t\t\t$(\'#tool_open\').show();\n
\t\t\t\t\tsvgCanvas.open = opts.open;\n
\t\t\t\t}\n
\t\t\t\tif (opts.save) {\n
\t\t\t\t\teditor.showSaveWarning = false;\n
\t\t\t\t\tsvgCanvas.bind(\'saved\', opts.save);\n
\t\t\t\t}\n
\t\t\t\tif (opts.exportImage || opts.pngsave) { // Deprecating pngsave\n
\t\t\t\t\tsvgCanvas.bind(\'exported\', opts.exportImage || opts.pngsave);\n
\t\t\t\t}\n
\t\t\t\tcustomHandlers = opts;\n
\t\t\t});\n
\t\t};\n
\n
\t\teditor.randomizeIds = function () {\n
\t\t\tsvgCanvas.randomizeIds(arguments);\n
\t\t};\n
\n
\t\teditor.init = function () {\n
\t\t\t// Todo: Avoid var-defined functions and group functions together, etc. where possible\n
\t\t\tvar good_langs = [];\n
\t\t\t$(\'#lang_select option\').each(function() {\n
\t\t\t\tgood_langs.push(this.value);\n
\t\t\t});\n
\n
\t\t\tfunction setupCurPrefs () {\n
\t\t\t\tcurPrefs = $.extend(true, {}, defaultPrefs, curPrefs); // Now safe to merge with priority for curPrefs in the event any are already set\n
\t\t\t\t// Export updated prefs\n
\t\t\t\teditor.curPrefs = curPrefs;\n
\t\t\t}\n
\t\t\tfunction setupCurConfig () {\n
\t\t\t\tcurConfig = $.extend(true, {}, defaultConfig, curConfig); // Now safe to merge with priority for curConfig in the event any are already set\n
\t\t\t\t\n
\t\t\t\t// Now deal with extensions\n
\t\t\t\tif (!curConfig.noDefaultExtensions) {\n
\t\t\t\t\tcurConfig.extensions = curConfig.extensions.concat(defaultExtensions);\n
\t\t\t\t}\n
\t\t\t\t// ...and remove any dupes\n
\t\t\t\tcurConfig.extensions = $.grep(curConfig.extensions, function (n, i) {\n
\t\t\t\t\treturn i === curConfig.extensions.indexOf(n);\n
\t\t\t\t});\n
\t\t\t\t// Export updated config\n
\t\t\t\teditor.curConfig = curConfig;\n
\t\t\t}\n
\t\t\t(function() {\n
\t\t\t\t// Load config/data from URL if given\n
\t\t\t\tvar src, qstr;\n
\t\t\t\turldata = $.deparam.querystring(true);\n
\t\t\t\tif (!$.isEmptyObject(urldata)) {\n
\t\t\t\t\tif (urldata.dimensions) {\n
\t\t\t\t\t\turldata.dimensions = urldata.dimensions.split(\',\');\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tif (urldata.bkgd_color) {\n
\t\t\t\t\t\turldata.bkgd_color = \'#\' + urldata.bkgd_color;\n
\t\t\t\t\t}\n
\t\t\t\n
\t\t\t\t\tif (urldata.extensions) {\n
\t\t\t\t\t\t// For security reasons, disallow cross-domain or cross-folder extensions via URL\n
\t\t\t\t\t\turldata.extensions = urldata.extensions.match(/[:\\/\\\\]/) ? \'\' : urldata.extensions.split(\',\');\n
\t\t\t\t\t}\n
\n
\t\t\t\t\t// Disallowing extension paths via URL for\n
\t\t\t\t\t// security reasons, even for same-domain\n
\t\t\t\t\t// ones given potential to interact in undesirable\n
\t\t\t\t\t// ways with other script resources\n
\t\t\t\t\t$.each(\n
\t\t\t\t\t\t[\n
\t\t\t\t\t\t\t\'extPath\', \'imgPath\',\n
\t\t\t\t\t\t\t\'langPath\', \'jGraduatePath\'\n
\t\t\t\t\t\t],\n
\t\t\t\t\t\tfunction (pathConfig) {\n
\t\t\t\t\t\t\tif (urldata[pathConfig]) {\n
\t\t\t\t\t\t\t\tdelete urldata[pathConfig];\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t);\n
\n
\t\t\t\t\tsvgEditor.setConfig(urldata, {overwrite: false}); // Note: source, url, and paramurl (as with storagePrompt later) are not set on config but are used below\n
\t\t\t\t\t\n
\t\t\t\t\tsetupCurConfig();\n
\n
\t\t\t\t\tif (!curConfig.preventURLContentLoading) {\n
\t\t\t\t\t\tsrc = urldata.source;\n
\t\t\t\t\t\tqstr = $.param.querystring();\n
\t\t\t\t\t\tif (!src) { // urldata.source may have been null if it ended with \'=\'\n
\t\t\t\t\t\t\tif (qstr.indexOf(\'source=data:\') >= 0) {\n
\t\t\t\t\t\t\t\tsrc = qstr.match(/source=(data:[^&]*)/)[1];\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tif (src) {\n
\t\t\t\t\t\t\tif (src.indexOf(\'data:\') === 0) {\n
\t\t\t\t\t\t\t\t// plusses get replaced by spaces, so re-insert\n
\t\t\t\t\t\t\t\tsrc = src.replace(/ /g, \'+\');\n
\t\t\t\t\t\t\t\teditor.loadFromDataURI(src);\n
\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\teditor.loadFromString(src);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\treturn;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tif (qstr.indexOf(\'paramurl=\') !== -1) {\n
\t\t\t\t\t\t\t// Get parameter URL (use full length of remaining location.href)\n
\t\t\t\t\t\t\tsvgEditor.loadFromURL(qstr.substr(9));\n
\t\t\t\t\t\t\treturn;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tif (urldata.url) {\n
\t\t\t\t\t\t\tsvgEditor.loadFromURL(urldata.url);\n
\t\t\t\t\t\t\treturn;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\tif (!urldata.noStorageOnLoad || curConfig.forceStorage) {\n
\t\t\t\t\t\tsvgEditor.loadContentAndPrefs();\n
\t\t\t\t\t}\n
\t\t\t\t\tsetupCurPrefs();\n
\t\t\t\t}\n
\t\t\t\telse {\n
\t\t\t\t\tsetupCurConfig();\n
\t\t\t\t\tsvgEditor.loadContentAndPrefs();\n
\t\t\t\t\tsetupCurPrefs();\n
\t\t\t\t}\n
\t\t\t}());\n
\n
\t\t\t// For external openers\n
\t\t\t(function() {\n
\t\t\t\t// let the opener know SVG Edit is ready (now that config is set up)\n
\t\t\t\tvar svgEditorReadyEvent,\n
\t\t\t\t\tw = window.opener;\n
\t\t\t\tif (w) {\n
\t\t\t\t\ttry {\n
\t\t\t\t\t\tsvgEditorReadyEvent = w.document.createEvent(\'Event\');\n
\t\t\t\t\t\tsvgEditorReadyEvent.initEvent(\'svgEditorReady\', true, true);\n
\t\t\t\t\t\tw.document.documentElement.dispatchEvent(svgEditorReadyEvent);\n
\t\t\t\t\t}\n
\t\t\t\t\tcatch(e) {}\n
\t\t\t\t}\n
\t\t\t}());\n
\t\t\t\n
\t\t\tvar setIcon = editor.setIcon = function(elem, icon_id, forcedSize) {\n
\t\t\t\tvar icon = (typeof icon_id === \'string\') ? $.getSvgIcon(icon_id, true) : icon_id.clone();\n
\t\t\t\tif (!icon) {\n
\t\t\t\t\tconsole.log(\'NOTE: Icon image missing: \' + icon_id);\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\t\t\t\t$(elem).empty().append(icon);\n
\t\t\t};\n
\n
\t\t\tvar extFunc = function() {\n
\t\t\t\t$.each(curConfig.extensions, function() {\n
\t\t\t\t\tvar extname = this;\n
\t\t\t\t\t$.getScript(curConfig.extPath + extname, function(d) {\n
\t\t\t\t\t\t// Fails locally in Chrome 5\n
\t\t\t\t\t\tif (!d) {\n
\t\t\t\t\t\t\tvar s = document.createElement(\'script\');\n
\t\t\t\t\t\t\ts.src = curConfig.extPath + extname;\n
\t\t\t\t\t\t\tdocument.querySelector(\'head\').appendChild(s);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t});\n
\t\t\t\t});\n
\n
\t\t\t\t// var lang = (\'lang\' in curPrefs) ? curPrefs.lang : null;\n
\t\t\t\teditor.putLocale(null, good_langs);\n
\t\t\t};\n
\n
\t\t\t// Load extensions\n
\t\t\t// Bit of a hack to run extensions in local Opera/IE9\n
\t\t\tif (document.location.protocol === \'file:\') {\n
\t\t\t\tsetTimeout(extFunc, 100);\n
\t\t\t} else {\n
\t\t\t\textFunc();\n
\t\t\t}\n
\t\t\t$.svgIcons(curConfig.imgPath + \'svg_edit_icons.svg\', {\n
\t\t\t\tw:24, h:24,\n
\t\t\t\tid_match: false,\n
\t\t\t\tno_img: !svgedit.browser.isWebkit(), // Opera & Firefox 4 gives odd behavior w/images\n
\t\t\t\tfallback_path: curConfig.imgPath,\n
\t\t\t\tfallback: {\n
\t\t\t\t\t\'new_image\': \'clear.png\',\n
\t\t\t\t\t\'save\': \'save.png\',\n
\t\t\t\t\t\'open\': \'open.png\',\n
\t\t\t\t\t\'source\': \'source.png\',\n
\t\t\t\t\t\'docprops\': \'document-properties.png\',\n
\t\t\t\t\t\'wireframe\': \'wireframe.png\',\n
\n
\t\t\t\t\t\'undo\': \'undo.png\',\n
\t\t\t\t\t\'redo\': \'redo.png\',\n
\n
\t\t\t\t\t\'select\': \'select.png\',\n
\t\t\t\t\t\'select_node\': \'select_node.png\',\n
\t\t\t\t\t\'pencil\': \'fhpath.png\',\n
\t\t\t\t\t\'pen\': \'line.png\',\n
\t\t\t\t\t\'square\': \'square.png\',\n
\t\t\t\t\t\'rect\': \'rect.png\',\n
\t\t\t\t\t\'fh_rect\': \'freehand-square.png\',\n
\t\t\t\t\t\'circle\': \'circle.png\',\n
\t\t\t\t\t\'ellipse\': \'ellipse.png\',\n
\t\t\t\t\t\'fh_ellipse\': \'freehand-circle.png\',\n
\t\t\t\t\t\'path\': \'path.png\',\n
\t\t\t\t\t\'text\': \'text.png\',\n
\t\t\t\t\t\'image\': \'image.png\',\n
\t\t\t\t\t\'zoom\': \'zoom.png\',\n
\n
\t\t\t\t\t\'clone\': \'clone.png\',\n
\t\t\t\t\t\'node_clone\': \'node_clone.png\',\n
\t\t\t\t\t\'delete\': \'delete.png\',\n
\t\t\t\t\t\'node_delete\': \'node_delete.png\',\n
\t\t\t\t\t\'group\': \'shape_group_elements.png\',\n
\t\t\t\t\t\'ungroup\': \'shape_ungroup.png\',\n
\t\t\t\t\t\'move_top\': \'move_top.png\',\n
\t\t\t\t\t\'move_bottom\': \'move_bottom.png\',\n
\t\t\t\t\t\'to_path\': \'to_path.png\',\n
\t\t\t\t\t\'link_controls\': \'link_controls.png\',\n
\t\t\t\t\t\'reorient\': \'reorient.png\',\n
\n
\t\t\t\t\t\'align_left\': \'align-left.png\',\n
\t\t\t\t\t\'align_center\': \'align-center.png\',\n
\t\t\t\t\t\'align_right\': \'align-right.png\',\n
\t\t\t\t\t\'align_top\': \'align-top.png\',\n
\t\t\t\t\t\'align_middle\': \'align-middle.png\',\n
\t\t\t\t\t\'align_bottom\': \'align-bottom.png\',\n
\n
\t\t\t\t\t\'go_up\': \'go-up.png\',\n
\t\t\t\t\t\'go_down\': \'go-down.png\',\n
\n
\t\t\t\t\t\'ok\': \'save.png\',\n
\t\t\t\t\t\'cancel\': \'cancel.png\',\n
\n
\t\t\t\t\t\'arrow_right\': \'flyouth.png\',\n
\t\t\t\t\t\'arrow_down\': \'dropdown.gif\'\n
\t\t\t\t},\n
\t\t\t\tplacement: {\n
\t\t\t\t\t\'#logo\': \'logo\',\n
\n
\t\t\t\t\t\'#tool_clear div,#layer_new\': \'new_image\',\n
\t\t\t\t\t\'#tool_save div\': \'save\',\n
\t\t\t\t\t\'#tool_export div\': \'export\',\n
\t\t\t\t\t\'#tool_open div div\': \'open\',\n
\t\t\t\t\t\'#tool_import div div\': \'import\',\n
\t\t\t\t\t\'#tool_source\': \'source\',\n
\t\t\t\t\t\'#tool_docprops > div\': \'docprops\',\n
\t\t\t\t\t\'#tool_wireframe\': \'wireframe\',\n
\n
\t\t\t\t\t\'#tool_undo\': \'undo\',\n
\t\t\t\t\t\'#tool_redo\': \'redo\',\n
\n
\t\t\t\t\t\'#tool_select\': \'select\',\n
\t\t\t\t\t\'#tool_fhpath\': \'pencil\',\n
\t\t\t\t\t\'#tool_line\': \'pen\',\n
\t\t\t\t\t\'#tool_rect,#tools_rect_show\': \'rect\',\n
\t\t\t\t\t\'#tool_square\': \'square\',\n
\t\t\t\t\t\'#tool_fhrect\': \'fh_rect\',\n
\t\t\t\t\t\'#tool_ellipse,#tools_ellipse_show\': \'ellipse\',\n
\t\t\t\t\t\'#tool_circle\': \'circle\',\n
\t\t\t\t\t\'#tool_fhellipse\': \'fh_ellipse\',\n
\t\t\t\t\t\'#tool_path\': \'path\',\n
\t\t\t\t\t\'#tool_text,#layer_rename\': \'text\',\n
\t\t\t\t\t\'#tool_image\': \'image\',\n
\t\t\t\t\t\'#tool_zoom\': \'zoom\',\n
\n
\t\t\t\t\t\'#tool_clone,#tool_clone_multi\': \'clone\',\n
\t\t\t\t\t\'#tool_node_clone\': \'node_clone\',\n
\t\t\t\t\t\'#layer_delete,#tool_delete,#tool_delete_multi\': \'delete\',\n
\t\t\t\t\t\'#tool_node_delete\': \'node_delete\',\n
\t\t\t\t\t\'#tool_add_subpath\': \'add_subpath\',\n
\t\t\t\t\t\'#tool_openclose_path\': \'open_path\',\n
\t\t\t\t\t\'#tool_move_top\': \'move_top\',\n
\t\t\t\t\t\'#tool_move_bottom\': \'move_bottom\',\n
\t\t\t\t\t\'#tool_topath\': \'to_path\',\n
\t\t\t\t\t\'#tool_node_link\': \'link_controls\',\n
\t\t\t\t\t\'#tool_reorient\': \'reorient\',\n
\t\t\t\t\t\'#tool_group_elements\': \'group_elements\',\n
\t\t\t\t\t\'#tool_ungroup\': \'ungroup\',\n
\t\t\t\t\t\'#tool_unlink_use\': \'unlink_use\',\n
\n
\t\t\t\t\t\'#tool_alignleft, #tool_posleft\': \'align_left\',\n
\t\t\t\t\t\'#tool_aligncenter, #tool_poscenter\': \'align_center\',\n
\t\t\t\t\t\'#tool_alignright, #tool_posright\': \'align_right\',\n
\t\t\t\t\t\'#tool_aligntop, #tool_postop\': \'align_top\',\n
\t\t\t\t\t\'#tool_alignmiddle, #tool_posmiddle\': \'align_middle\',\n
\t\t\t\t\t\'#tool_alignbottom, #tool_posbottom\': \'align_bottom\',\n
\t\t\t\t\t\'#cur_position\': \'align\',\n
\n
\t\t\t\t\t\'#linecap_butt,#cur_linecap\': \'linecap_butt\',\n
\t\t\t\t\t\'#linecap_round\': \'linecap_round\',\n
\t\t\t\t\t\'#linecap_square\': \'linecap_square\',\n
\n
\t\t\t\t\t\'#linejoin_miter,#cur_linejoin\': \'linejoin_miter\',\n
\t\t\t\t\t\'#linejoin_round\': \'linejoin_round\',\n
\t\t\t\t\t\'#linejoin_bevel\': \'linejoin_bevel\',\n
\n
\t\t\t\t\t\'#url_notice\': \'warning\',\n
\n
\t\t\t\t\t\'#layer_up\': \'go_up\',\n
\t\t\t\t\t\'#layer_down\': \'go_down\',\n
\t\t\t\t\t\'#layer_moreopts\': \'context_menu\',\n
\t\t\t\t\t\'#layerlist td.layervis\': \'eye\',\n
\n
\t\t\t\t\t\'#tool_source_save,#tool_docprops_save,#tool_prefs_save\': \'ok\',\n
\t\t\t\t\t\'#tool_source_cancel,#tool_docprops_cancel,#tool_prefs_cancel\': \'cancel\',\n
\n
\t\t\t\t\t\'#rwidthLabel, #iwidthLabel\': \'width\',\n
\t\t\t\t\t\'#rheightLabel, #iheightLabel\': \'height\',\n
\t\t\t\t\t\'#cornerRadiusLabel span\': \'c_radius\',\n
\t\t\t\t\t\'#angleLabel\': \'angle\',\n
\t\t\t\t\t\'#linkLabel,#tool_make_link,#tool_make_link_multi\': \'globe_link\',\n
\t\t\t\t\t\'#zoomLabel\': \'zoom\',\n
\t\t\t\t\t\'#tool_fill label\': \'fill\',\n
\t\t\t\t\t\'#tool_stroke .icon_label\': \'stroke\',\n
\t\t\t\t\t\'#group_opacityLabel\': \'opacity\',\n
\t\t\t\t\t\'#blurLabel\': \'blur\',\n
\t\t\t\t\t\'#font_sizeLabel\': \'fontsize\',\n
\n
\t\t\t\t\t\'.flyout_arrow_horiz\': \'arrow_right\',\n
\t\t\t\t\t\'.dropdown button, #main_button .dropdown\': \'arrow_down\',\n
\t\t\t\t\t\'#palette .palette_item:first, #fill_bg, #stroke_bg\': \'no_color\'\n
\t\t\t\t},\n
\t\t\t\tresize: {\n
\t\t\t\t\t\'#logo .svg_icon\': 28,\n
\t\t\t\t\t\'.flyout_arrow_horiz .svg_icon\': 5,\n
\t\t\t\t\t\'.layer_button .svg_icon, #layerlist td.layervis .svg_icon\': 14,\n
\t\t\t\t\t\'.dropdown button .svg_icon\': 7,\n
\t\t\t\t\t\'#main_button .dropdown .svg_icon\': 9,\n
\t\t\t\t\t\'.palette_item:first .svg_icon\' : 15,\n
\t\t\t\t\t\'#fill_bg .svg_icon, #stroke_bg .svg_icon\': 16,\n
\t\t\t\t\t\'.toolbar_button button .svg_icon\': 16,\n
\t\t\t\t\t\'.stroke_tool div div .svg_icon\': 20,\n
\t\t\t\t\t\'#tools_bottom label .svg_icon\': 18\n
\t\t\t\t},\n
\t\t\t\tcallback: function(icons) {\n
\t\t\t\t\t$(\'.toolbar_button button > svg, .toolbar_button button > img\').each(function() {\n
\t\t\t\t\t\t$(this).parent().prepend(this);\n
\t\t\t\t\t});\n
\n
\t\t\t\t\tvar min_height,\n
\t\t\t\t\t\ttleft = $(\'#tools_left\');\n
\t\t\t\t\tif (tleft.length !== 0) {\n
\t\t\t\t\t\tmin_height = tleft.offset().top + tleft.outerHeight();\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\tvar size = $.pref(\'iconsize\');\n
\t\t\t\t\tsvgEditor.setIconSize(size || ($(window).height() < min_height ? \'s\': \'m\'));\n
\n
\t\t\t\t\t// Look for any missing flyout icons from plugins\n
\t\t\t\t\t$(\'.tools_flyout\').each(function() {\n
\t\t\t\t\t\tvar shower = $(\'#\' + this.id + \'_show\');\n
\t\t\t\t\t\tvar sel = shower.attr(\'data-curopt\');\n
\t\t\t\t\t\t// Check if there\'s an icon here\n
\t\t\t\t\t\tif (!shower.children(\'svg, img\').length) {\n
\t\t\t\t\t\t\tvar clone = $(sel).children().clone();\n
\t\t\t\t\t\t\tif (clone.length) {\n
\t\t\t\t\t\t\t\tclone[0].removeAttribute(\'style\'); //Needed for Opera\n
\t\t\t\t\t\t\t\tshower.append(clone);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t});\n
\n
\t\t\t\t\tsvgEditor.runCallbacks();\n
\n
\t\t\t\t\tsetTimeout(function() {\n
\t\t\t\t\t\t$(\'.flyout_arrow_horiz:empty\').each(function() {\n
\t\t\t\t\t\t\t$(this).append($.getSvgIcon(\'arrow_right\').width(5).height(5));\n
\t\t\t\t\t\t});\n
\t\t\t\t\t}, 1);\n
\t\t\t\t}\n
\t\t\t});\n
\n
\t\t\teditor.canvas = svgCanvas = new $.SvgCanvas(document.getElementById(\'svgcanvas\'), curConfig);\n
\t\t\tvar supportsNonSS, resize_timer, changeZoom, Actions, curScrollPos,\n
\t\t\t\tpalette = [ // Todo: Make into configuration item?\n
\t\t\t\t\t\'#000000\', \'#3f3f3f\', \'#7f7f7f\', \'#bfbfbf\', \'#ffffff\',\n
\t\t\t\t\t\'#ff0000\', \'#ff7f00\', \'#ffff00\', \'#7fff00\',\n
\t\t\t\t\t\'#00ff00\', \'#00ff7f\', \'#00ffff\', \'#007fff\',\n
\t\t\t\t\t\'#0000ff\', \'#7f00ff\', \'#ff00ff\', \'#ff007f\',\n
\t\t\t\t\t\'#7f0000\', \'#7f3f00\', \'#7f7f00\', \'#3f7f00\',\n
\t\t\t\t\t\'#007f00\', \'#007f3f\', \'#007f7f\', \'#003f7f\',\n
\t\t\t\t\t\'#00007f\', \'#3f007f\', \'#7f007f\', \'#7f003f\',\n
\t\t\t\t\t\'#ffaaaa\', \'#ffd4aa\', \'#ffffaa\', \'#d4ffaa\',\n
\t\t\t\t\t\'#aaffaa\', \'#aaffd4\', \'#aaffff\', \'#aad4ff\',\n
\t\t\t\t\t\'#aaaaff\', \'#d4aaff\', \'#ffaaff\', \'#ffaad4\'\n
\t\t\t\t],\n
\t\t\t\tmodKey = (svgedit.browser.isMac() ? \'meta+\' : \'ctrl+\'), // ⌘\n
\t\t\t\tpath = svgCanvas.pathActions,\n
\t\t\t\tundoMgr = svgCanvas.undoMgr,\n
\t\t\t\tUtils = svgedit.utilities,\n
\t\t\t\tdefaultImageURL = curConfig.imgPath + \'logo.png\',\n
\t\t\t\tworkarea = $(\'#workarea\'),\n
\t\t\t\tcanv_menu = $(\'#cmenu_canvas\'),\n
\t\t\t\t// layer_menu = $(\'#cmenu_layers\'), // Unused\n
\t\t\t\texportWindow = null,\n
\t\t\t\tzoomInIcon = \'crosshair\',\n
\t\t\t\tzoomOutIcon = \'crosshair\',\n
\t\t\t\tui_context = \'toolbars\',\n
\t\t\t\torigSource = \'\',\n
\t\t\t\tpaintBox = {fill: null, stroke:null};\n
\t\t\t\n
\t\t\t// This sets up alternative dialog boxes. They mostly work the same way as\n
\t\t\t// their UI counterparts, expect instead of returning the result, a callback\n
\t\t\t// needs to be included that returns the result as its first parameter.\n
\t\t\t// In the future we may want to add additional types of dialog boxes, since\n
\t\t\t// they should be easy to handle this way.\n
\t\t\t(function() {\n
\t\t\t\t$(\'#dialog_container\').draggable({cancel: \'#dialog_content, #dialog_buttons *\', containment: \'window\'});\n
\t\t\t\tvar box = $(\'#dialog_box\'),\n
\t\t\t\t\tbtn_holder = $(\'#dialog_buttons\'),\n
\t\t\t\t\tdialog_content = $(\'#dialog_content\'),\n
\t\t\t\t\tdbox = function(type, msg, callback, defaultVal, opts, changeCb, checkbox) {\n
\t\t\t\t\t\tvar ok, ctrl, chkbx;\n
\t\t\t\t\t\tdialog_content.html(\'<p>\'+msg.replace(/\\n/g, \'</p><p>\')+\'</p>\')\n
\t\t\t\t\t\t\t.toggleClass(\'prompt\', (type == \'prompt\'));\n
\t\t\t\t\t\tbtn_holder.empty();\n
\n
\t\t\t\t\t\tok = $(\'<input type="button" value="\' + uiStrings.common.ok + \'">\').appendTo(btn_holder);\n
\n
\t\t\t\t\t\tif (type !== \'alert\') {\n
\t\t\t\t\t\t\t$(\'<input type="button" value="\' + uiStrings.common.cancel + \'">\')\n
\t\t\t\t\t\t\t\t.appendTo(btn_holder)\n
\t\t\t\t\t\t\t\t.click(function() { box.hide(); callback(false);});\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tif (type === \'prompt\') {\n
\t\t\t\t\t\t\tctrl = $(\'<input type="text">\').prependTo(btn_holder);\n
\t\t\t\t\t\t\tctrl.val(defaultVal || \'\');\n
\t\t\t\t\t\t\tctrl.bind(\'keydown\', \'return\', function() {ok.click();});\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\telse if (type === \'select\') {\n
\t\t\t\t\t\t\tvar div = $(\'<div style="text-align:center;">\');\n
\t\t\t\t\t\t\tctrl = $(\'<select>\').appendTo(div);\n
\t\t\t\t\t\t\tif (checkbox) {\n
\t\t\t\t\t\t\t\tvar label = $(\'<label>\').text(checkbox.label);\n
\t\t\t\t\t\t\t\tchkbx = $(\'<input type="checkbox">\').appendTo(label);\n
\t\t\t\t\t\t\t\tchkbx.val(checkbox.value);\n
\t\t\t\t\t\t\t\tif (checkbox.tooltip) {\n
\t\t\t\t\t\t\t\t\tlabel.attr(\'title\', checkbox.tooltip);\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\tchkbx.prop(\'checked\', !!checkbox.checked);\n
\t\t\t\t\t\t\t\tdiv.append($(\'<div>\').append(label));\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t$.each(opts || [], function (opt, val) {\n
\t\t\t\t\t\t\t\tif (typeof val === \'object\') {\n
\t\t\t\t\t\t\t\t\tctrl.append($(\'<option>\').val(val.value).html(val.text));\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\telse {\n
\t\t\t\t\t\t\t\t\tctrl.append($(\'<option>\').html(val));\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t});\n
\t\t\t\t\t\t\tdialog_content.append(div);\n
\t\t\t\t\t\t\tif (defaultVal) {\n
\t\t\t\t\t\t\t\tctrl.val(defaultVal);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\tif (changeCb) {\n
\t\t\t\t\t\t\t\tctrl.bind(\'change\', \'return\', changeCb);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\tctrl.bind(\'keydown\', \'return\', function() {ok.click();});\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tif (type === \'process\') {\n
\t\t\t\t\t\t\tok.hide();\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tbox.show();\n
\n
\t\t\t\t\t\tok.click(function() {\n
\t\t\t\t\t\t\tbox.hide();\n
\t\t\t\t\t\t\tvar resp = (type === \'prompt\' || type === \'select\') ? ctrl.val() : true;\n
\t\t\t\t\t\t\tif (callback) {\n
\t\t\t\t\t\t\t\tif (chkbx) {\n
\t\t\t\t\t\t\t\t\tcallback(resp, chkbx.prop(\'checked\'));\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\telse {\n
\t\t\t\t\t\t\t\t\tcallback(resp);\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}).focus();\n
\n
\t\t\t\t\t\tif (type === \'prompt\' || type === \'select\') {\n
\t\t\t\t\t\t\tctrl.focus();\n
\t\t\t\t\t\t}\n
\t\t\t\t\t};\n
\n
\t\t\t\t$.alert = function(msg, cb) { dbox(\'alert\', msg, cb);};\n
\t\t\t\t$.confirm = function(msg, cb) {\tdbox(\'confirm\', msg, cb);};\n
\t\t\t\t$.process_cancel = function(msg, cb) { dbox(\'process\', msg, cb);};\n
\t\t\t\t$.prompt = function(msg, txt, cb) { dbox(\'prompt\', msg, cb, txt);};\n
\t\t\t\t$.select = function(msg, opts, cb, changeCb, txt, checkbox) { dbox(\'select\', msg, cb, txt, opts, changeCb, checkbox);};\n
\t\t\t}());\n
\n
\t\t\tvar setSelectMode = function() {\n
\t\t\t\tvar curr = $(\'.tool_button_current\');\n
\t\t\t\tif (curr.length && curr[0].id !== \'tool_select\') {\n
\t\t\t\t\tcurr.removeClass(\'tool_button_current\').addClass(\'tool_button\');\n
\t\t\t\t\t$(\'#tool_select\').addClass(\'tool_button_current\').removeClass(\'tool_button\');\n
\t\t\t\t\t$(\'#styleoverrides\').text(\'#svgcanvas svg *{cursor:move;pointer-events:all} #svgcanvas svg{cursor:default}\');\n
\t\t\t\t}\n
\t\t\t\tsvgCanvas.setMode(\'select\');\n
\t\t\t\tworkarea.css(\'cursor\', \'auto\');\n
\t\t\t};\n
\n
\t\t\t// used to make the flyouts stay on the screen longer the very first time\n
\t\t\t// var flyoutspeed = 1250; // Currently unused\n
\t\t\tvar textBeingEntered = false;\n
\t\t\tvar selectedElement = null;\n
\t\t\tvar multiselected = false;\n
\t\t\tvar editingsource = false;\n
\t\t\tvar docprops = false;\n
\t\t\tvar preferences = false;\n
\t\t\tvar cur_context = \'\';\n
\t\t\tvar origTitle = $(\'title:first\').text();\n
\t\t\t// Make [1,2,5] array\n
\t\t\tvar r_intervals = [];\n
\t\t\tvar i;\n
\t\t\tfor (i = 0.1; i < 1E5; i *= 10) {\n
\t\t\t\tr_intervals.push(i);\n
\t\t\t\tr_intervals.push(2 * i);\n
\t\t\t\tr_intervals.push(5 * i);\n
\t\t\t}\n
\n
\t\t\t// This function highlights the layer passed in (by fading out the other layers)\n
\t\t\t// if no layer is passed in, this function restores the other layers\n
\t\t\tvar toggleHighlightLayer = function(layerNameToHighlight) {\n
\t\t\t\tvar i, curNames = [], numLayers = svgCanvas.getCurrentDrawing().getNumLayers();\n
\t\t\t\tfor (i = 0; i < numLayers; i++) {\n
\t\t\t\t\tcurNames[i] = svgCanvas.getCurrentDrawing().getLayerName(i);\n
\t\t\t\t}\n
\n
\t\t\t\tif (layerNameToHighlight) {\n
\t\t\t\t\tfor (i = 0; i < numLayers; ++i) {\n
\t\t\t\t\t\tif (curNames[i] != layerNameToHighlight) {\n
\t\t\t\t\t\t\tsvgCanvas.getCurrentDrawing().setLayerOpacity(curNames[i], 0.5);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t} else {\n
\t\t\t\t\tfor (i = 0; i < numLayers; ++i) {\n
\t\t\t\t\t\tsvgCanvas.getCurrentDrawing().setLayerOpacity(curNames[i], 1.0);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar populateLayers = function() {\n
\t\t\t\tsvgCanvas.clearSelection();\n
\t\t\t\tvar layerlist = $(\'#layerlist tbody\').empty();\n
\t\t\t\tvar selLayerNames = $(\'#selLayerNames\').empty();\n
\t\t\t\tvar drawing = svgCanvas.getCurrentDrawing();\n
\t\t\t\tvar currentLayerName = drawing.getCurrentLayerName();\n
\t\t\t\tvar layer = svgCanvas.getCurrentDrawing().getNumLayers();\n
\t\t\t\tvar icon = $.getSvgIcon(\'eye\');\n
\t\t\t\t// we get the layers in the reverse z-order (the layer rendered on top is listed first)\n
\t\t\t\twhile (layer--) {\n
\t\t\t\t\tvar name = drawing.getLayerName(layer);\n
\t\t\t\t\tvar layerTr = $(\'<tr class="layer">\').toggleClass(\'layersel\', name === currentLayerName);\n
\t\t\t\t\tvar layerVis = $(\'<td class="layervis">\').toggleClass(\'layerinvis\', !drawing.getLayerVisibility(name));\n
\t\t\t\t\tvar layerName = $(\'<td class="layername">\' + name + \'</td>\');\n
\t\t\t\t\tlayerlist.append(layerTr.append(layerVis, layerName));\n
\t\t\t\t\tselLayerNames.append(\'<option value="\' + name + \'">\' + name + \'</option>\');\n
\t\t\t\t}\n
\t\t\t\tif (icon !== undefined) {\n
\t\t\t\t\tvar copy = icon.clone();\n
\t\t\t\t\t$(\'td.layervis\', layerlist).append(copy);\n
\t\t\t\t\t$.resizeSvgIcons({\'td.layervis .svg_icon\': 14});\n
\t\t\t\t}\n
\t\t\t\t// handle selection of layer\n
\t\t\t\t$(\'#layerlist td.layername\')\n
\t\t\t\t\t.mouseup(function(evt) {\n
\t\t\t\t\t\t$(\'#layerlist tr.layer\').removeClass(\'layersel\');\n
\t\t\t\t\t\t$(this.parentNode).addClass(\'layersel\');\n
\t\t\t\t\t\tsvgCanvas.setCurrentLayer(this.textContent);\n
\t\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t\t})\n
\t\t\t\t\t.mouseover(function() {\n
\t\t\t\t\t\ttoggleHighlightLayer(this.textContent);\n
\t\t\t\t\t})\n
\t\t\t\t\t.mouseout(function() {\n
\t\t\t\t\t\ttoggleHighlightLayer();\n
\t\t\t\t\t});\n
\t\t\t\t$(\'#layerlist td.layervis\').click(function() {\n
\t\t\t\t\tvar row = $(this.parentNode).prevAll().length;\n
\t\t\t\t\tvar name = $(\'#layerlist tr.layer:eq(\' + row + \') td.layername\').text();\n
\t\t\t\t\tvar vis = $(this).hasClass(\'layerinvis\');\n
\t\t\t\t\tsvgCanvas.setLayerVisibility(name, vis);\n
\t\t\t\t\t$(this).toggleClass(\'layerinvis\');\n
\t\t\t\t});\n
\n
\t\t\t\t// if there were too few rows, let\'s add a few to make it not so lonely\n
\t\t\t\tvar num = 5 - $(\'#layerlist tr.layer\').size();\n
\t\t\t\twhile (num-- > 0) {\n
\t\t\t\t\t// FIXME: there must a better way to do this\n
\t\t\t\t\tlayerlist.append(\'<tr><td style="color:white">_</td><td/></tr>\');\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar showSourceEditor = function(e, forSaving) {\n
\t\t\t\tif (editingsource) {return;}\n
\n
\t\t\t\teditingsource = true;\n
\t\t\t\torigSource = svgCanvas.getSvgString();\n
\t\t\t\t$(\'#save_output_btns\').toggle(!!forSaving);\n
\t\t\t\t$(\'#tool_source_back\').toggle(!forSaving);\n
\t\t\t\t$(\'#svg_source_textarea\').val(origSource);\n
\t\t\t\t$(\'#svg_source_editor\').fadeIn();\n
\t\t\t\t$(\'#svg_source_textarea\').focus();\n
\t\t\t};\n
\n
\t\t\tvar togglePathEditMode = function(editmode, elems) {\n
\t\t\t\t$(\'#path_node_panel\').toggle(editmode);\n
\t\t\t\t$(\'#tools_bottom_2,#tools_bottom_3\').toggle(!editmode);\n
\t\t\t\tif (editmode) {\n
\t\t\t\t\t// Change select icon\n
\t\t\t\t\t$(\'.tool_button_current\').removeClass(\'tool_button_current\').addClass(\'tool_button\');\n
\t\t\t\t\t$(\'#tool_select\').addClass(\'tool_button_current\').removeClass(\'tool_button\');\n
\t\t\t\t\tsetIcon(\'#tool_select\', \'select_node\');\n
\t\t\t\t\tmultiselected = false;\n
\t\t\t\t\tif (elems.length) {\n
\t\t\t\t\t\tselectedElement = elems[0];\n
\t\t\t\t\t}\n
\t\t\t\t} else {\n
\t\t\t\t\tsetTimeout(function () {\n
\t\t\t\t\t\tsetIcon(\'#tool_select\', \'select\');\n
\t\t\t\t\t}, 1000);\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar saveHandler = function(wind, svg) {\n
\t\t\t\teditor.showSaveWarning = false;\n
\n
\t\t\t\t// by default, we add the XML prolog back, systems integrating SVG-edit (wikis, CMSs)\n
\t\t\t\t// can just provide their own custom save handler and might not want the XML prolog\n
\t\t\t\tsvg = \'<?xml version="1.0"?>\\n\' + svg;\n
\n
\t\t\t\t// IE9 doesn\'t allow standalone Data URLs\n
\t\t\t\t// https://connect.microsoft.com/IE/feedback/details/542600/data-uri-images-fail-when-loaded-by-themselves\n
\t\t\t\tif (svgedit.browser.isIE()) {\n
\t\t\t\t\tshowSourceEditor(0, true);\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\n
\t\t\t\t// Opens the SVG in new window\n
\t\t\t\tvar win = wind.open(\'data:image/svg+xml;base64,\' + Utils.encode64(svg));\n
\n
\t\t\t\t// Alert will only appear the first time saved OR the first time the bug is encountered\n
\t\t\t\tvar done = $.pref(\'save_notice_done\');\n
\t\t\t\tif (done !== \'all\') {\n
\t\t\t\t\tvar note = uiStrings.notification.saveFromBrowser.replace(\'%s\', \'SVG\');\n
\n
\t\t\t\t\t// Check if FF and has <defs/>\n
\t\t\t\t\tif (svgedit.browser.isGecko()) {\n
\t\t\t\t\t\tif (svg.indexOf(\'<defs\') !== -1) {\n
\t\t\t\t\t\t\t// warning about Mozilla bug #308590 when applicable (seems to be fixed now in Feb 2013)\n
\t\t\t\t\t\t\tnote += \'\\n\\n\' + uiStrings.notification.defsFailOnSave;\n
\t\t\t\t\t\t\t$.pref(\'save_notice_done\', \'all\');\n
\t\t\t\t\t\t\tdone = \'all\';\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t$.pref(\'save_notice_done\', \'part\');\n
\t\t\t\t\t\t}\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\t$.pref(\'save_notice_done\', \'all\');\n
\t\t\t\t\t}\n
\t\t\t\t\tif (done !== \'part\') {\n
\t\t\t\t\t\twin.alert(note);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar exportHandler = function(win, data) {\n
\t\t\t\tvar issues = data.issues,\n
\t\t\t\t\ttype = data.type || \'PNG\',\n
\t\t\t\t\tdataURLType = (type === \'ICO\' ? \'BMP\' : type).toLowerCase();\n
\n
\t\t\t\tif (!$(\'#export_canvas\').length) {\n
\t\t\t\t\t$(\'<canvas>\', {id: \'export_canvas\'}).hide().appendTo(\'body\');\n
\t\t\t\t}\n
\t\t\t\tvar c = $(\'#export_canvas\')[0];\n
\n
\t\t\t\tc.width = svgCanvas.contentW;\n
\t\t\t\tc.height = svgCanvas.contentH;\n
\t\t\t\tcanvg(c, data.svg, {renderCallback: function() {\n
\t\t\t\t\tvar datauri = data.quality ? c.toDataURL(\'image/\' + dataURLType, data.quality) : c.toDataURL(\'image/\' + dataURLType);\n
\t\t\t\t\texportWindow.location.href = datauri;\n
\t\t\t\t\tvar done = $.pref(\'export_notice_done\');\n
\t\t\t\t\tif (done !== \'all\') {\n
\t\t\t\t\t\tvar note = uiStrings.notification.saveFromBrowser.replace(\'%s\', type);\n
\n
\t\t\t\t\t\t// Check if there\'s issues\n
\t\t\t\t\t\tif (issues.length) {\n
\t\t\t\t\t\t\tvar pre = \'\\n \\u2022 \';\n
\t\t\t\t\t\t\tnote += (\'\\n\\n\' + uiStrings.notification.noteTheseIssues + pre + issues.join(pre));\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t// Note that this will also prevent the notice even though new issues may appear later.\n
\t\t\t\t\t\t// May want to find a way to deal with that without annoying the user\n
\t\t\t\t\t\t$.pref(\'export_notice_done\', \'all\');\n
\t\t\t\t\t\texportWindow.alert(note);\n
\t\t\t\t\t}\n
\t\t\t\t}});\n
\t\t\t};\n
\n
\t\t\tvar operaRepaint = function() {\n
\t\t\t\t// Repaints canvas in Opera. Needed for stroke-dasharray change as well as fill change\n
\t\t\t\tif (!window.opera) {\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\t\t\t\t$(\'<p/>\').hide().appendTo(\'body\').remove();\n
\t\t\t};\n
\n
\t\t\tfunction setStrokeOpt(opt, changeElem) {\n
\t\t\t\tvar id = opt.id;\n
\t\t\t\tvar bits = id.split(\'_\');\n
\t\t\t\tvar pre = bits[0];\n
\t\t\t\tvar val = bits[1];\n
\n
\t\t\t\tif (changeElem) {\n
\t\t\t\t\tsvgCanvas.setStrokeAttr(\'stroke-\' + pre, val);\n
\t\t\t\t}\n
\t\t\t\toperaRepaint();\n
\t\t\t\tsetIcon(\'#cur_\' + pre, id, 20);\n
\t\t\t\t$(opt).addClass(\'current\').siblings().removeClass(\'current\');\n
\t\t\t}\n
\n
\t\t\t// This is a common function used when a tool has been clicked (chosen)\n
\t\t\t// It does several common things:\n
\t\t\t// - removes the tool_button_current class from whatever tool currently has it\n
\t\t\t// - hides any flyouts\n
\t\t\t// - adds the tool_button_current class to the button passed in\n
\t\t\tvar toolButtonClick = editor.toolButtonClick = function(button, noHiding) {\n
\t\t\t\tif ($(button).hasClass(\'disabled\')) {return false;}\n
\t\t\t\tif ($(button).parent().hasClass(\'tools_flyout\')) {return true;}\n
\t\t\t\tvar fadeFlyouts = \'normal\';\n
\t\t\t\tif (!noHiding) {\n
\t\t\t\t\t$(\'.tools_flyout\').fadeOut(fadeFlyouts);\n
\t\t\t\t}\n
\t\t\t\t$(\'#styleoverrides\').text(\'\');\n
\t\t\t\tworkarea.css(\'cursor\', \'auto\');\n
\t\t\t\t$(\'.tool_button_current\').removeClass(\'tool_button_current\').addClass(\'tool_button\');\n
\t\t\t\t$(button).addClass(\'tool_button_current\').removeClass(\'tool_button\');\n
\t\t\t\treturn true;\n
\t\t\t};\n
\n
\t\t\tvar clickSelect = editor.clickSelect = function() {\n
\t\t\t\tif (toolButtonClick(\'#tool_select\')) {\n
\t\t\t\t\tsvgCanvas.setMode(\'select\');\n
\t\t\t\t\t$(\'#styleoverrides\').text(\'#svgcanvas svg *{cursor:move;pointer-events:all}, #svgcanvas svg{cursor:default}\');\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar setImageURL = editor.setImageURL = function(url) {\n
\t\t\t\tif (!url) {\n
\t\t\t\t\turl = defaultImageURL;\n
\t\t\t\t}\n
\t\t\t\tsvgCanvas.setImageURL(url);\n
\t\t\t\t$(\'#image_url\').val(url);\n
\n
\t\t\t\tif (url.indexOf(\'data:\') === 0) {\n
\t\t\t\t\t// data URI found\n
\t\t\t\t\t$(\'#image_url\').hide();\n
\t\t\t\t\t$(\'#change_image_url\').show();\n
\t\t\t\t} else {\n
\t\t\t\t\t// regular URL\n
\t\t\t\t\tsvgCanvas.embedImage(url, function(dataURI) {\n
\t\t\t\t\t\t// Couldn\'t embed, so show warning\n
\t\t\t\t\t\t$(\'#url_notice\').toggle(!dataURI);\n
\t\t\t\t\t\tdefaultImageURL = url;\n
\t\t\t\t\t});\n
\t\t\t\t\t$(\'#image_url\').show();\n
\t\t\t\t\t$(\'#change_image_url\').hide();\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tfunction setBackground (color, url) {\n
\t\t\t\t// if (color == $.pref(\'bkgd_color\') && url == $.pref(\'bkgd_url\')) {return;}\n
\t\t\t\t$.pref(\'bkgd_color\', color);\n
\t\t\t\t$.pref(\'bkgd_url\', url);\n
\n
\t\t\t\t// This should be done in svgcanvas.js for the borderRect fill\n
\t\t\t\tsvgCanvas.setBackground(color, url);\n
\t\t\t}\n
\n
\t\t\tfunction promptImgURL() {\n
\t\t\t\tvar curhref = svgCanvas.getHref(selectedElement);\n
\t\t\t\tcurhref = curhref.indexOf(\'data:\') === 0 ? \'\' : curhref;\n
\t\t\t\t$.prompt(uiStrings.notification.enterNewImgURL, curhref, function(url) {\n
\t\t\t\t\tif (url) {setImageURL(url);}\n
\t\t\t\t});\n
\t\t\t}\n
\n
\t\t\tvar setInputWidth = function(elem) {\n
\t\t\t\tvar w = Math.min(Math.max(12 + elem.value.length * 6, 50), 300);\n
\t\t\t\t$(elem).width(w);\n
\t\t\t};\n
\n
\t\t\tfunction updateRulers(scanvas, zoom) {\n
\t\t\t\tif (!zoom) {zoom = svgCanvas.getZoom();}\n
\t\t\t\tif (!scanvas) {scanvas = $(\'#svgcanvas\');}\n
\n
\t\t\t\tvar d, i;\n
\t\t\t\tvar limit = 30000;\n
\t\t\t\tvar contentElem = svgCanvas.getContentElem();\n
\t\t\t\tvar units = svgedit.units.getTypeMap();\n
\t\t\t\tvar unit = units[curConfig.baseUnit]; // 1 = 1px\n
\n
\t\t\t\t// draw x ruler then y ruler\n
\t\t\t\tfor (d = 0; d < 2; d++) {\n
\t\t\t\t\tvar isX = (d === 0);\n
\t\t\t\t\tvar dim = isX ? \'x\' : \'y\';\n
\t\t\t\t\tvar lentype = isX ? \'width\' : \'height\';\n
\t\t\t\t\tvar contentDim = Number(contentElem.getAttribute(dim));\n
\n
\t\t\t\t\tvar $hcanv_orig = $(\'#ruler_\' + dim + \' canvas:first\');\n
\n
\t\t\t\t\t// Bit of a hack to fully clear the canvas in Safari & IE9\n
\t\t\t\t\tvar $hcanv = $hcanv_orig.clone();\n
\t\t\t\t\t$hcanv_orig.replaceWith($hcanv);\n
\n
\t\t\t\t\tvar hcanv = $hcanv[0];\n
\n
\t\t\t\t\t// Set the canvas size to the width of the container\n
\t\t\t\t\tvar ruler_len = scanvas[lentype]();\n
\t\t\t\t\tvar total_len = ruler_len;\n
\t\t\t\t\thcanv.parentNode.style[lentype] = total_len + \'px\';\n
\t\t\t\t\tvar ctx_num = 0;\n
\t\t\t\t\tvar ctx = hcanv.getContext(\'2d\');\n
\t\t\t\t\tvar ctx_arr, num, ctx_arr_num;\n
\n
\t\t\t\t\tctx.fillStyle = \'rgb(200,0,0)\';\n
\t\t\t\t\tctx.fillRect(0, 0, hcanv.width, hcanv.height);\n
\n
\t\t\t\t\t// Remove any existing canvasses\n
\t\t\t\t\t$hcanv.siblings().remove();\n
\t\t\t\t\t\n
\t\t\t\t\t// Create multiple canvases when necessary (due to browser limits)\n
\t\t\t\t\tif (ruler_len >= limit) {\n
\t\t\t\t\t\tctx_arr_num = parseInt(ruler_len / limit, 10) + 1;\n
\t\t\t\t\t\tctx_arr = [];\n
\t\t\t\t\t\tctx_arr[0] = ctx;\n
\t\t\t\t\t\tvar copy;\n
\t\t\t\t\t\tfor (i = 1; i < ctx_arr_num; i++) {\n
\t\t\t\t\t\t\thcanv[lentype] = limit;\n
\t\t\t\t\t\t\tcopy = hcanv.cloneNode(true);\n
\t\t\t\t\t\t\thcanv.parentNode.appendChild(copy);\n
\t\t\t\t\t\t\tctx_arr[i] = copy.getContext(\'2d\');\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tcopy[lentype] = ruler_len % limit;\n
\n
\t\t\t\t\t\t// set copy width to last\n
\t\t\t\t\t\truler_len = limit;\n
\t\t\t\t\t}\n
\n
\t\t\t\t\thcanv[lentype] = ruler_len;\n
\n
\t\t\t\t\tvar u_multi = unit * zoom;\n
\n
\t\t\t\t\t// Calculate the main number interval\n
\t\t\t\t\tvar raw_m = 50 / u_multi;\n
\t\t\t\t\tvar multi = 1;\n
\t\t\t\t\tfor (i = 0; i < r_intervals.length; i++) {\n
\t\t\t\t\t\tnum = r_intervals[i];\n
\t\t\t\t\t\tmulti = num;\n
\t\t\t\t\t\tif (raw_m <= num) {\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tvar big_int = multi * u_multi;\n
\n
\t\t\t\t\tctx.font = \'9px sans-serif\';\n
\n
\t\t\t\t\tvar ruler_d = ((contentDim / u_multi) % multi) * u_multi;\n
\t\t\t\t\tvar label_pos = ruler_d - big_int;\n
\t\t\t\t\t// draw big intervals\n
\t\t\t\t\twhile (ruler_d < total_len) {\n
\t\t\t\t\t\tlabel_pos += big_int;\n
\t\t\t\t\t\t// var real_d = ruler_d - contentDim; // Currently unused\n
\n
\t\t\t\t\t\tvar cur_d = Math.round(ruler_d) + 0.5;\n
\t\t\t\t\t\tif (isX) {\n
\t\t\t\t\t\t\tctx.moveTo(cur_d, 15);\n
\t\t\t\t\t\t\tctx.lineTo(cur_d, 0);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\telse {\n
\t\t\t\t\t\t\tctx.moveTo(15, cur_d);\n
\t\t\t\t\t\t\tctx.lineTo(0, cur_d);\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tnum = (label_pos - contentDim) / u_multi;\n
\t\t\t\t\t\tvar label;\n
\t\t\t\t\t\tif (multi >= 1) {\n
\t\t\t\t\t\t\tlabel = Math.round(num);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\telse {\n
\t\t\t\t\t\t\tvar decs = String(multi).split(\'.\')[1].length;\n
\t\t\t\t\t\t\tlabel = num.toFixed(decs);\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t// Change 1000s to Ks\n
\t\t\t\t\t\tif (label !== 0 && label !== 1000 && label % 1000 === 0) {\n
\t\t\t\t\t\t\tlabel = (label / 1000) + \'K\';\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tif (isX) {\n
\t\t\t\t\t\t\tctx.fillText(label, ruler_d+2, 8);\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t// draw label vertically\n
\t\t\t\t\t\t\tvar str = String(label).split(\'\');\n
\t\t\t\t\t\t\tfor (i = 0; i < str.length; i++) {\n
\t\t\t\t\t\t\t\tctx.fillText(str[i], 1, (ruler_d+9) + i*9);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tvar part = big_int / 10;\n
\t\t\t\t\t\t// draw the small intervals\n
\t\t\t\t\t\tfor (i = 1; i < 10; i++) {\n
\t\t\t\t\t\t\tvar sub_d = Math.round(ruler_d + part * i) + 0.5;\n
\t\t\t\t\t\t\tif (ctx_arr && sub_d > ruler_len) {\n
\t\t\t\t\t\t\t\tctx_num++;\n
\t\t\t\t\t\t\t\tctx.stroke();\n
\t\t\t\t\t\t\t\tif (ctx_num >= ctx_arr_num) {\n
\t\t\t\t\t\t\t\t\ti = 10;\n
\t\t\t\t\t\t\t\t\truler_d = total_len;\n
\t\t\t\t\t\t\t\t\tcontinue;\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\tctx = ctx_arr[ctx_num];\n
\t\t\t\t\t\t\t\truler_d -= limit;\n
\t\t\t\t\t\t\t\tsub_d = Math.round(ruler_d + part * i) + 0.5;\n
\t\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t\t// odd lines are slighly longer\n
\t\t\t\t\t\t\tvar line_num = (i % 2) ? 12 : 10;\n
\t\t\t\t\t\t\tif (isX) {\n
\t\t\t\t\t\t\t\tctx.moveTo(sub_d, 15);\n
\t\t\t\t\t\t\t\tctx.lineTo(sub_d, line_num);\n
\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\tctx.moveTo(15, sub_d);\n
\t\t\t\t\t\t\t\tctx.lineTo(line_num, sub_d);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\truler_d += big_int;\n
\t\t\t\t\t}\n
\t\t\t\t\tctx.strokeStyle = \'#000\';\n
\t\t\t\t\tctx.stroke();\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\tvar updateCanvas = editor.updateCanvas = function(center, new_ctr) {\n
\t\t\t\tvar w = workarea.width(), h = workarea.height();\n
\t\t\t\tvar w_orig = w, h_orig = h;\n
\t\t\t\tvar zoom = svgCanvas.getZoom();\n
\t\t\t\tvar w_area = workarea;\n
\t\t\t\tvar cnvs = $(\'#svgcanvas\');\n
\t\t\t\tvar old_ctr = {\n
\t\t\t\t\tx: w_area[0].scrollLeft + w_orig/2,\n
\t\t\t\t\ty: w_area[0].scrollTop + h_orig/2\n
\t\t\t\t};\n
\t\t\t\tvar multi = curConfig.canvas_expansion;\n
\t\t\t\tw = Math.max(w_orig, svgCanvas.contentW * zoom * multi);\n
\t\t\t\th = Math.max(h_orig, svgCanvas.contentH * zoom * multi);\n
\n
\t\t\t\tif (w == w_orig && h == h_orig) {\n
\t\t\t\t\tworkarea.css(\'overflow\', \'hidden\');\n
\t\t\t\t} else {\n
\t\t\t\t\tworkarea.css(\'overflow\', \'scroll\');\n
\t\t\t\t}\n
\n
\t\t\t\tvar old_can_y = cnvs.height()/2;\n
\t\t\t\tvar old_can_x = cnvs.width()/2;\n
\t\t\t\tcnvs.width(w).height(h);\n
\t\t\t\tvar new_can_y = h/2;\n
\t\t\t\tvar new_can_x = w/2;\n
\t\t\t\tvar offset = svgCanvas.updateCanvas(w, h);\n
\n
\t\t\t\tvar ratio = new_can_x / old_can_x;\n
\n
\t\t\t\tvar scroll_x = w/2 - w_orig/2;\n
\t\t\t\tvar scroll_y = h/2 - h_orig/2;\n
\n
\t\t\t\tif (!new_ctr) {\n
\t\t\t\t\tvar old_dist_x = old_ctr.x - old_can_x;\n
\t\t\t\t\tvar new_x = new_can_x + old_dist_x * ratio;\n
\n
\t\t\t\t\tvar old_dist_y = old_ctr.y - old_can_y;\n
\t\t\t\t\tvar new_y = new_can_y + old_dist_y * ratio;\n
\n
\t\t\t\t\tnew_ctr = {\n
\t\t\t\t\t\tx: new_x,\n
\t\t\t\t\t\ty: new_y\n
\t\t\t\t\t};\n
\t\t\t\t} else {\n
\t\t\t\t\tnew_ctr.x += offset.x;\n
\t\t\t\t\tnew_ctr.y += offset.y;\n
\t\t\t\t}\n
\n
\t\t\t\tif (center) {\n
\t\t\t\t\t// Go to top-left for larger documents\n
\t\t\t\t\tif (svgCanvas.contentW > w_area.width()) {\n
\t\t\t\t\t\t// Top-left\n
\t\t\t\t\t\tworkarea[0].scrollLeft = offset.x - 10;\n
\t\t\t\t\t\tworkarea[0].scrollTop = offset.y - 10;\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\t// Center\n
\t\t\t\t\t\tw_area[0].scrollLeft = scroll_x;\n
\t\t\t\t\t\tw_area[0].scrollTop = scroll_y;\n
\t\t\t\t\t}\n
\t\t\t\t} else {\n
\t\t\t\t\tw_area[0].scrollLeft = new_ctr.x - w_orig/2;\n
\t\t\t\t\tw_area[0].scrollTop = new_ctr.y - h_orig/2;\n
\t\t\t\t}\n
\t\t\t\tif (curConfig.showRulers) {\n
\t\t\t\t\tupdateRulers(cnvs, zoom);\n
\t\t\t\t\tworkarea.scroll();\n
\t\t\t\t}\n
\t\t\t\tif (urldata.storagePrompt !== true && !editor.storagePromptClosed) {\n
\t\t\t\t\t$(\'#dialog_box\').hide();\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar updateToolButtonState = function() {\n
\t\t\t\tvar index, button;\n
\t\t\t\tvar bNoFill = (svgCanvas.getColor(\'fill\') == \'none\');\n
\t\t\t\tvar bNoStroke = (svgCanvas.getColor(\'stroke\') == \'none\');\n
\t\t\t\tvar buttonsNeedingStroke = [ \'#tool_fhpath\', \'#tool_line\' ];\n
\t\t\t\tvar buttonsNeedingFillAndStroke = [ \'#tools_rect .tool_button\', \'#tools_ellipse .tool_button\', \'#tool_text\', \'#tool_path\'];\n
\t\t\t\tif (bNoStroke) {\n
\t\t\t\t\tfor (index in buttonsNeedingStroke) {\n
\t\t\t\t\t\tbutton = buttonsNeedingStroke[index];\n
\t\t\t\t\t\tif ($(button).hasClass(\'tool_button_current\')) {\n
\t\t\t\t\t\t\tclickSelect();\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t$(button).addClass(\'disabled\');\n
\t\t\t\t\t}\n
\t\t\t\t} else {\n
\t\t\t\t\tfor (index in buttonsNeedingStroke) {\n
\t\t\t\t\t\tbutton = buttonsNeedingStroke[index];\n
\t\t\t\t\t\t$(button).removeClass(\'disabled\');\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\tif (bNoStroke && bNoFill) {\n
\t\t\t\t\tfor (index in buttonsNeedingFillAndStroke) {\n
\t\t\t\t\t\tbutton = buttonsNeedingFillAndStroke[index];\n
\t\t\t\t\t\tif ($(button).hasClass(\'tool_button_current\')) {\n
\t\t\t\t\t\t\tclickSelect();\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t$(button).addClass(\'disabled\');\n
\t\t\t\t\t}\n
\t\t\t\t} else {\n
\t\t\t\t\tfor (index in buttonsNeedingFillAndStroke) {\n
\t\t\t\t\t\tbutton = buttonsNeedingFillAndStroke[index];\n
\t\t\t\t\t\t$(button).removeClass(\'disabled\');\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\tsvgCanvas.runExtensions(\'toolButtonStateUpdate\', {\n
\t\t\t\t\tnofill: bNoFill,\n
\t\t\t\t\tnostroke: bNoStroke\n
\t\t\t\t});\n
\n
\t\t\t\t// Disable flyouts if all inside are disabled\n
\t\t\t\t$(\'.tools_flyout\').each(function() {\n
\t\t\t\t\tvar shower = $(\'#\' + this.id + \'_show\');\n
\t\t\t\t\tvar has_enabled = false;\n
\t\t\t\t\t$(this).children().each(function() {\n
\t\t\t\t\t\tif (!$(this).hasClass(\'disabled\')) {\n
\t\t\t\t\t\t\thas_enabled = true;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t});\n
\t\t\t\t\tshower.toggleClass(\'disabled\', !has_enabled);\n
\t\t\t\t});\n
\n
\t\t\t\toperaRepaint();\n
\t\t\t};\n
\n
\t\t\t// Updates the toolbar (colors, opacity, etc) based on the selected element\n
\t\t\t// This function also updates the opacity and id elements that are in the context panel\n
\t\t\tvar updateToolbar = function() {\n
\t\t\t\tvar i, len;\n
\t\t\t\tif (selectedElement != null) {\n
\t\t\t\t\tswitch (selectedElement.tagName) {\n
\t\t\t\t\tcase \'use\':\n
\t\t\t\t\tcase \'image\':\n
\t\t\t\t\tcase \'foreignObject\':\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'g\':\n
\t\t\t\t\tcase \'a\':\n
\t\t\t\t\t\t// Look for common styles\n
\t\t\t\t\t\tvar gWidth = null;\n
\t\t\t\t\t\tvar childs = selectedElement.getElementsByTagName(\'*\');\n
\t\t\t\t\t\tfor (i = 0, len = childs.length; i < len; i++) {\n
\t\t\t\t\t\t\tvar swidth = childs[i].getAttribute(\'stroke-width\');\n
\n
\t\t\t\t\t\t\tif (i === 0) {\n
\t\t\t\t\t\t\t\tgWidth = swidth;\n
\t\t\t\t\t\t\t} else if (gWidth !== swidth) {\n
\t\t\t\t\t\t\t\tgWidth = null;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t$(\'#stroke_width\').val(gWidth === null ? \'\' : gWidth);\n
\n
\t\t\t\t\t\tpaintBox.fill.update(true);\n
\t\t\t\t\t\tpaintBox.stroke.update(true);\n
\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tdefault:\n
\t\t\t\t\t\tpaintBox.fill.update(true);\n
\t\t\t\t\t\tpaintBox.stroke.update(true);\n
\n
\t\t\t\t\t\t$(\'#stroke_width\').val(selectedElement.getAttribute(\'stroke-width\') || 1);\n
\t\t\t\t\t\t$(\'#stroke_style\').val(selectedElement.getAttribute(\'stroke-dasharray\') || \'none\');\n
\n
\t\t\t\t\t\tvar attr = selectedElement.getAttribute(\'stroke-linejoin\') || \'miter\';\n
\n
\t\t\t\t\t\tif ($(\'#linejoin_\' + attr).length != 0) {\n
\t\t\t\t\t\t\tsetStrokeOpt($(\'#linejoin_\' + attr)[0]);\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tattr = selectedElement.getAttribute(\'stroke-linecap\') || \'butt\';\n
\n
\t\t\t\t\t\tif ($(\'#linecap_\' + attr).length != 0) {\n
\t\t\t\t\t\t\tsetStrokeOpt($(\'#linecap_\' + attr)[0]);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\t// All elements including image and group have opacity\n
\t\t\t\tif (selectedElement != null) {\n
\t\t\t\t\tvar opac_perc = ((selectedElement.getAttribute(\'opacity\')||1.0)*100);\n
\t\t\t\t\t$(\'#group_opacity\').val(opac_perc);\n
\t\t\t\t\t$(\'#opac_slider\').slider(\'option\', \'value\', opac_perc);\n
\t\t\t\t\t$(\'#elem_id\').val(selectedElement.id);\n
\t\t\t\t}\n
\n
\t\t\t\tupdateToolButtonState();\n
\t\t\t};\n
\n
\t\t\t// updates the context panel tools based on the selected element\n
\t\t\tvar updateContextPanel = function() {\n
\t\t\t\tvar elem = selectedElement;\n
\t\t\t\t// If element has just been deleted, consider it null\n
\t\t\t\tif (elem != null && !elem.parentNode) {elem = null;}\n
\t\t\t\tvar currentLayerName = svgCanvas.getCurrentDrawing().getCurrentLayerName();\n
\t\t\t\tvar currentMode = svgCanvas.getMode();\n
\t\t\t\tvar unit = curConfig.baseUnit !== \'px\' ? curConfig.baseUnit : null;\n
\n
\t\t\t\tvar is_node = currentMode == \'pathedit\'; //elem ? (elem.id && elem.id.indexOf(\'pathpointgrip\') == 0) : false;\n
\t\t\t\tvar menu_items = $(\'#cmenu_canvas li\');\n
\t\t\t\t$(\'#selected_panel, #multiselected_panel, #g_panel, #rect_panel, #circle_panel,\'+\n
\t\t\t\t\t\'#ellipse_panel, #line_panel, #text_panel, #image_panel, #container_panel,\'+\n
\t\t\t\t\t\' #use_panel, #a_panel\').hide();\n
\t\t\t\tif (elem != null) {\n
\t\t\t\t\tvar elname = elem.nodeName;\n
\t\t\t\t\t// If this is a link with no transform and one child, pretend\n
\t\t\t\t\t// its child is selected\n
//\t\t\t\t\tif (elname === \'a\') { // && !$(elem).attr(\'transform\')) {\n
//\t\t\t\t\t\telem = elem.firstChild;\n
//\t\t\t\t\t}\n
\n
\t\t\t\t\tvar angle = svgCanvas.getRotationAngle(elem);\n
\t\t\t\t\t$(\'#angle\').val(angle);\n
\n
\t\t\t\t\tvar blurval = svgCanvas.getBlur(elem);\n
\t\t\t\t\t$(\'#blur\').val(blurval);\n
\t\t\t\t\t$(\'#blur_slider\').slider(\'option\', \'value\', blurval);\n
\n
\t\t\t\t\tif (svgCanvas.addedNew) {\n
\t\t\t\t\t\tif (elname === \'image\') {\n
\t\t\t\t\t\t\t// Prompt for URL if not a data URL\n
\t\t\t\t\t\t\tif (svgCanvas.getHref(elem).indexOf(\'data:\') !== 0) {\n
\t\t\t\t\t\t\t\tpromptImgURL();\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t} /*else if (elname == \'text\') {\n
\t\t\t\t\t\t\t// TODO: Do something here for new text\n
\t\t\t\t\t\t}*/\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tif (!is_node && currentMode != \'pathedit\') {\n
\t\t\t\t\t\t$(\'#selected_panel\').show();\n
\t\t\t\t\t\t// Elements in this array already have coord fields\n
\t\t\t\t\t\tif ([\'line\', \'circle\', \'ellipse\'].indexOf(elname) >= 0) {\n
\t\t\t\t\t\t\t$(\'#xy_panel\').hide();\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\tvar x, y;\n
\n
\t\t\t\t\t\t\t// Get BBox vals for g, polyline and path\n
\t\t\t\t\t\t\tif ([\'g\', \'polyline\', \'path\'].indexOf(elname) >= 0) {\n
\t\t\t\t\t\t\t\tvar bb = svgCanvas.getStrokedBBox([elem]);\n
\t\t\t\t\t\t\t\tif (bb) {\n
\t\t\t\t\t\t\t\t\tx = bb.x;\n
\t\t\t\t\t\t\t\t\ty = bb.y;\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\tx = elem.getAttribute(\'x\');\n
\t\t\t\t\t\t\t\ty = elem.getAttribute(\'y\');\n
\t\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t\tif (unit) {\n
\t\t\t\t\t\t\t\tx = svgedit.units.convertUnit(x);\n
\t\t\t\t\t\t\t\ty = svgedit.units.convertUnit(y);\n
\t\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t\t$(\'#selected_x\').val(x || 0);\n
\t\t\t\t\t\t\t$(\'#selected_y\').val(y || 0);\n
\t\t\t\t\t\t\t$(\'#xy_panel\').show();\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t// Elements in this array cannot be converted to a path\n
\t\t\t\t\t\tvar no_path = [\'image\', \'text\', \'path\', \'g\', \'use\'].indexOf(elname) == -1;\n
\t\t\t\t\t\t$(\'#tool_topath\').toggle(no_path);\n
\t\t\t\t\t\t$(\'#tool_reorient\').toggle(elname === \'path\');\n
\t\t\t\t\t\t$(\'#tool_reorient\').toggleClass(\'disabled\', angle === 0);\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tvar point = path.getNodePoint();\n
\t\t\t\t\t\t$(\'#tool_add_subpath\').removeClass(\'push_button_pressed\').addClass(\'tool_button\');\n
\t\t\t\t\t\t$(\'#tool_node_delete\').toggleClass(\'disabled\', !path.canDeleteNodes);\n
\n
\t\t\t\t\t\t// Show open/close button based on selected point\n
\t\t\t\t\t\tsetIcon(\'#tool_openclose_path\', path.closed_subpath ? \'open_path\' : \'close_path\');\n
\n
\t\t\t\t\t\tif (point) {\n
\t\t\t\t\t\t\tvar seg_type = $(\'#seg_type\');\n
\t\t\t\t\t\t\tif (unit) {\n
\t\t\t\t\t\t\t\tpoint.x = svgedit.units.convertUnit(point.x);\n
\t\t\t\t\t\t\t\tpoint.y = svgedit.units.convertUnit(point.y);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t$(\'#path_node_x\').val(point.x);\n
\t\t\t\t\t\t\t$(\'#path_node_y\').val(point.y);\n
\t\t\t\t\t\t\tif (point.type) {\n
\t\t\t\t\t\t\t\tseg_type.val(point.type).removeAttr(\'disabled\');\n
\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\tseg_type.val(4).attr(\'disabled\', \'disabled\');\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\treturn;\n
\t\t\t\t\t}\n
\n
\t\t\t\t\t// update contextual tools here\n
\t\t\t\t\tvar panels = {\n
\t\t\t\t\t\tg: [],\n
\t\t\t\t\t\ta: [],\n
\t\t\t\t\t\trect: [\'rx\', \'width\', \'height\'],\n
\t\t\t\t\t\timage: [\'width\', \'height\'],\n
\t\t\t\t\t\tcircle: [\'cx\', \'cy\', \'r\'],\n
\t\t\t\t\t\tellipse: [\'cx\', \'cy\', \'rx\', \'ry\'],\n
\t\t\t\t\t\tline: [\'x1\', \'y1\', \'x2\', \'y2\'],\n
\t\t\t\t\t\ttext: [],\n
\t\t\t\t\t\tuse: []\n
\t\t\t\t\t};\n
\n
\t\t\t\t\tvar el_name = elem.tagName;\n
\n
//\t\t\t\t\tif ($(elem).data(\'gsvg\')) {\n
//\t\t\t\t\t\t$(\'#g_panel\').show();\n
//\t\t\t\t\t}\n
\n
\t\t\t\t\tvar link_href = null;\n
\t\t\t\t\tif (el_name === \'a\') {\n
\t\t\t\t\t\tlink_href = svgCanvas.getHref(elem);\n
\t\t\t\t\t\t$(\'#g_panel\').show();\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tif (elem.parentNode.tagName === \'a\') {\n
\t\t\t\t\t\tif (!$(elem).siblings().length) {\n
\t\t\t\t\t\t\t$(\'#a_panel\').show();\n
\t\t\t\t\t\t\tlink_href = svgCanvas.getHref(elem.parentNode);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\n
\t\t\t\t\t// Hide/show the make_link buttons\n
\t\t\t\t\t$(\'#tool_make_link, #tool_make_link\').toggle(!link_href);\n
\n
\t\t\t\t\tif (link_href) {\n
\t\t\t\t\t\t$(\'#link_url\').val(link_href);\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tif (panels[el_name]) {\n
\t\t\t\t\t\tvar cur_panel = panels[el_name];\n
\n
\t\t\t\t\t\t$(\'#\' + el_name + \'_panel\').show();\n
\n
\t\t\t\t\t\t$.each(cur_panel, function(i, item) {\n
\t\t\t\t\t\t\tvar attrVal = elem.getAttribute(item);\n
\t\t\t\t\t\t\tif (curConfig.baseUnit !== \'px\' && elem[item]) {\n
\t\t\t\t\t\t\t\tvar bv = elem[item].baseVal.value;\n
\t\t\t\t\t\t\t\tattrVal = svgedit.units.convertUnit(bv);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t$(\'#\' + el_name + \'_\' + item).val(attrVal || 0);\n
\t\t\t\t\t\t});\n
\n
\t\t\t\t\t\tif (el_name == \'text\') {\n
\t\t\t\t\t\t\t$(\'#text_panel\').css(\'display\', \'inline\');\n
\t\t\t\t\t\t\tif (svgCanvas.getItalic()) {\n
\t\t\t\t\t\t\t\t$(\'#tool_italic\').addClass(\'push_button_pressed\').removeClass(\'tool_button\');\n
\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\t$(\'#tool_italic\').removeClass(\'push_button_pressed\').addClass(\'tool_button\');\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\tif (svgCanvas.getBold()) {\n
\t\t\t\t\t\t\t\t$(\'#tool_bold\').addClass(\'push_button_pressed\').removeClass(\'tool_button\');\n
\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\t$(\'#tool_bold\').removeClass(\'push_button_pressed\').addClass(\'tool_button\');\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t$(\'#font_family\').val(elem.getAttribute(\'font-family\'));\n
\t\t\t\t\t\t\t$(\'#font_size\').val(elem.getAttribute(\'font-size\'));\n
\t\t\t\t\t\t\t$(\'#text\').val(elem.textContent);\n
\t\t\t\t\t\t\tif (svgCanvas.addedNew) {\n
\t\t\t\t\t\t\t\t// Timeout needed for IE9\n
\t\t\t\t\t\t\t\tsetTimeout(function() {\n
\t\t\t\t\t\t\t\t\t$(\'#text\').focus().select();\n
\t\t\t\t\t\t\t\t}, 100);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t} // text\n
\t\t\t\t\t\telse if (el_name == \'image\') {\n
\t\t\t\t\t\t\tsetImageURL(svgCanvas.getHref(elem));\n
\t\t\t\t\t\t} // image\n
\t\t\t\t\t\telse if (el_name === \'g\' || el_name === \'use\') {\n
\t\t\t\t\t\t\t$(\'#container_panel\').show();\n
\t\t\t\t\t\t\tvar title = svgCanvas.getTitle();\n
\t\t\t\t\t\t\tvar label = $(\'#g_title\')[0];\n
\t\t\t\t\t\t\tlabel.value = title;\n
\t\t\t\t\t\t\tsetInputWidth(label);\n
\t\t\t\t\t\t\t$(\'#g_title\').prop(\'disabled\', el_name == \'use\');\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\tmenu_items[(el_name === \'g\' ? \'en\' : \'dis\') + \'ableContextMenuItems\'](\'#ungroup\');\n
\t\t\t\t\tmenu_items[((el_name === \'g\' || !multiselected) ? \'dis\' : \'en\') + \'ableContextMenuItems\'](\'#group\');\n
\t\t\t\t} // if (elem != null)\n
\t\t\t\telse if (multiselected) {\n
\t\t\t\t\t$(\'#multiselected_panel\').show();\n
\t\t\t\t\tmenu_items\n
\t\t\t\t\t\t.enableContextMenuItems(\'#group\')\n
\t\t\t\t\t\t.disableContextMenuItems(\'#ungroup\');\n
\t\t\t\t} else {\n
\t\t\t\t\tmenu_items.disableContextMenuItems(\'#delete,#cut,#copy,#group,#ungroup,#move_front,#move_up,#move_down,#move_back\');\n
\t\t\t\t}\n
\n
\t\t\t\t// update history buttons\n
\t\t\t\t$(\'#tool_undo\').toggleClass(\'disabled\', undoMgr.getUndoStackSize() === 0);\n
\t\t\t\t$(\'#tool_redo\').toggleClass(\'disabled\', undoMgr.getRedoStackSize() === 0);\n
\n
\t\t\t\tsvgCanvas.addedNew = false;\n
\n
\t\t\t\tif ( (elem && !is_node)\t|| multiselected) {\n
\t\t\t\t\t// update the selected elements\' layer\n
\t\t\t\t\t$(\'#selLayerNames\').removeAttr(\'disabled\').val(currentLayerName);\n
\n
\t\t\t\t\t// Enable regular menu options\n
\t\t\t\t\tcanv_menu.enableContextMenuItems(\'#delete,#cut,#copy,#move_front,#move_up,#move_down,#move_back\');\n
\t\t\t\t} else {\n
\t\t\t\t\t$(\'#selLayerNames\').attr(\'disabled\', \'disabled\');\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar updateWireFrame = function() {\n
\t\t\t\t// Test support\n
\t\t\t\tif (supportsNonSS) {return;}\n
\n
\t\t\t\tvar rule = \'#workarea.wireframe #svgcontent * { stroke-width: \' + 1/svgCanvas.getZoom() + \'px; }\';\n
\t\t\t\t$(\'#wireframe_rules\').text(workarea.hasClass(\'wireframe\') ? rule : \'\');\n
\t\t\t};\n
\n
\t\t\tvar updateTitle = function(title) {\n
\t\t\t\ttitle = title || svgCanvas.getDocumentTitle();\n
\t\t\t\tvar newTitle = origTitle + (title ? \': \' + title : \'\');\n
\n
\t\t\t\t// Remove title update with current context info, isn\'t really necessary\n
//\t\t\t\tif (cur_context) {\n
//\t\t\t\t\tnew_title = new_title + cur_context;\n
//\t\t\t\t}\n
\t\t\t\t$(\'title:first\').text(newTitle);\n
\t\t\t};\n
\n
\t\t\t// called when we\'ve selected a different element\n
\t\t\tvar selectedChanged = function(win, elems) {\n
\t\t\t\tvar mode = svgCanvas.getMode();\n
\t\t\t\tif (mode === \'select\') {\n
\t\t\t\t\tsetSelectMode();\n
\t\t\t\t}\n
\t\t\t\tvar is_node = (mode == "pathedit");\n
\t\t\t\t// if elems[1] is present, then we have more than one element\n
\t\t\t\tselectedElement = (elems.length === 1 || elems[1] == null ? elems[0] : null);\n
\t\t\t\tmultiselected = (elems.length >= 2 && elems[1] != null);\n
\t\t\t\tif (selectedElement != null) {\n
\t\t\t\t\t// unless we\'re already in always set the mode of the editor to select because\n
\t\t\t\t\t// upon creation of a text element the editor is switched into\n
\t\t\t\t\t// select mode and this event fires - we need our UI to be in sync\n
\n
\t\t\t\t\tif (!is_node) {\n
\t\t\t\t\t\tupdateToolbar();\n
\t\t\t\t\t}\n
\t\t\t\t} // if (elem != null)\n
\n
\t\t\t\t// Deal with pathedit mode\n
\t\t\t\ttogglePathEditMode(is_node, elems);\n
\t\t\t\tupdateContextPanel();\n
\t\t\t\tsvgCanvas.runExtensions(\'selectedChanged\', {\n
\t\t\t\t\telems: elems,\n
\t\t\t\t\tselectedElement: selectedElement,\n
\t\t\t\t\tmultiselected: multiselected\n
\t\t\t\t});\n
\t\t\t};\n
\n
\t\t\t// Call when part of element is in process of changing, generally\n
\t\t\t// on mousemove actions like rotate, move, etc.\n
\t\t\tvar elementTransition = function(win, elems) {\n
\t\t\t\tvar mode = svgCanvas.getMode();\n
\t\t\t\tvar elem = elems[0];\n
\n
\t\t\t\tif (!elem) {\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\n
\t\t\t\tmultiselected = (elems.length >= 2 && elems[1] != null);\n
\t\t\t\t// Only updating fields for single elements for now\n
\t\t\t\tif (!multiselected) {\n
\t\t\t\t\tswitch (mode) {\n
\t\t\t\t\t\tcase \'rotate\':\n
\t\t\t\t\t\t\tvar ang = svgCanvas.getRotationAngle(elem);\n
\t\t\t\t\t\t\t$(\'#angle\').val(ang);\n
\t\t\t\t\t\t\t$(\'#tool_reorient\').toggleClass(\'disabled\', ang === 0);\n
\t\t\t\t\t\t\tbreak;\n
\n
\t\t\t\t\t\t// TODO: Update values that change on move/resize, etc\n
//\t\t\t\t\t\tcase "select":\n
//\t\t\t\t\t\tcase "resize":\n
//\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\tsvgCanvas.runExtensions(\'elementTransition\', {\n
\t\t\t\t\telems: elems\n
\t\t\t\t});\n
\t\t\t};\n
\n
\t\t\t// called when any element has changed\n
\t\t\tvar elementChanged = function(win, elems) {\n
\t\t\t\tvar i,\n
\t\t\t\t\tmode = svgCanvas.getMode();\n
\t\t\t\tif (mode === \'select\') {\n
\t\t\t\t\tsetSelectMode();\n
\t\t\t\t}\n
\n
\t\t\t\tfor (i = 0; i < elems.length; ++i) {\n
\t\t\t\t\tvar elem = elems[i];\n
\n
\t\t\t\t\t// if the element changed was the svg, then it could be a resolution change\n
\t\t\t\t\tif (elem && elem.tagName === \'svg\') {\n
\t\t\t\t\t\tpopulateLayers();\n
\t\t\t\t\t\tupdateCanvas();\n
\t\t\t\t\t}\n
\t\t\t\t\t// Update selectedElement if element is no longer part of the image.\n
\t\t\t\t\t// This occurs for the text elements in Firefox\n
\t\t\t\t\telse if (elem && selectedElement && selectedElement.parentNode == null) {\n
//\t\t\t\t\t\t|| elem && elem.tagName == "path" && !multiselected) { // This was added in r1430, but not sure why\n
\t\t\t\t\t\tselectedElement = elem;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\teditor.showSaveWarning = true;\n
\n
\t\t\t\t// we update the contextual panel with potentially new\n
\t\t\t\t// positional/sizing information (we DON\'T want to update the\n
\t\t\t\t// toolbar here as that creates an infinite loop)\n
\t\t\t\t// also this updates the history buttons\n
\n
\t\t\t\t// we tell it to skip focusing the text control if the\n
\t\t\t\t// text element was previously in focus\n
\t\t\t\tupdateContextPanel();\n
\n
\t\t\t\t// In the event a gradient was flipped:\n
\t\t\t\tif (selectedElement && mode === \'select\') {\n
\t\t\t\t\tpaintBox.fill.update();\n
\t\t\t\t\tpaintBox.stroke.update();\n
\t\t\t\t}\n
\n
\t\t\t\tsvgCanvas.runExtensions(\'elementChanged\', {\n
\t\t\t\t\telems: elems\n
\t\t\t\t});\n
\t\t\t};\n
\n
\t\t\tvar zoomDone = function() {\n
\t\t\t\tupdateWireFrame();\n
\t\t\t\t// updateCanvas(); // necessary?\n
\t\t\t};\n
\n
\t\t\tvar zoomChanged = svgCanvas.zoomChanged = function(win, bbox, autoCenter) {\n
\t\t\t\tvar scrbar = 15,\n
\t\t\t\t\t// res = svgCanvas.getResolution(), // Currently unused\n
\t\t\t\t\tw_area = workarea;\n
\t\t\t\t// var canvas_pos = $(\'#svgcanvas\').position(); // Currently unused\n
\t\t\t\tvar z_info = svgCanvas.setBBoxZoom(bbox, w_area.width()-scrbar, w_area.height()-scrbar);\n
\t\t\t\tif (!z_info) {return;}\n
\t\t\t\tvar zoomlevel = z_info.zoom,\n
\t\t\t\t\tbb = z_info.bbox;\n
\n
\t\t\t\tif (zoomlevel < 0.001) {\n
\t\t\t\t\tchangeZoom({value: 0.1});\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\n
\t\t\t\t$(\'#zoom\').val((zoomlevel*100).toFixed(1));\n
\n
\t\t\t\tif (autoCenter) {\n
\t\t\t\t\tupdateCanvas();\n
\t\t\t\t} else {\n
\t\t\t\t\tupdateCanvas(false, {x: bb.x * zoomlevel + (bb.width * zoomlevel)/2, y: bb.y * zoomlevel + (bb.height * zoomlevel)/2});\n
\t\t\t\t}\n
\n
\t\t\t\tif (svgCanvas.getMode() == \'zoom\' && bb.width) {\n
\t\t\t\t\t// Go to select if a zoom box was drawn\n
\t\t\t\t\tsetSelectMode();\n
\t\t\t\t}\n
\n
\t\t\t\tzoomDone();\n
\t\t\t};\n
\n
\t\t\tchangeZoom = function(ctl) {\n
\t\t\t\tvar zoomlevel = ctl.value / 100;\n
\t\t\t\tif (zoomlevel < 0.001) {\n
\t\t\t\t\tctl.value = 0.1;\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\t\t\t\tvar zoom = svgCanvas.getZoom();\n
\t\t\t\tvar w_area = workarea;\n
\n
\t\t\t\tzoomChanged(window, {\n
\t\t\t\t\twidth: 0,\n
\t\t\t\t\theight: 0,\n
\t\t\t\t\t// center pt of scroll position\n
\t\t\t\t\tx: (w_area[0].scrollLeft + w_area.width()/2)/zoom,\n
\t\t\t\t\ty: (w_area[0].scrollTop + w_area.height()/2)/zoom,\n
\t\t\t\t\tzoom: zoomlevel\n
\t\t\t\t}, true);\n
\t\t\t};\n
\n
\t\t\t$(\'#cur_context_panel\').delegate(\'a\', \'click\', function() {\n
\t\t\t\tvar link = $(this);\n
\t\t\t\tif (link.attr(\'data-root\')) {\n
\t\t\t\t\tsvgCanvas.leaveContext();\n
\t\t\t\t} else {\n
\t\t\t\t\tsvgCanvas.setContext(link.text());\n
\t\t\t\t}\n
\t\t\t\tsvgCanvas.clearSelection();\n
\t\t\t\treturn false;\n
\t\t\t});\n
\n
\t\t\tvar contextChanged = function(win, context) {\n
\t\t\t\tvar link_str = \'\';\n
\t\t\t\tif (context) {\n
\t\t\t\t\tvar str = \'\';\n
\t\t\t\t\tlink_str = \'<a href="#" data-root="y">\' + svgCanvas.getCurrentDrawing().getCurrentLayerName() + \'</a>\';\n
\n
\t\t\t\t\t$(context).parentsUntil(\'#svgcontent > g\').andSelf().each(function() {\n
\t\t\t\t\t\tif (this.id) {\n
\t\t\t\t\t\t\tstr += \' > \' + this.id;\n
\t\t\t\t\t\t\tif (this !== context) {\n
\t\t\t\t\t\t\t\tlink_str += \' > <a href="#">\' + this.id + \'</a>\';\n
\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\tlink_str += \' > \' + this.id;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t});\n
\n
\t\t\t\t\tcur_context = str;\n
\t\t\t\t} else {\n
\t\t\t\t\tcur_context = null;\n
\t\t\t\t}\n
\t\t\t\t$(\'#cur_context_panel\').toggle(!!context).html(link_str);\n
\n
\t\t\t\tupdateTitle();\n
\t\t\t};\n
\n
\t\t\t// Makes sure the current selected paint is available to work with\n
\t\t\tvar prepPaints = function() {\n
\t\t\t\tpaintBox.fill.prep();\n
\t\t\t\tpaintBox.stroke.prep();\n
\t\t\t};\n
\n
\t\t\tvar flyout_funcs = {};\n
\n
\t\t\tvar setFlyoutTitles = function() {\n
\t\t\t\t$(\'.tools_flyout\').each(function() {\n
\t\t\t\t\tvar shower = $(\'#\' + this.id + \'_show\');\n
\t\t\t\t\tif (shower.data(\'isLibrary\')) {\n
\t\t\t\t\t\treturn;\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tvar tooltips = [];\n
\t\t\t\t\t$(this).children().each(function() {\n
\t\t\t\t\t\ttooltips.push(this.title);\n
\t\t\t\t\t});\n
\t\t\t\t\tshower[0].title = tooltips.join(\' / \');\n
\t\t\t\t});\n
\t\t\t};\n
\n
\t\t\tvar setFlyoutPositions = function() {\n
\t\t\t\t$(\'.tools_flyout\').each(function() {\n
\t\t\t\t\tvar shower = $(\'#\' + this.id + \'_show\');\n
\t\t\t\t\tvar pos = shower.offset();\n
\t\t\t\t\tvar w = shower.outerWidth();\n
\t\t\t\t\t$(this).css({left: (pos.left + w) * editor.tool_scale, top: pos.top});\n
\t\t\t\t});\n
\t\t\t};\n
\n
\t\t\tvar setupFlyouts = function(holders) {\n
\t\t\t\t$.each(holders, function(hold_sel, btn_opts) {\n
\t\t\t\t\tvar buttons = $(hold_sel).children();\n
\t\t\t\t\tvar show_sel = hold_sel + \'_show\';\n
\t\t\t\t\tvar shower = $(show_sel);\n
\t\t\t\t\tvar def = false;\n
\t\t\t\t\tbuttons.addClass(\'tool_button\')\n
\t\t\t\t\t\t.unbind(\'click mousedown mouseup\') // may not be necessary\n
\t\t\t\t\t\t.each(function(i) {\n
\t\t\t\t\t\t\t// Get this buttons options\n
\t\t\t\t\t\t\tvar opts = btn_opts[i];\n
\n
\t\t\t\t\t\t\t// Remember the function that goes with this ID\n
\t\t\t\t\t\t\tflyout_funcs[opts.sel] = opts.fn;\n
\n
\t\t\t\t\t\t\tif (opts.isDefault) {def = i;}\n
\n
\t\t\t\t\t\t\t// Clicking the icon in flyout should set this set\'s icon\n
\t\t\t\t\t\t\tvar func = function(event) {\n
\t\t\t\t\t\t\t\tvar options = opts;\n
\t\t\t\t\t\t\t\t//find the currently selected tool if comes from keystroke\n
\t\t\t\t\t\t\t\tif (event.type === \'keydown\') {\n
\t\t\t\t\t\t\t\t\tvar flyoutIsSelected = $(options.parent + \'_show\').hasClass(\'tool_button_current\');\n
\t\t\t\t\t\t\t\t\tvar currentOperation = $(options.parent + \'_show\').attr(\'data-curopt\');\n
\t\t\t\t\t\t\t\t\t$.each(holders[opts.parent], function(i, tool) {\n
\t\t\t\t\t\t\t\t\t\tif (tool.sel == currentOperation) {\n
\t\t\t\t\t\t\t\t\t\t\tif (!event.shiftKey || !flyoutIsSelected) {\n
\t\t\t\t\t\t\t\t\t\t\t\toptions = tool;\n
\t\t\t\t\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\t\t\t\t\toptions = holders[opts.parent][i+1] || holders[opts.parent][0];\n
\t\t\t\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\t\t});\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\tif ($(this).hasClass(\'disabled\')) {return false;}\n
\t\t\t\t\t\t\t\tif (toolButtonClick(show_sel)) {\n
\t\t\t\t\t\t\t\t\toptions.fn();\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\tvar icon;\n
\t\t\t\t\t\t\t\tif (options.icon) {\n
\t\t\t\t\t\t\t\t\ticon = $.getSvgIcon(options.icon, true);\n
\t\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\t\ticon = $(options.sel).children().eq(0).clone();\n
\t\t\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t\t\ticon[0].setAttribute(\'width\', shower.width());\n
\t\t\t\t\t\t\t\ticon[0].setAttribute(\'height\', shower.height());\n
\t\t\t\t\t\t\t\tshower.children(\':not(.flyout_arrow_horiz)\').remove();\n
\t\t\t\t\t\t\t\tshower.append(icon).attr(\'data-curopt\', options.sel); // This sets the current mode\n
\t\t\t\t\t\t\t};\n
\n
\t\t\t\t\t\t\t$(this).mouseup(func);\n
\n
\t\t\t\t\t\t\tif (opts.key) {\n
\t\t\t\t\t\t\t\t$(document).bind(\'keydown\', opts.key[0] + \' shift+\' + opts.key[0], func);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t});\n
\n
\t\t\t\t\tif (def) {\n
\t\t\t\t\t\tshower.attr(\'data-curopt\', btn_opts[def].sel);\n
\t\t\t\t\t} else if (!shower.attr(\'data-curopt\')) {\n
\t\t\t\t\t\t// Set first as default\n
\t\t\t\t\t\tshower.attr(\'data-curopt\', btn_opts[0].sel);\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tvar timer;\n
\t\t\t\t\tvar pos = $(show_sel).position();\n
\n
\t\t\t\t\t// Clicking the "show" icon should set the current mode\n
\t\t\t\t\tshower.mousedown(function(evt) {\n
\t\t\t\t\t\tif (shower.hasClass(\'disabled\')) {\n
\t\t\t\t\t\t\treturn false;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tvar holder = $(hold_sel);\n
\t\t\t\t\t\tvar l = pos.left + 34;\n
\t\t\t\t\t\tvar w = holder.width() * -1;\n
\t\t\t\t\t\tvar time = holder.data(\'shown_popop\') ? 200 : 0;\n
\t\t\t\t\t\ttimer = setTimeout(function() {\n
\t\t\t\t\t\t\t// Show corresponding menu\n
\t\t\t\t\t\t\tif (!shower.data(\'isLibrary\')) {\n
\t\t\t\t\t\t\t\tholder.css(\'left\', w).show().animate({\n
\t\t\t\t\t\t\t\t\tleft: l\n
\t\t\t\t\t\t\t\t}, 150);\n
\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\tholder.css(\'left\', l).show();\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\tholder.data(\'shown_popop\', true);\n
\t\t\t\t\t\t},time);\n
\t\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t\t}).mouseup(function(evt) {\n
\t\t\t\t\t\tclearTimeout(timer);\n
\t\t\t\t\t\tvar opt = $(this).attr(\'data-curopt\');\n
\t\t\t\t\t\t// Is library and popped up, so do nothing\n
\t\t\t\t\t\tif (shower.data(\'isLibrary\') && $(show_sel.replace(\'_show\', \'\')).is(\':visible\')) {\n
\t\t\t\t\t\t\ttoolButtonClick(show_sel, true);\n
\t\t\t\t\t\t\treturn;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tif (toolButtonClick(show_sel) && flyout_funcs[opt]) {\n
\t\t\t\t\t\t\tflyout_funcs[opt]();\n
\t\t\t\t\t\t}\n
\t\t\t\t\t});\n
\t\t\t\t\t// $(\'#tools_rect\').mouseleave(function(){$(\'#tools_rect\').fadeOut();});\n
\t\t\t\t});\n
\t\t\t\tsetFlyoutTitles();\n
\t\t\t\tsetFlyoutPositions();\n
\t\t\t};\n
\n
\t\t\tvar makeFlyoutHolder = function(id, child) {\n
\t\t\t\tvar div = $(\'<div>\', {\n
\t\t\t\t\t\'class\': \'tools_flyout\',\n
\t\t\t\t\tid: id\n
\t\t\t\t}).appendTo(\'#svg_editor\').append(child);\n
\n
\t\t\t\treturn div;\n
\t\t\t};\n
\n
\t\t\tvar uaPrefix = (function() {\n
\t\t\t\tvar prop;\n
\t\t\t\tvar regex = /^(Moz|Webkit|Khtml|O|ms|Icab)(?=[A-Z])/;\n
\t\t\t\tvar someScript = document.getElementsByTagName(\'script\')[0];\n
\t\t\t\tfor (prop in someScript.style) {\n
\t\t\t\t\tif (regex.test(prop)) {\n
\t\t\t\t\t\t// test is faster than match, so it\'s better to perform\n
\t\t\t\t\t\t// that on the lot and match only when necessary\n
\t\t\t\t\t\treturn prop.match(regex)[0];\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\t// Nothing found so far?\n
\t\t\t\tif (\'WebkitOpacity\' in someScript.style) {return \'Webkit\';}\n
\t\t\t\tif (\'KhtmlOpacity\' in someScript.style) {return \'Khtml\';}\n
\n
\t\t\t\treturn \'\';\n
\t\t\t}());\n
\n
\t\t\tvar scaleElements = function(elems, scale) {\n
\t\t\t\t// var prefix = \'-\' + uaPrefix.toLowerCase() + \'-\'; // Currently unused\n
\t\t\t\tvar sides = [\'top\', \'left\', \'bottom\', \'right\'];\n
\n
\t\t\t\telems.each(function() {\n
\t\t\t\t\t// Handled in CSS\n
\t\t\t\t\t// this.style[uaPrefix + \'Transform\'] = \'scale(\' + scale + \')\';\n
\t\t\t\t\tvar i;\n
\t\t\t\t\tvar el = $(this);\n
\t\t\t\t\tvar w = el.outerWidth() * (scale - 1);\n
\t\t\t\t\tvar h = el.outerHeight() * (scale - 1);\n
\t\t\t\t\t// var margins = {}; // Currently unused\n
\n
\t\t\t\t\tfor (i = 0; i < 4; i++) {\n
\t\t\t\t\t\tvar s = sides[i];\n
\t\t\t\t\t\tvar cur = el.data(\'orig_margin-\' + s);\n
\t\t\t\t\t\tif (cur == null) {\n
\t\t\t\t\t\t\tcur = parseInt(el.css(\'margin-\' + s), 10);\n
\t\t\t\t\t\t\t// Cache the original margin\n
\t\t\t\t\t\t\tel.data(\'orig_margin-\' + s, cur);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tvar val = cur * scale;\n
\t\t\t\t\t\tif (s === \'right\') {\n
\t\t\t\t\t\t\tval += w;\n
\t\t\t\t\t\t} else if (s === \'bottom\') {\n
\t\t\t\t\t\t\tval += h;\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tel.css(\'margin-\' + s, val);\n
\t\t\t\t\t\t// el.css(\'outline\', \'1px solid red\');\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t};\n
\n
\t\t\tvar setIconSize = editor.setIconSize = function (size) {\n
\n
//\t\t\t\tvar elems = $(\'.tool_button, .push_button, .tool_button_current, .disabled, .icon_label, #url_notice, #tool_open\');\n
\t\t\t\tvar sel_toscale = \'#tools_top .toolset, #editor_panel > *, #history_panel > *,\'+\n
\'\t\t\t\t#main_button, #tools_left > *, #path_node_panel > *, #multiselected_panel > *,\'+\n
\'\t\t\t\t#g_panel > *, #tool_font_size > *, .tools_flyout\';\n
\n
\t\t\t\tvar elems = $(sel_toscale);\n
\t\t\t\tvar scale = 1;\n
\n
\t\t\t\tif (typeof size === \'number\') {\n
\t\t\t\t\tscale = size;\n
\t\t\t\t} else {\n
\t\t\t\t\tvar icon_sizes = {s: 0.75, m:1, l: 1.25, xl: 1.5};\n
\t\t\t\t\tscale = icon_sizes[size];\n
\t\t\t\t}\n
\n
\t\t\t\teditor.tool_scale = scale;\n
\n
\t\t\t\tsetFlyoutPositions();\n
\t\t\t\t// $(\'.tools_flyout\').each(function() {\n
//\t\t\t\t\tvar pos = $(this).position();\n
//\t\t\t\t\tconsole.log($(this), pos.left+(34 * scale));\n
//\t\t\t\t\t$(this).css({\'left\': pos.left+(34 * scale), \'top\': pos.top+(77 * scale)});\n
//\t\t\t\t\tconsole.log(\'l\', $(this).css(\'left\'));\n
//\t\t\t\t});\n
\n
//\t\t\t\tvar scale = .75;\n
\n
\t\t\t\tvar hidden_ps = elems.parents(\':hidden\');\n
\t\t\t\thidden_ps.css(\'visibility\', \'hidden\').show();\n
\t\t\t\tscaleElements(elems, scale);\n
\t\t\t\thidden_ps.css(\'visibility\', \'visible\').hide();\n
//\t\t\t\treturn;\n
\n
\t\t\t\t$.pref(\'iconsize\', size);\n
\t\t\t\t$(\'#iconsize\').val(size);\n
\n
\t\t\t\t// Change icon size\n
//\t\t\t\t$(\'.tool_button, .push_button, .tool_button_current, .disabled, .icon_label, #url_notice, #tool_open\')\n
//\t\t\t\t.find(\'> svg, > img\').each(function() {\n
//\t\t\t\t\tthis.setAttribute(\'width\',size_num);\n
//\t\t\t\t\tthis.setAttribute(\'height\',size_num);\n
//\t\t\t\t});\n
//\n
//\t\t\t\t$.resizeSvgIcons({\n
//\t\t\t\t\t\'.flyout_arrow_horiz > svg, .flyout_arrow_horiz > img\': size_num / 5,\n
//\t\t\t\t\t\'#logo > svg, #logo > img\': size_num * 1.3,\n
//\t\t\t\t\t\'#tools_bottom .icon_label > *\': (size_num === 16 ? 18 : size_num * .75)\n
//\t\t\t\t});\n
//\t\t\t\tif (size != \'s\') {\n
//\t\t\t\t\t$.resizeSvgIcons({\'#layerbuttons svg, #layerbuttons img\': size_num * .6});\n
//\t\t\t\t}\n
\n
\t\t\t\t// Note that all rules will be prefixed with \'#svg_editor\' when parsed\n
\t\t\t\tvar cssResizeRules = {\n
//\t\t\t\t\t\'.tool_button,\\\n
//\t\t\t\t\t.push_button,\\\n
//\t\t\t\t\t.tool_button_current,\\\n
//\t\t\t\t\t.push_button_pressed,\\\n
//\t\t\t\t\t.disabled,\\\n
//\t\t\t\t\t.icon_label,\\\n
//\t\t\t\t\t.tools_flyout .tool_button\': {\n
//\t\t\t\t\t\t\'width\': {s: \'16px\', l: \'32px\', xl: \'48px\'},\n
//\t\t\t\t\t\t\'height\': {s: \'16px\', l: \'32px\', xl: \'48px\'},\n
//\t\t\t\t\t\t\'padding\': {s: \'1px\', l: \'2px\', xl: \'3px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'.tool_sep\': {\n
//\t\t\t\t\t\t\'height\': {s: \'16px\', l: \'32px\', xl: \'48px\'},\n
//\t\t\t\t\t\t\'margin\': {s: \'2px 2px\', l: \'2px 5px\', xl: \'2px 8px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'#main_icon\': {\n
//\t\t\t\t\t\t\'width\': {s: \'31px\', l: \'53px\', xl: \'75px\'},\n
//\t\t\t\t\t\t\'height\': {s: \'22px\', l: \'42px\', xl: \'64px\'}\n
//\t\t\t\t\t},\n
\t\t\t\t\t\'#tools_top\': {\n
\t\t\t\t\t\t\'left\': 50,\n
\t\t\t\t\t\t\'height\': 72\n
\t\t\t\t\t},\n
\t\t\t\t\t\'#tools_left\': {\n
\t\t\t\t\t\t\'width\': 31,\n
\t\t\t\t\t\t\'top\': 74\n
\t\t\t\t\t},\n
\t\t\t\t\t\'div#workarea\': {\n
\t\t\t\t\t\t\'left\': 38,\n
\t\t\t\t\t\t\'top\': 74\n
\t\t\t\t\t}\n
//\t\t\t\t\t\'#tools_bottom\': {\n
//\t\t\t\t\t\t\'left\': {s: \'27px\', l: \'46px\', xl: \'65px\'},\n
//\t\t\t\t\t\t\'height\': {s: \'58px\', l: \'98px\', xl: \'145px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'#color_tools\': {\n
//\t\t\t\t\t\t\'border-spacing\': {s: \'0 1px\'},\n
//\t\t\t\t\t\t\'margin-top\': {s: \'-1px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'#color_tools .icon_label\': {\n
//\t\t\t\t\t\t\'width\': {l:\'43px\', xl: \'60px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'.color_tool\': {\n
//\t\t\t\t\t\t\'height\': {s: \'20px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'#tool_opacity\': {\n
//\t\t\t\t\t\t\'top\': {s: \'1px\'},\n
//\t\t\t\t\t\t\'height\': {s: \'auto\', l:\'auto\', xl:\'auto\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'#tools_top input, #tools_bottom input\': {\n
//\t\t\t\t\t\t\'margin-top\': {s: \'2px\', l: \'4px\', xl: \'5px\'},\n
//\t\t\t\t\t\t\'height\': {s: \'auto\', l: \'auto\', xl: \'auto\'},\n
//\t\t\t\t\t\t\'border\': {s: \'1px solid #555\', l: \'auto\', xl: \'auto\'},\n
//\t\t\t\t\t\t\'font-size\': {s: \'.9em\', l: \'1.2em\', xl: \'1.4em\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'#zoom_panel\': {\n
//\t\t\t\t\t\t\'margin-top\': {s: \'3px\', l: \'4px\', xl: \'5px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'#copyright, #tools_bottom .label\': {\n
//\t\t\t\t\t\t\'font-size\': {l: \'1.5em\', xl: \'2em\'},\n
//\t\t\t\t\t\t\'line-height\': {s: \'15px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'#tools_bottom_2\': {\n
//\t\t\t\t\t\t\'width\': {l: \'295px\', xl: \'355px\'},\n
//\t\t\t\t\t\t\'top\': {s: \'4px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'#tools_top > div, #tools_top\': {\n
//\t\t\t\t\t\t\'line-height\': {s: \'17px\', l: \'34px\', xl: \'50px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'.dropdown button\': {\n
//\t\t\t\t\t\t\'height\': {s: \'18px\', l: \'34px\', xl: \'40px\'},\n
//\t\t\t\t\t\t\'line-height\': {s: \'18px\', l: \'34px\', xl: \'40px\'},\n
//\t\t\t\t\t\t\'margin-top\': {s: \'3px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'#tools_top label, #tools_bottom label\': {\n
//\t\t\t\t\t\t\'font-size\': {s: \'1em\', l: \'1.5em\', xl: \'2em\'},\n
//\t\t\t\t\t\t\'height\': {s: \'25px\', l: \'42px\', xl: \'64px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'div.toolset\': {\n
//\t\t\t\t\t\t\'height\': {s: \'25px\', l: \'42px\', xl: \'64px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'#tool_bold, #tool_italic\': {\n
//\t\t\t\t\t\t\'font-size\': {s: \'1.5em\', l: \'3em\', xl: \'4.5em\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'#sidepanels\': {\n
//\t\t\t\t\t\t\'top\': {s: \'50px\', l: \'88px\', xl: \'125px\'},\n
//\t\t\t\t\t\t\'bottom\': {s: \'51px\', l: \'68px\', xl: \'65px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'#layerbuttons\': {\n
//\t\t\t\t\t\t\'width\': {l: \'130px\', xl: \'175px\'},\n
//\t\t\t\t\t\t\'height\': {l: \'24px\', xl: \'30px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'#layerlist\': {\n
//\t\t\t\t\t\t\'width\': {l: \'128px\', xl: \'150px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'.layer_button\': {\n
//\t\t\t\t\t\t\'width\': {l: \'19px\', xl: \'28px\'},\n
//\t\t\t\t\t\t\'height\': {l: \'19px\', xl: \'28px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'input.spin-button\': {\n
//\t\t\t\t\t\t\'background-image\': {l: \'url(\'images/spinbtn_updn_big.png\')\', xl: \'url(\'images/spinbtn_updn_big.png\')\'},\n
//\t\t\t\t\t\t\'background-position\': {l: \'100% -5px\', xl: \'100% -2px\'},\n
//\t\t\t\t\t\t\'padding-right\': {l: \'24px\', xl: \'24px\' }\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'input.spin-button.up\': {\n
//\t\t\t\t\t\t\'background-position\': {l: \'100% -45px\', xl: \'100% -42px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'input.spin-button.down\': {\n
//\t\t\t\t\t\t\'background-position\': {l: \'100% -85px\', xl: \'100% -82px\'}\n
//\t\t\t\t\t},\n
//\t\t\t\t\t\'#position_opts\': {\n
//\t\t\t\t\t\t\'width\': {all: (size_num*4) +\'px\'}\n
//\t\t\t\t\t}\n
\t\t\t\t};\n
\n
\t\t\t\tvar rule_elem = $(\'#tool_size_rules\');\n
\t\t\t\tif (!rule_elem.length) {\n
\t\t\t\t\trule_elem = $(\'<style id="tool_size_rules"><\\/style>\').appendTo(\'head\');\n
\t\t\t\t} else {\n
\t\t\t\t\trule_elem.empty();\n
\t\t\t\t}\n
\n
\t\t\t\tif (size !== \'m\') {\n
\t\t\t\t\tvar styleStr = \'\';\n
\t\t\t\t\t$.each(cssResizeRules, function(selector, rules) {\n
\t\t\t\t\t\tselector = \'#svg_editor \' + selector.replace(/,/g,\', #svg_editor\');\n
\t\t\t\t\t\tstyleStr += selector + \'{\';\n
\t\t\t\t\t\t$.each(rules, function(prop, values) {\n
\t\t\t\t\t\t\tvar val;\n
\t\t\t\t\t\t\tif (typeof values === \'number\') {\n
\t\t\t\t\t\t\t\tval = (values * scale) + \'px\';\n
\t\t\t\t\t\t\t} else if (values[size] || values.all) {\n
\t\t\t\t\t\t\t\tval = (values[size] || values.all);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\tstyleStr += (prop + \':\' + val + \';\');\n
\t\t\t\t\t\t});\n
\t\t\t\t\t\tstyleStr += \'}\';\n
\t\t\t\t\t});\n
\t\t\t\t\t//this.style[uaPrefix + \'Transform\'] = \'scale(\' + scale + \')\';\n
\t\t\t\t\tvar prefix = \'-\' + uaPrefix.toLowerCase() + \'-\';\n
\t\t\t\t\tstyleStr += (sel_toscale + \'{\' + prefix + \'transform: scale(\' + scale + \');}\'\n
\t\t\t\t\t+ \' #svg_editor div.toolset .toolset {\' + prefix + \'transform: scale(1); margin: 1px !important;}\' // Hack for markers\n
\t\t\t\t\t+ \' #svg_editor .ui-slider {\' + prefix + \'transform: scale(\' + (1/scale) + \');}\' // Hack for sliders\n
\t\t\t\t\t);\n
\t\t\t\t\trule_elem.text(styleStr);\n
\t\t\t\t}\n
\n
\t\t\t\tsetFlyoutPositions();\n
\t\t\t};\n
\n
\t\t\t// TODO: Combine this with addDropDown or find other way to optimize\n
\t\t\tvar addAltDropDown = function(elem, list, callback, opts) {\n
\t\t\t\tvar button = $(elem);\n
\t\t\t\tlist = $(list);\n
\t\t\t\tvar on_button = false;\n
\t\t\t\tvar dropUp = opts.dropUp;\n
\t\t\t\tif (dropUp) {\n
\t\t\t\t\t$(elem).addClass(\'dropup\');\n
\t\t\t\t}\n
\t\t\t\tlist.find(\'li\').bind(\'mouseup\', function() {\n
\t\t\t\t\tif (opts.seticon) {\n
\t\t\t\t\t\tsetIcon(\'#cur_\' + button[0].id , $(this).children());\n
\t\t\t\t\t\t$(this).addClass(\'current\').siblings().removeClass(\'current\');\n
\t\t\t\t\t}\n
\t\t\t\t\tcallback.apply(this, arguments);\n
\n
\t\t\t\t});\n
\n
\t\t\t\t$(window).mouseup(function(evt) {\n
\t\t\t\t\tif (!on_button) {\n
\t\t\t\t\t\tbutton.removeClass(\'down\');\n
\t\t\t\t\t\tlist.hide();\n
\t\t\t\t\t\tlist.css({top:0, left:0});\n
\t\t\t\t\t}\n
\t\t\t\t\ton_button = false;\n
\t\t\t\t});\n
\n
\t\t\t\t// var height = list.height(); // Currently unused\n
\t\t\t\tbutton.bind(\'mousedown\',function() {\n
\t\t\t\t\tvar off = button.offset();\n
\t\t\t\t\tif (dropUp) {\n
\t\t\t\t\t\toff.top -= list.height();\n
\t\t\t\t\t\toff.left += 8;\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\toff.top += button.height();\n
\t\t\t\t\t}\n
\t\t\t\t\tlist.offset(off);\n
\n
\t\t\t\t\tif (!button.hasClass(\'down\')) {\n
\t\t\t\t\t\tlist.show();\n
\t\t\t\t\t\ton_button = true;\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\t// CSS position must be reset for Webkit\n
\t\t\t\t\t\tlist.hide();\n
\t\t\t\t\t\tlist.css({top:0, left:0});\n
\t\t\t\t\t}\n
\t\t\t\t\tbutton.toggleClass(\'down\');\n
\t\t\t\t}).hover(function() {\n
\t\t\t\t\ton_button = true;\n
\t\t\t\t}).mouseout(function() {\n
\t\t\t\t\ton_button = false;\n
\t\t\t\t});\n
\n
\t\t\t\tif (opts.multiclick) {\n
\t\t\t\t\tlist.mousedown(function() {\n
\t\t\t\t\t\ton_button = true;\n
\t\t\t\t\t});\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar extsPreLang = [];\n
\t\t\tvar extAdded = function(win, ext) {\n
\t\t\t\tif (!ext) {\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\t\t\t\tvar cb_called = false;\n
\t\t\t\tvar resize_done = false;\n
\t\t\t\tvar cb_ready = true; // Set to false to delay callback (e.g. wait for $.svgIcons)\n
\t\t\t\t\n
\t\t\t\tif (ext.langReady) {\n
\t\t\t\t\tif (editor.langChanged) { // We check for this since the "lang" pref could have been set by storage\n
\t\t\t\t\t\tvar lang = $.pref(\'lang\');\n
\t\t\t\t\t\text.langReady({lang:lang, uiStrings:uiStrings});\n
\t\t\t\t\t}\n
\t\t\t\t\telse {\n
\t\t\t\t\t\textsPreLang.push(ext);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\tfunction prepResize() {\n
\t\t\t\t\tif (resize_timer) {\n
\t\t\t\t\t\tclearTimeout(resize_timer);\n
\t\t\t\t\t\tresize_timer = null;\n
\t\t\t\t\t}\n
\t\t\t\t\tif (!resize_done) {\n
\t\t\t\t\t\tresize_timer = setTimeout(function() {\n
\t\t\t\t\t\t\tresize_done = true;\n
\t\t\t\t\t\t\tsetIconSize($.pref(\'iconsize\'));\n
\t\t\t\t\t\t}, 50);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\tvar runCallback = function() {\n
\t\t\t\t\tif (ext.callback && !cb_called && cb_ready) {\n
\t\t\t\t\t\tcb_called = true;\n
\t\t\t\t\t\text.callback();\n
\t\t\t\t\t}\n
\t\t\t\t};\n
\n
\t\t\t\tvar btn_selects = [];\n
\n
\t\t\t\tif (ext.context_tools) {\n
\t\t\t\t\t$.each(ext.context_tools, function(i, tool) {\n
\t\t\t\t\t\t// Add select tool\n
\t\t\t\t\t\tvar html;\n
\t\t\t\t\t\tvar cont_id = tool.container_id ? (\' id="\' + tool.container_id + \'"\') : \'\';\n
\t\t\t\t\t\tvar panel = $(\'#\' + tool.panel);\n
\n
\t\t\t\t\t\t// create the panel if it doesn\'t exist\n
\t\t\t\t\t\tif (!panel.length) {\n
\t\t\t\t\t\t\tpanel = $(\'<div>\', {id: tool.panel}).appendTo(\'#tools_top\');\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t// TODO: Allow support for other types, or adding to existing tool\n
\t\t\t\t\t\tswitch (tool.type) {\n
\t\t\t\t\t\tcase \'tool_button\':\n
\t\t\t\t\t\t\thtml = \'<div class="tool_button">\' + tool.id + \'</div>\';\n
\t\t\t\t\t\t\tvar div = $(html).appendTo(panel);\n
\t\t\t\t\t\t\tif (tool.events) {\n
\t\t\t\t\t\t\t\t$.each(tool.events, function(evt, func) {\n
\t\t\t\t\t\t\t\t\t$(div).bind(evt, func);\n
\t\t\t\t\t\t\t\t});\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tcase \'select\':\n
\t\t\t\t\t\t\thtml = \'<label\' + cont_id + \'>\'\n
\t\t\t\t\t\t\t\t+ \'<select id="\' + tool.id + \'">\';\n
\t\t\t\t\t\t\t$.each(tool.options, function(val, text) {\n
\t\t\t\t\t\t\t\tvar sel = (val == tool.defval) ? " selected":"";\n
\t\t\t\t\t\t\t\thtml += \'<option value="\'+val+\'"\' + sel + \'>\' + text + \'</option>\';\n
\t\t\t\t\t\t\t});\n
\t\t\t\t\t\t\thtml += "</select></label>";\n
\t\t\t\t\t\t\t// Creates the tool, hides & adds it, returns the select element\n
\t\t\t\t\t\t\tvar sel = $(html).appendTo(panel).find(\'select\');\n
\n
\t\t\t\t\t\t\t$.each(tool.events, function(evt, func) {\n
\t\t\t\t\t\t\t\t$(sel).bind(evt, func);\n
\t\t\t\t\t\t\t});\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tcase \'button-select\':\n
\t\t\t\t\t\t\thtml = \'<div id="\' + tool.id + \'" class="dropdown toolset" title="\' + tool.title + \'">\'\n
\t\t\t\t\t\t\t\t+ \'<div id="cur_\' + tool.id + \'" class="icon_label"></div><button></button></div>\';\n
\n
\t\t\t\t\t\t\tvar list = $(\'<ul id="\' + tool.id + \'_opts"></ul>\').appendTo(\'#option_lists\');\n
\n
\t\t\t\t\t\t\tif (tool.colnum) {\n
\t\t\t\t\t\t\t\tlist.addClass(\'optcols\' + tool.colnum);\n
\t\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t\t// Creates the tool, hides & adds it, returns the select element\n
\t\t\t\t\t\t\tvar dropdown = $(html).appendTo(panel).children();\n
\n
\t\t\t\t\t\t\tbtn_selects.push({\n
\t\t\t\t\t\t\t\telem: (\'#\' + tool.id),\n
\t\t\t\t\t\t\t\tlist: (\'#\' + tool.id + \'_opts\'),\n
\t\t\t\t\t\t\t\ttitle: tool.title,\n
\t\t\t\t\t\t\t\tcallback: tool.events.change,\n
\t\t\t\t\t\t\t\tcur: (\'#cur_\' + tool.id)\n
\t\t\t\t\t\t\t});\n
\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tcase \'input\':\n
\t\t\t\t\t\t\thtml = \'<label\' + cont_id + \'>\'\n
\t\t\t\t\t\t\t\t+ \'<span id="\' + tool.id + \'_label">\'\n
\t\t\t\t\t\t\t\t+ tool.label + \':</span>\'\n
\t\t\t\t\t\t\t\t+ \'<input id="\' + tool.id + \'" title="\' + tool.title\n
\t\t\t\t\t\t\t\t+ \'" size="\' + (tool.size || "4") + \'" value="\' + (tool.defval || "") + \'" type="text"/></label>\';\n
\n
\t\t\t\t\t\t\t// Creates the tool, hides & adds it, returns the select element\n
\n
\t\t\t\t\t\t\t// Add to given tool.panel\n
\t\t\t\t\t\t\tvar inp = $(html).appendTo(panel).find(\'input\');\n
\n
\t\t\t\t\t\t\tif (tool.spindata) {\n
\t\t\t\t\t\t\t\tinp.SpinButton(tool.spindata);\n
\t\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t\tif (tool.events) {\n
\t\t\t\t\t\t\t\t$.each(tool.events, function(evt, func) {\n
\t\t\t\t\t\t\t\t\tinp.bind(evt, func);\n
\t\t\t\t\t\t\t\t});\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\tbreak;\n
\n
\t\t\t\t\t\tdefault:\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t});\n
\t\t\t\t}\n
\n
\t\t\t\tif (ext.buttons) {\n
\t\t\t\t\tvar fallback_obj = {},\n
\t\t\t\t\t\tplacement_obj = {},\n
\t\t\t\t\t\tsvgicons = ext.svgicons,\n
\t\t\t\t\t\tholders = {};\n
\n
\t\t\t\t\t// Add buttons given by extension\n
\t\t\t\t\t$.each(ext.buttons, function(i, btn) {\n
\t\t\t\t\t\tvar icon, svgicon, tls_id;\n
\t\t\t\t\t\tvar id = btn.id;\n
\t\t\t\t\t\tvar num = i;\n
\n
\t\t\t\t\t\t// Give button a unique ID\n
\t\t\t\t\t\twhile($(\'#\'+id).length) {\n
\t\t\t\t\t\t\tid = btn.id + \'_\' + (++num);\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tif (!svgicons) {\n
\t\t\t\t\t\t\ticon = $(\'<img src="\' + btn.icon + \'">\');\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\tfallback_obj[id] = btn.icon;\n
\t\t\t\t\t\t\tsvgicon = btn.svgicon || btn.id;\n
\t\t\t\t\t\t\tif (btn.type == \'app_menu\') {\n
\t\t\t\t\t\t\t\tplacement_obj[\'#\' + id + \' > div\'] = svgicon;\n
\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\tplacement_obj[\'#\' + id] = svgicon;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tvar cls, parent;\n
\n
\t\t\t\t\t\t// Set button up according to its type\n
\t\t\t\t\t\tswitch ( btn.type ) {\n
\t\t\t\t\t\tcase \'mode_flyout\':\n
\t\t\t\t\t\tcase \'mode\':\n
\t\t\t\t\t\t\tcls = \'tool_button\';\n
\t\t\t\t\t\t\tparent = \'#tools_left\';\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tcase \'context\':\n
\t\t\t\t\t\t\tcls = \'tool_button\';\n
\t\t\t\t\t\t\tparent = \'#\' + btn.panel;\n
\t\t\t\t\t\t\t// create the panel if it doesn\'t exist\n
\t\t\t\t\t\t\tif (!$(parent).length) {\n
\t\t\t\t\t\t\t\t$(\'<div>\', {id: btn.panel}).appendTo(\'#tools_top\');\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tcase \'app_menu\':\n
\t\t\t\t\t\t\tcls = \'\';\n
\t\t\t\t\t\t\tparent = \'#main_menu ul\';\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tvar flyout_holder, cur_h, show_btn, ref_data, ref_btn;\n
\t\t\t\t\t\tvar button = $((btn.list || btn.type == \'app_menu\') ? \'<li/>\' : \'<div/>\')\n
\t\t\t\t\t\t\t.attr(\'id\', id)\n
\t\t\t\t\t\t\t.attr(\'title\', btn.title)\n
\t\t\t\t\t\t\t.addClass(cls);\n
\t\t\t\t\t\tif (!btn.includeWith && !btn.list) {\n
\t\t\t\t\t\t\tif (\'position\' in btn) {\n
\t\t\t\t\t\t\t\tif ($(parent).children().eq(btn.position).length) {\n
\t\t\t\t\t\t\t\t\t$(parent).children().eq(btn.position).before(button);\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\telse {\n
\t\t\t\t\t\t\t\t\t$(parent).children().last().before(button);\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\tbutton.appendTo(parent);\n
\t\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t\tif (btn.type ==\'mode_flyout\') {\n
\t\t\t\t\t\t\t// Add to flyout menu / make flyout menu\n
\t//\t\t\t\t\t\t\tvar opts = btn.includeWith;\n
\t//\t\t\t\t\t\t\t// opts.button, default, position\n
\t\t\t\t\t\t\t\tref_btn = $(button);\n
\n
\t\t\t\t\t\t\t\tflyout_holder = ref_btn.parent();\n
\t\t\t\t\t\t\t\t// Create a flyout menu if there isn\'t one already\n
\t\t\t\t\t\t\t\tif (!ref_btn.parent().hasClass(\'tools_flyout\')) {\n
\t\t\t\t\t\t\t\t\t// Create flyout placeholder\n
\t\t\t\t\t\t\t\t\ttls_id = ref_btn[0].id.replace(\'tool_\', \'tools_\');\n
\t\t\t\t\t\t\t\t\tshow_btn = ref_btn.clone()\n
\t\t\t\t\t\t\t\t\t\t.attr(\'id\', tls_id + \'_show\')\n
\t\t\t\t\t\t\t\t\t\t.append($(\'<div>\', {\'class\': \'flyout_arrow_horiz\'}));\n
\n
\t\t\t\t\t\t\t\t\tref_btn.before(show_btn);\n
\n
\t\t\t\t\t\t\t\t\t// Create a flyout div\n
\t\t\t\t\t\t\t\t\tflyout_holder = makeFlyoutHolder(tls_id, ref_btn);\n
\t\t\t\t\t\t\t\t\tflyout_holder.data(\'isLibrary\', true);\n
\t\t\t\t\t\t\t\t\tshow_btn.data(\'isLibrary\', true);\n
\t\t\t\t\t\t\t\t}\n
\t//\t\t\t\t\t\t\tref_data = Actions.getButtonData(opts.button);\n
\n
\t\t\t\t\t\t\t\tplacement_obj[\'#\' + tls_id + \'_show\'] = btn.id;\n
\t\t\t\t\t\t\t\t// TODO: Find way to set the current icon using the iconloader if this is not default\n
\n
\t\t\t\t\t\t\t\t// Include data for extension button as well as ref button\n
\t\t\t\t\t\t\t\tcur_h = holders[\'#\'+flyout_holder[0].id] = [{\n
\t\t\t\t\t\t\t\t\tsel: \'#\'+id,\n
\t\t\t\t\t\t\t\t\tfn: btn.events.click,\n
\t\t\t\t\t\t\t\t\ticon: btn.id,\n
//\t\t\t\t\t\t\t\t\tkey: btn.key,\n
\t\t\t\t\t\t\t\t\tisDefault: true\n
\t\t\t\t\t\t\t\t}, ref_data];\n
\t//\n
\t//\t\t\t\t\t\t\t// {sel:\'#tool_rect\', fn: clickRect, evt: \'mouseup\', key: 4, parent: \'#tools_rect\', icon: \'rect\'}\n
\t//\n
\t//\t\t\t\t\t\t\tvar pos = (\'position\' in opts)?opts.position:\'last\';\n
\t//\t\t\t\t\t\t\tvar len = flyout_holder.children().length;\n
\t//\n
\t//\t\t\t\t\t\t\t// Add at given position or end\n
\t//\t\t\t\t\t\t\tif (!isNaN(pos) && pos >= 0 && pos < len) {\n
\t//\t\t\t\t\t\t\t\tflyout_holder.children().eq(pos).before(button);\n
\t//\t\t\t\t\t\t\t} else {\n
\t//\t\t\t\t\t\t\t\tflyout_holder.append(button);\n
\t//\t\t\t\t\t\t\t\tcur_h.reverse();\n
\t//\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t} else if (btn.type == \'app_menu\') {\n
\t\t\t\t\t\t\t\tbutton.append(\'<div>\').append(btn.title);\n
\t\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\telse if (btn.list) {\n
\t\t\t\t\t\t\t// Add button to list\n
\t\t\t\t\t\t\tbutton.addClass(\'push_button\');\n
\t\t\t\t\t\t\t$(\'#\' + btn.list + \'_opts\').append(button);\n
\t\t\t\t\t\t\tif (btn.isDefault) {\n
\t\t\t\t\t\t\t\t$(\'#cur_\' + btn.list).append(button.children().clone());\n
\t\t\t\t\t\t\t\tsvgicon = btn.svgicon || btn.id;\n
\t\t\t\t\t\t\t\tplacement_obj[\'#cur_\' + btn.list] = svgicon;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\telse if (btn.includeWith) {\n
\t\t\t\t\t\t\t// Add to flyout menu / make flyout menu\n
\t\t\t\t\t\t\tvar opts = btn.includeWith;\n
\t\t\t\t\t\t\t// opts.button, default, position\n
\t\t\t\t\t\t\tref_btn = $(opts.button);\n
\n
\t\t\t\t\t\t\tflyout_holder = ref_btn.parent();\n
\t\t\t\t\t\t\t// Create a flyout menu if there isn\'t one already\n
\t\t\t\t\t\t\tif (!ref_btn.parent().hasClass(\'tools_flyout\')) {\n
\t\t\t\t\t\t\t\t// Create flyout placeholder\n
\t\t\t\t\t\t\t\ttls_id = ref_btn[0].id.replace(\'tool_\', \'tools_\');\n
\t\t\t\t\t\t\t\tshow_btn = ref_btn.clone()\n
\t\t\t\t\t\t\t\t\t.attr(\'id\',tls_id + \'_show\')\n
\t\t\t\t\t\t\t\t\t.append($(\'<div>\', {\'class\': \'flyout_arrow_horiz\'}));\n
\n
\t\t\t\t\t\t\t\tref_btn.before(show_btn);\n
\n
\t\t\t\t\t\t\t\t// Create a flyout div\n
\t\t\t\t\t\t\t\tflyout_holder = makeFlyoutHolder(tls_id, ref_btn);\n
\t\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t\tref_data = Actions.getButtonData(opts.button);\n
\n
\t\t\t\t\t\t\tif (opts.isDefault) {\n
\t\t\t\t\t\t\t\tplacement_obj[\'#\' + tls_id + \'_show\'] = btn.id;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t// TODO: Find way to set the current icon using the iconloader if this is not default\n
\n
\t\t\t\t\t\t\t// Include data for extension button as well as ref button\n
\t\t\t\t\t\t\tcur_h = holders[\'#\'+flyout_holder[0].id] = [{\n
\t\t\t\t\t\t\t\tsel: \'#\'+id,\n
\t\t\t\t\t\t\t\tfn: btn.events.click,\n
\t\t\t\t\t\t\t\ticon: btn.id,\n
\t\t\t\t\t\t\t\tkey: btn.key,\n
\t\t\t\t\t\t\t\tisDefault: btn.includeWith?btn.includeWith.isDefault:0\n
\t\t\t\t\t\t\t}, ref_data];\n
\n
\t\t\t\t\t\t\t// {sel:\'#tool_rect\', fn: clickRect, evt: \'mouseup\', key: 4, parent: \'#tools_rect\', icon: \'rect\'}\n
\n
\t\t\t\t\t\t\tvar pos  = (\'position\' in opts) ? opts.position : \'last\';\n
\t\t\t\t\t\t\tvar len = flyout_holder.children().length;\n
\n
\t\t\t\t\t\t\t// Add at given position or end\n
\t\t\t\t\t\t\tif (!isNaN(pos) && pos >= 0 && pos < len) {\n
\t\t\t\t\t\t\t\tflyout_holder.children().eq(pos).before(button);\n
\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\tflyout_holder.append(button);\n
\t\t\t\t\t\t\t\tcur_h.reverse();\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tif (!svgicons) {\n
\t\t\t\t\t\t\tbutton.append(icon);\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tif (!btn.list) {\n
\t\t\t\t\t\t\t// Add given events to button\n
\t\t\t\t\t\t\t$.each(btn.events, function(name, func) {\n
\t\t\t\t\t\t\t\tif (name == \'click\' && btn.type == \'mode\') {\n
\t\t\t\t\t\t\t\t\tif (btn.includeWith) {\n
\t\t\t\t\t\t\t\t\t\tbutton.bind(name, func);\n
\t\t\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\t\t\tbutton.bind(name, function() {\n
\t\t\t\t\t\t\t\t\t\t\tif (toolButtonClick(button)) {\n
\t\t\t\t\t\t\t\t\t\t\t\tfunc();\n
\t\t\t\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\t\t\t});\n
\t\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\t\tif (btn.key) {\n
\t\t\t\t\t\t\t\t\t\t$(document).bind(\'keydown\', btn.key, func);\n
\t\t\t\t\t\t\t\t\t\tif (btn.title) {\n
\t\t\t\t\t\t\t\t\t\t\tbutton.attr(\'title\', btn.title + \' [\'+btn.key+\']\');\n
\t\t\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\t\tbutton.bind(name, func);\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t});\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tsetupFlyouts(holders);\n
\t\t\t\t\t});\n
\n
\t\t\t\t\t$.each(btn_selects, function() {\n
\t\t\t\t\t\taddAltDropDown(this.elem, this.list, this.callback, {seticon: true});\n
\t\t\t\t\t});\n
\n
\t\t\t\t\tif (svgicons) {\n
\t\t\t\t\t\tcb_ready = false; // Delay callback\n
\t\t\t\t\t}\n
\n
\t\t\t\t\t$.svgIcons(svgicons, {\n
\t\t\t\t\t\tw: 24, h: 24,\n
\t\t\t\t\t\tid_match: false,\n
\t\t\t\t\t\tno_img: (!svgedit.browser.isWebkit()),\n
\t\t\t\t\t\tfallback: fallback_obj,\n
\t\t\t\t\t\tplacement: placement_obj,\n
\t\t\t\t\t\tcallback: function (icons) {\n
\t\t\t\t\t\t\t// Non-ideal hack to make the icon match the current size\n
\t\t\t\t\t\t\t//if (curPrefs.iconsize && curPrefs.iconsize !== \'m\') {\n
\t\t\t\t\t\t\tif ($.pref(\'iconsize\') !== \'m\') {\n
\t\t\t\t\t\t\t\tprepResize();\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\tcb_ready = true; // Ready for callback\n
\t\t\t\t\t\t\trunCallback();\n
\t\t\t\t\t\t}\n
\t\t\t\t\t});\n
\t\t\t\t}\n
\n
\t\t\t\trunCallback();\n
\t\t\t};\n
\n
\t\t\tvar getPaint = function(color, opac, type) {\n
\t\t\t\t// update the editor\'s fill paint\n
\t\t\t\tvar opts = { alpha: opac };\n
\t\t\t\tif (color.indexOf(\'url(#\') === 0) {\n
\t\t\t\t\tvar refElem = svgCanvas.getRefElem(color);\n
\t\t\t\t\tif (refElem) {\n
\t\t\t\t\t\trefElem = refElem.cloneNode(true);\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\trefElem = $(\'#\' + type + \'_color defs *\')[0];\n
\t\t\t\t\t}\n
\t\t\t\t\topts[refElem.tagName] = refElem;\n
\t\t\t\t} else if (color.indexOf(\'#\') === 0) {\n
\t\t\t\t\topts.solidColor = color.substr(1);\n
\t\t\t\t} else {\n
\t\t\t\t\topts.solidColor = \'none\';\n
\t\t\t\t}\n
\t\t\t\treturn new $.jGraduate.Paint(opts);\n
\t\t\t};\n
\n
\t\t\t$(\'#text\').focus( function(){ textBeingEntered = true; } );\n
\t\t\t$(\'#text\').blur( function(){ textBeingEntered = false; } );\n
\n
\t\t\t// bind the selected event to our function that handles updates to the UI\n
\t\t\tsvgCanvas.bind(\'selected\', selectedChanged);\n
\t\t\tsvgCanvas.bind(\'transition\', elementTransition);\n
\t\t\tsvgCanvas.bind(\'changed\', elementChanged);\n
\t\t\tsvgCanvas.bind(\'saved\', saveHandler);\n
\t\t\tsvgCanvas.bind(\'exported\', exportHandler);\n
\t\t\tsvgCanvas.bind(\'zoomed\', zoomChanged);\n
\t\t\tsvgCanvas.bind(\'contextset\', contextChanged);\n
\t\t\tsvgCanvas.bind(\'extension_added\', extAdded);\n
\t\t\tsvgCanvas.textActions.setInputElem($(\'#text\')[0]);\n
\n
\t\t\tvar str = \'<div class="palette_item" data-rgb="none"></div>\';\n
\t\t\t$.each(palette, function(i, item) {\n
\t\t\t\tstr += \'<div class="palette_item" style="background-color: \' + item + \';" data-rgb="\' + item + \'"></div>\';\n
\t\t\t});\n
\t\t\t$(\'#palette\').append(str);\n
\n
\t\t\t// Set up editor background functionality\n
\t\t\t// TODO add checkerboard as "pattern"\n
\t\t\tvar color_blocks = [\'#FFF\', \'#888\', \'#000\']; // ,\'url(data:image/gif;base64,R0lGODlhEAAQAIAAAP%2F%2F%2F9bW1iH5BAAAAAAALAAAAAAQABAAAAIfjG%2Bgq4jM3IFLJgpswNly%2FXkcBpIiVaInlLJr9FZWAQA7)\'];\n
\t\t\tstr = \'\';\n
\t\t\t$.each(color_blocks, function() {\n
\t\t\t\tstr += \'<div class="color_block" style="background-color:\' + this + \';"></div>\';\n
\t\t\t});\n
\t\t\t$(\'#bg_blocks\').append(str);\n
\t\t\tvar blocks = $(\'#bg_blocks div\');\n
\t\t\tvar cur_bg = \'cur_background\';\n
\t\t\tblocks.each(function() {\n
\t\t\t\tvar blk = $(this);\n
\t\t\t\tblk.click(function() {\n
\t\t\t\t\tblocks.removeClass(cur_bg);\n
\t\t\t\t\t$(this).addClass(cur_bg);\n
\t\t\t\t});\n
\t\t\t});\n
\n
\t\t\tsetBackground($.pref(\'bkgd_color\'), $.pref(\'bkgd_url\'));\n
\n
\t\t\t$(\'#image_save_opts input\').val([$.pref(\'img_save\')]);\n
\n
\t\t\tvar changeRectRadius = function(ctl) {\n
\t\t\t\tsvgCanvas.setRectRadius(ctl.value);\n
\t\t\t};\n
\n
\t\t\tvar changeFontSize = function(ctl) {\n
\t\t\t\tsvgCanvas.setFontSize(ctl.value);\n
\t\t\t};\n
\n
\t\t\tvar changeStrokeWidth = function(ctl) {\n
\t\t\t\tvar val = ctl.value;\n
\t\t\t\tif (val == 0 && selectedElement && [\'line\', \'polyline\'].indexOf(selectedElement.nodeName) >= 0) {\n
\t\t\t\t\tval = ctl.value = 1;\n
\t\t\t\t}\n
\t\t\t\tsvgCanvas.setStrokeWidth(val);\n
\t\t\t};\n
\n
\t\t\tvar changeRotationAngle = function(ctl) {\n
\t\t\t\tsvgCanvas.setRotationAngle(ctl.value);\n
\t\t\t\t$(\'#tool_reorient\').toggleClass(\'disabled\', parseInt(ctl.value, 10) === 0);\n
\t\t\t};\n
\t\t\t\n
\t\t\tvar changeOpacity = function(ctl, val) {\n
\t\t\t\tif (val == null) {val = ctl.value;}\n
\t\t\t\t$(\'#group_opacity\').val(val);\n
\t\t\t\tif (!ctl || !ctl.handle) {\n
\t\t\t\t\t$(\'#opac_slider\').slider(\'option\', \'value\', val);\n
\t\t\t\t}\n
\t\t\t\tsvgCanvas.setOpacity(val/100);\n
\t\t\t};\n
\n
\t\t\tvar changeBlur = function(ctl, val, noUndo) {\n
\t\t\t\tif (val == null) {val = ctl.value;}\n
\t\t\t\t$(\'#blur\').val(val);\n
\t\t\t\tvar complete = false;\n
\t\t\t\tif (!ctl || !ctl.handle) {\n
\t\t\t\t\t$(\'#blur_slider\').slider(\'option\', \'value\', val);\n
\t\t\t\t\tcomplete = true;\n
\t\t\t\t}\n
\t\t\t\tif (noUndo) {\n
\t\t\t\t\tsvgCanvas.setBlurNoUndo(val);\n
\t\t\t\t} else {\n
\t\t\t\t\tsvgCanvas.setBlur(val, complete);\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\t$(\'#stroke_style\').change(function() {\n
\t\t\t\tsvgCanvas.setStrokeAttr(\'stroke-dasharray\', $(this).val());\n
\t\t\t\toperaRepaint();\n
\t\t\t});\n
\n
\t\t\t$(\'#stroke_linejoin\').change(function() {\n
\t\t\t\tsvgCanvas.setStrokeAttr(\'stroke-linejoin\', $(this).val());\n
\t\t\t\toperaRepaint();\n
\t\t\t});\n
\n
\t\t\t// Lose focus for select elements when changed (Allows keyboard shortcuts to work better)\n
\t\t\t$(\'select\').change(function(){$(this).blur();});\n
\n
\t\t\t// fired when user wants to move elements to another layer\n
\t\t\tvar promptMoveLayerOnce = false;\n
\t\t\t$(\'#selLayerNames\').change(function() {\n
\t\t\t\tvar destLayer = this.options[this.selectedIndex].value;\n
\t\t\t\tvar confirmStr = uiStrings.notification.QmoveElemsToLayer.replace(\'%s\', destLayer);\n
\t\t\t\tvar moveToLayer = function(ok) {\n
\t\t\t\t\tif (!ok) {return;}\n
\t\t\t\t\tpromptMoveLayerOnce = true;\n
\t\t\t\t\tsvgCanvas.moveSelectedToLayer(destLayer);\n
\t\t\t\t\tsvgCanvas.clearSelection();\n
\t\t\t\t\tpopulateLayers();\n
\t\t\t\t};\n
\t\t\t\tif (destLayer) {\n
\t\t\t\t\tif (promptMoveLayerOnce) {\n
\t\t\t\t\t\tmoveToLayer(true);\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\t$.confirm(confirmStr, moveToLayer);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t});\n
\n
\t\t\t$(\'#font_family\').change(function() {\n
\t\t\t\tsvgCanvas.setFontFamily(this.value);\n
\t\t\t});\n
\n
\t\t\t$(\'#seg_type\').change(function() {\n
\t\t\t\tsvgCanvas.setSegType($(this).val());\n
\t\t\t});\n
\n
\t\t\t$(\'#text\').keyup(function() {\n
\t\t\t\tsvgCanvas.setTextContent(this.value);\n
\t\t\t});\n
\n
\t\t\t$(\'#image_url\').change(functi

]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAM=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="3" aka="AAAAAAAAAAM=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

on() {\n
\t\t\t\tsetImageURL(this.value);\n
\t\t\t});\n
\n
\t\t\t$(\'#link_url\').change(function() {\n
\t\t\t\tif (this.value.length) {\n
\t\t\t\t\tsvgCanvas.setLinkURL(this.value);\n
\t\t\t\t} else {\n
\t\t\t\t\tsvgCanvas.removeHyperlink();\n
\t\t\t\t}\n
\t\t\t});\n
\n
\t\t\t$(\'#g_title\').change(function() {\n
\t\t\t\tsvgCanvas.setGroupTitle(this.value);\n
\t\t\t});\n
\n
\t\t\t$(\'.attr_changer\').change(function() {\n
\t\t\t\tvar attr = this.getAttribute(\'data-attr\');\n
\t\t\t\tvar val = this.value;\n
\t\t\t\tvar valid = svgedit.units.isValidUnit(attr, val, selectedElement);\n
\n
\t\t\t\tif (!valid) {\n
\t\t\t\t\t$.alert(uiStrings.notification.invalidAttrValGiven);\n
\t\t\t\t\tthis.value = selectedElement.getAttribute(attr);\n
\t\t\t\t\treturn false;\n
\t\t\t\t}\n
\n
\t\t\t\tif (attr !== \'id\') {\n
\t\t\t\t\tif (isNaN(val)) {\n
\t\t\t\t\t\tval = svgCanvas.convertToNum(attr, val);\n
\t\t\t\t\t} else if (curConfig.baseUnit !== \'px\') {\n
\t\t\t\t\t\t// Convert unitless value to one with given unit\n
\n
\t\t\t\t\t\tvar unitData = svgedit.units.getTypeMap();\n
\n
\t\t\t\t\t\tif (selectedElement[attr] || svgCanvas.getMode() === \'pathedit\' || attr === \'x\' || attr === \'y\') {\n
\t\t\t\t\t\t\tval *= unitData[curConfig.baseUnit];\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\t// if the user is changing the id, then de-select the element first\n
\t\t\t\t// change the ID, then re-select it with the new ID\n
\t\t\t\tif (attr === \'id\') {\n
\t\t\t\t\tvar elem = selectedElement;\n
\t\t\t\t\tsvgCanvas.clearSelection();\n
\t\t\t\t\telem.id = val;\n
\t\t\t\t\tsvgCanvas.addToSelection([elem],true);\n
\t\t\t\t} else {\n
\t\t\t\t\tsvgCanvas.changeSelectedAttribute(attr, val);\n
\t\t\t\t}\n
\t\t\t\tthis.blur();\n
\t\t\t});\n
\n
\t\t\t// Prevent selection of elements when shift-clicking\n
\t\t\t$(\'#palette\').mouseover(function() {\n
\t\t\t\tvar inp = $(\'<input type="hidden">\');\n
\t\t\t\t$(this).append(inp);\n
\t\t\t\tinp.focus().remove();\n
\t\t\t});\n
\n
\t\t\t$(\'.palette_item\').mousedown(function(evt) {\n
\t\t\t\t// shift key or right click for stroke\n
\t\t\t\tvar picker = evt.shiftKey || evt.button === 2 ? \'stroke\' : \'fill\';\n
\t\t\t\tvar color = $(this).data(\'rgb\');\n
\t\t\t\tvar paint;\n
\n
\t\t\t\t// Webkit-based browsers returned \'initial\' here for no stroke\n
\t\t\t\tif (color === \'none\' || color === \'transparent\' || color === \'initial\') {\n
\t\t\t\t\tcolor = \'none\';\n
\t\t\t\t\tpaint = new $.jGraduate.Paint();\n
\t\t\t\t} else {\n
\t\t\t\t\tpaint = new $.jGraduate.Paint({alpha: 100, solidColor: color.substr(1)});\n
\t\t\t\t}\n
\n
\t\t\t\tpaintBox[picker].setPaint(paint);\n
\t\t\t\tsvgCanvas.setColor(picker, color);\n
\n
\t\t\t\tif (color !== \'none\' && svgCanvas.getPaintOpacity(picker) !== 1) {\n
\t\t\t\t\tsvgCanvas.setPaintOpacity(picker, 1.0);\n
\t\t\t\t}\n
\t\t\t\tupdateToolButtonState();\n
\t\t\t}).bind(\'contextmenu\', function(e) {e.preventDefault();});\n
\n
\t\t\t$(\'#toggle_stroke_tools\').on(\'click\', function() {\n
\t\t\t\t$(\'#tools_bottom\').toggleClass(\'expanded\');\n
\t\t\t});\n
\n
\t\t\t(function() {\n
\t\t\t\tvar last_x = null, last_y = null, w_area = workarea[0],\n
\t\t\t\t\tpanning = false, keypan = false;\n
\n
\t\t\t\t$(\'#svgcanvas\').bind(\'mousemove mouseup\', function(evt) {\n
\t\t\t\t\tif (panning === false) {return;}\n
\n
\t\t\t\t\tw_area.scrollLeft -= (evt.clientX - last_x);\n
\t\t\t\t\tw_area.scrollTop -= (evt.clientY - last_y);\n
\n
\t\t\t\t\tlast_x = evt.clientX;\n
\t\t\t\t\tlast_y = evt.clientY;\n
\n
\t\t\t\t\tif (evt.type === \'mouseup\') {panning = false;}\n
\t\t\t\t\treturn false;\n
\t\t\t\t}).mousedown(function(evt) {\n
\t\t\t\t\tif (evt.button === 1 || keypan === true) {\n
\t\t\t\t\t\tpanning = true;\n
\t\t\t\t\t\tlast_x = evt.clientX;\n
\t\t\t\t\t\tlast_y = evt.clientY;\n
\t\t\t\t\t\treturn false;\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\n
\t\t\t\t$(window).mouseup(function() {\n
\t\t\t\t\tpanning = false;\n
\t\t\t\t});\n
\n
\t\t\t\t$(document).bind(\'keydown\', \'space\', function(evt) {\n
\t\t\t\t\tsvgCanvas.spaceKey = keypan = true;\n
\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t}).bind(\'keyup\', \'space\', function(evt) {\n
\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t\tsvgCanvas.spaceKey = keypan = false;\n
\t\t\t\t}).bind(\'keydown\', \'shift\', function(evt) {\n
\t\t\t\t\tif (svgCanvas.getMode() === \'zoom\') {\n
\t\t\t\t\t\tworkarea.css(\'cursor\', zoomOutIcon);\n
\t\t\t\t\t}\n
\t\t\t\t}).bind(\'keyup\', \'shift\', function(evt) {\n
\t\t\t\t\tif (svgCanvas.getMode() === \'zoom\') {\n
\t\t\t\t\t\tworkarea.css(\'cursor\', zoomInIcon);\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\n
\t\t\t\teditor.setPanning = function(active) {\n
\t\t\t\t\tsvgCanvas.spaceKey = keypan = active;\n
\t\t\t\t};\n
\t\t\t}());\n
\n
\t\t\t(function () {\n
\t\t\t\tvar button = $(\'#main_icon\');\n
\t\t\t\tvar overlay = $(\'#main_icon span\');\n
\t\t\t\tvar list = $(\'#main_menu\');\n
\t\t\t\tvar on_button = false;\n
\t\t\t\tvar height = 0;\n
\t\t\t\tvar js_hover = true;\n
\t\t\t\tvar set_click = false;\n
\n
\t\t\t\t/*\n
\t\t\t\t// Currently unused\n
\t\t\t\tvar hideMenu = function() {\n
\t\t\t\t\tlist.fadeOut(200);\n
\t\t\t\t};\n
\t\t\t\t*/\n
\n
\t\t\t\t$(window).mouseup(function(evt) {\n
\t\t\t\t\tif (!on_button) {\n
\t\t\t\t\t\tbutton.removeClass(\'buttondown\');\n
\t\t\t\t\t\t// do not hide if it was the file input as that input needs to be visible\n
\t\t\t\t\t\t// for its change event to fire\n
\t\t\t\t\t\tif (evt.target.tagName != \'INPUT\') {\n
\t\t\t\t\t\t\tlist.fadeOut(200);\n
\t\t\t\t\t\t} else if (!set_click) {\n
\t\t\t\t\t\t\tset_click = true;\n
\t\t\t\t\t\t\t$(evt.target).click(function() {\n
\t\t\t\t\t\t\t\tlist.css(\'margin-left\', \'-9999px\').show();\n
\t\t\t\t\t\t\t});\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\ton_button = false;\n
\t\t\t\t}).mousedown(function(evt) {\n
//\t\t\t\t\t$(\'.contextMenu\').hide();\n
\t\t\t\t\tvar islib = $(evt.target).closest(\'div.tools_flyout, .contextMenu\').length;\n
\t\t\t\t\tif (!islib) {$(\'.tools_flyout:visible,.contextMenu\').fadeOut(250);}\n
\t\t\t\t});\n
\n
\t\t\t\toverlay.bind(\'mousedown\',function() {\n
\t\t\t\t\tif (!button.hasClass(\'buttondown\')) {\n
\t\t\t\t\t\t// Margin must be reset in case it was changed before;\n
\t\t\t\t\t\tlist.css(\'margin-left\', 0).show();\n
\t\t\t\t\t\tif (!height) {\n
\t\t\t\t\t\t\theight = list.height();\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t// Using custom animation as slideDown has annoying \'bounce effect\'\n
\t\t\t\t\t\tlist.css(\'height\',0).animate({\n
\t\t\t\t\t\t\t\'height\': height\n
\t\t\t\t\t\t}, 200);\n
\t\t\t\t\t\ton_button = true;\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tlist.fadeOut(200);\n
\t\t\t\t\t}\n
\t\t\t\t\tbutton.toggleClass(\'buttondown buttonup\');\n
\t\t\t\t}).hover(function() {\n
\t\t\t\t\ton_button = true;\n
\t\t\t\t}).mouseout(function() {\n
\t\t\t\t\ton_button = false;\n
\t\t\t\t});\n
\n
\t\t\t\tvar list_items = $(\'#main_menu li\');\n
\n
\t\t\t\t// Check if JS method of hovering needs to be used (Webkit bug)\n
\t\t\t\tlist_items.mouseover(function() {\n
\t\t\t\t\tjs_hover = ($(this).css(\'background-color\') == \'rgba(0, 0, 0, 0)\');\n
\n
\t\t\t\t\tlist_items.unbind(\'mouseover\');\n
\t\t\t\t\tif (js_hover) {\n
\t\t\t\t\t\tlist_items.mouseover(function() {\n
\t\t\t\t\t\t\tthis.style.backgroundColor = \'#FFC\';\n
\t\t\t\t\t\t}).mouseout(function() {\n
\t\t\t\t\t\t\tthis.style.backgroundColor = \'transparent\';\n
\t\t\t\t\t\t\treturn true;\n
\t\t\t\t\t\t});\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t}());\n
\t\t\t// Made public for UI customization.\n
\t\t\t// TODO: Group UI functions into a public svgEditor.ui interface.\n
\t\t\teditor.addDropDown = function(elem, callback, dropUp) {\n
\t\t\t\tif ($(elem).length == 0) {return;} // Quit if called on non-existant element\n
\t\t\t\tvar button = $(elem).find(\'button\');\n
\t\t\t\tvar list = $(elem).find(\'ul\').attr(\'id\', $(elem)[0].id + \'-list\');\n
\t\t\t\tvar on_button = false;\n
\t\t\t\tif (dropUp) {\n
\t\t\t\t\t$(elem).addClass(\'dropup\');\n
\t\t\t\t} else {\n
\t\t\t\t\t// Move list to place where it can overflow container\n
\t\t\t\t\t$(\'#option_lists\').append(list);\n
\t\t\t\t}\n
\t\t\t\tlist.find(\'li\').bind(\'mouseup\', callback);\n
\n
\t\t\t\t$(window).mouseup(function(evt) {\n
\t\t\t\t\tif (!on_button) {\n
\t\t\t\t\t\tbutton.removeClass(\'down\');\n
\t\t\t\t\t\tlist.hide();\n
\t\t\t\t\t}\n
\t\t\t\t\ton_button = false;\n
\t\t\t\t});\n
\n
\t\t\t\tbutton.bind(\'mousedown\',function() {\n
\t\t\t\t\tif (!button.hasClass(\'down\')) {\n
\t\t\t\t\t\tif (!dropUp) {\n
\t\t\t\t\t\t\tvar pos = $(elem).position();\n
\t\t\t\t\t\t\tlist.css({\n
\t\t\t\t\t\t\t\ttop: pos.top + 24,\n
\t\t\t\t\t\t\t\tleft: pos.left - 10\n
\t\t\t\t\t\t\t});\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tlist.show();\n
\t\t\t\t\t\ton_button = true;\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tlist.hide();\n
\t\t\t\t\t}\n
\t\t\t\t\tbutton.toggleClass(\'down\');\n
\t\t\t\t}).hover(function() {\n
\t\t\t\t\ton_button = true;\n
\t\t\t\t}).mouseout(function() {\n
\t\t\t\t\ton_button = false;\n
\t\t\t\t});\n
\t\t\t};\n
\n
\t\t\teditor.addDropDown(\'#font_family_dropdown\', function() {\n
\t\t\t\t$(\'#font_family\').val($(this).text()).change();\n
\t\t\t});\n
\n
\t\t\teditor.addDropDown(\'#opacity_dropdown\', function() {\n
\t\t\t\tif ($(this).find(\'div\').length) {return;}\n
\t\t\t\tvar perc = parseInt($(this).text().split(\'%\')[0], 10);\n
\t\t\t\tchangeOpacity(false, perc);\n
\t\t\t}, true);\n
\n
\t\t\t// For slider usage, see: http://jqueryui.com/demos/slider/\n
\t\t\t$(\'#opac_slider\').slider({\n
\t\t\t\tstart: function() {\n
\t\t\t\t\t$(\'#opacity_dropdown li:not(.special)\').hide();\n
\t\t\t\t},\n
\t\t\t\tstop: function() {\n
\t\t\t\t\t$(\'#opacity_dropdown li\').show();\n
\t\t\t\t\t$(window).mouseup();\n
\t\t\t\t},\n
\t\t\t\tslide: function(evt, ui) {\n
\t\t\t\t\tchangeOpacity(ui);\n
\t\t\t\t}\n
\t\t\t});\n
\n
\t\t\teditor.addDropDown(\'#blur_dropdown\', $.noop);\n
\n
\t\t\tvar slideStart = false;\n
\n
\t\t\t$(\'#blur_slider\').slider({\n
\t\t\t\tmax: 10,\n
\t\t\t\tstep: 0.1,\n
\t\t\t\tstop: function(evt, ui) {\n
\t\t\t\t\tslideStart = false;\n
\t\t\t\t\tchangeBlur(ui);\n
\t\t\t\t\t$(\'#blur_dropdown li\').show();\n
\t\t\t\t\t$(window).mouseup();\n
\t\t\t\t},\n
\t\t\t\tstart: function() {\n
\t\t\t\t\tslideStart = true;\n
\t\t\t\t},\n
\t\t\t\tslide: function(evt, ui) {\n
\t\t\t\t\tchangeBlur(ui, null, slideStart);\n
\t\t\t\t}\n
\t\t\t});\n
\n
\t\t\teditor.addDropDown(\'#zoom_dropdown\', function() {\n
\t\t\t\tvar item = $(this);\n
\t\t\t\tvar val = item.data(\'val\');\n
\t\t\t\tif (val) {\n
\t\t\t\t\tzoomChanged(window, val);\n
\t\t\t\t} else {\n
\t\t\t\t\tchangeZoom({value: parseInt(item.text(), 10)});\n
\t\t\t\t}\n
\t\t\t}, true);\n
\n
\t\t\taddAltDropDown(\'#stroke_linecap\', \'#linecap_opts\', function() {\n
\t\t\t\tsetStrokeOpt(this, true);\n
\t\t\t}, {dropUp: true});\n
\n
\t\t\taddAltDropDown(\'#stroke_linejoin\', \'#linejoin_opts\', function() {\n
\t\t\t\tsetStrokeOpt(this, true);\n
\t\t\t}, {dropUp: true});\n
\n
\t\t\taddAltDropDown(\'#tool_position\', \'#position_opts\', function() {\n
\t\t\t\tvar letter = this.id.replace(\'tool_pos\', \'\').charAt(0);\n
\t\t\t\tsvgCanvas.alignSelectedElements(letter, \'page\');\n
\t\t\t}, {multiclick: true});\n
\n
\t\t\t/*\n
\n
\t\t\tWhen a flyout icon is selected\n
\t\t\t\t(if flyout) {\n
\t\t\t\t- Change the icon\n
\t\t\t\t- Make pressing the button run its stuff\n
\t\t\t\t}\n
\t\t\t\t- Run its stuff\n
\n
\t\t\tWhen its shortcut key is pressed\n
\t\t\t\t- If not current in list, do as above\n
\t\t\t\t, else:\n
\t\t\t\t- Just run its stuff\n
\n
\t\t\t*/\n
\n
\t\t\t// Unfocus text input when workarea is mousedowned.\n
\t\t\t(function() {\n
\t\t\t\tvar inp;\n
\t\t\t\tvar unfocus = function() {\n
\t\t\t\t\t$(inp).blur();\n
\t\t\t\t};\n
\n
\t\t\t\t$(\'#svg_editor\').find(\'button, select, input:not(#text)\').focus(function() {\n
\t\t\t\t\tinp = this;\n
\t\t\t\t\tui_context = \'toolbars\';\n
\t\t\t\t\tworkarea.mousedown(unfocus);\n
\t\t\t\t}).blur(function() {\n
\t\t\t\t\tui_context = \'canvas\';\n
\t\t\t\t\tworkarea.unbind(\'mousedown\', unfocus);\n
\t\t\t\t\t// Go back to selecting text if in textedit mode\n
\t\t\t\t\tif (svgCanvas.getMode() == \'textedit\') {\n
\t\t\t\t\t\t$(\'#text\').focus();\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t}());\n
\n
\t\t\tvar clickFHPath = function() {\n
\t\t\t\tif (toolButtonClick(\'#tool_fhpath\')) {\n
\t\t\t\t\tsvgCanvas.setMode(\'fhpath\');\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar clickLine = function() {\n
\t\t\t\tif (toolButtonClick(\'#tool_line\')) {\n
\t\t\t\t\tsvgCanvas.setMode(\'line\');\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar clickSquare = function() {\n
\t\t\t\tif (toolButtonClick(\'#tool_square\')) {\n
\t\t\t\t\tsvgCanvas.setMode(\'square\');\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar clickRect = function() {\n
\t\t\t\tif (toolButtonClick(\'#tool_rect\')) {\n
\t\t\t\t\tsvgCanvas.setMode(\'rect\');\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar clickFHRect = function() {\n
\t\t\t\tif (toolButtonClick(\'#tool_fhrect\')) {\n
\t\t\t\t\tsvgCanvas.setMode(\'fhrect\');\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar clickCircle = function() {\n
\t\t\t\tif (toolButtonClick(\'#tool_circle\')) {\n
\t\t\t\t\tsvgCanvas.setMode(\'circle\');\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar clickEllipse = function() {\n
\t\t\t\tif (toolButtonClick(\'#tool_ellipse\')) {\n
\t\t\t\t\tsvgCanvas.setMode(\'ellipse\');\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar clickFHEllipse = function() {\n
\t\t\t\tif (toolButtonClick(\'#tool_fhellipse\')) {\n
\t\t\t\t\tsvgCanvas.setMode(\'fhellipse\');\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar clickImage = function() {\n
\t\t\t\tif (toolButtonClick(\'#tool_image\')) {\n
\t\t\t\t\tsvgCanvas.setMode(\'image\');\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar clickZoom = function() {\n
\t\t\t\tif (toolButtonClick(\'#tool_zoom\')) {\n
\t\t\t\t\tsvgCanvas.setMode(\'zoom\');\n
\t\t\t\t\tworkarea.css(\'cursor\', zoomInIcon);\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar zoomImage = function(multiplier) {\n
\t\t\t\tvar res = svgCanvas.getResolution();\n
\t\t\t\tmultiplier = multiplier ? res.zoom * multiplier : 1;\n
\t\t\t\t// setResolution(res.w * multiplier, res.h * multiplier, true);\n
\t\t\t\t$(\'#zoom\').val(multiplier * 100);\n
\t\t\t\tsvgCanvas.setZoom(multiplier);\n
\t\t\t\tzoomDone();\n
\t\t\t\tupdateCanvas(true);\n
\t\t\t};\n
\n
\t\t\tvar dblclickZoom = function() {\n
\t\t\t\tif (toolButtonClick(\'#tool_zoom\')) {\n
\t\t\t\t\tzoomImage();\n
\t\t\t\t\tsetSelectMode();\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar clickText = function() {\n
\t\t\t\tif (toolButtonClick(\'#tool_text\')) {\n
\t\t\t\t\tsvgCanvas.setMode(\'text\');\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar clickPath = function() {\n
\t\t\t\tif (toolButtonClick(\'#tool_path\')) {\n
\t\t\t\t\tsvgCanvas.setMode(\'path\');\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\t// Delete is a contextual tool that only appears in the ribbon if\n
\t\t\t// an element has been selected\n
\t\t\tvar deleteSelected = function() {\n
\t\t\t\tif (selectedElement != null || multiselected) {\n
\t\t\t\t\tsvgCanvas.deleteSelectedElements();\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar cutSelected = function() {\n
\t\t\t\tif (selectedElement != null || multiselected) {\n
\t\t\t\t\tsvgCanvas.cutSelectedElements();\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar copySelected = function() {\n
\t\t\t\tif (selectedElement != null || multiselected) {\n
\t\t\t\t\tsvgCanvas.copySelectedElements();\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar pasteInCenter = function() {\n
\t\t\t\tvar zoom = svgCanvas.getZoom();\n
\t\t\t\tvar x = (workarea[0].scrollLeft + workarea.width()/2)/zoom - svgCanvas.contentW;\n
\t\t\t\tvar y = (workarea[0].scrollTop + workarea.height()/2)/zoom - svgCanvas.contentH;\n
\t\t\t\tsvgCanvas.pasteElements(\'point\', x, y);\n
\t\t\t};\n
\n
\t\t\tvar moveToTopSelected = function() {\n
\t\t\t\tif (selectedElement != null) {\n
\t\t\t\t\tsvgCanvas.moveToTopSelectedElement();\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar moveToBottomSelected = function() {\n
\t\t\t\tif (selectedElement != null) {\n
\t\t\t\t\tsvgCanvas.moveToBottomSelectedElement();\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar moveUpDownSelected = function(dir) {\n
\t\t\t\tif (selectedElement != null) {\n
\t\t\t\t\tsvgCanvas.moveUpDownSelected(dir);\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar convertToPath = function() {\n
\t\t\t\tif (selectedElement != null) {\n
\t\t\t\t\tsvgCanvas.convertToPath();\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar reorientPath = function() {\n
\t\t\t\tif (selectedElement != null) {\n
\t\t\t\t\tpath.reorient();\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar makeHyperlink = function() {\n
\t\t\t\tif (selectedElement != null || multiselected) {\n
\t\t\t\t\t$.prompt(uiStrings.notification.enterNewLinkURL, \'http://\', function(url) {\n
\t\t\t\t\t\tif (url) {svgCanvas.makeHyperlink(url);}\n
\t\t\t\t\t});\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar moveSelected = function(dx,dy) {\n
\t\t\t\tif (selectedElement != null || multiselected) {\n
\t\t\t\t\tif (curConfig.gridSnapping) {\n
\t\t\t\t\t\t// Use grid snap value regardless of zoom level\n
\t\t\t\t\t\tvar multi = svgCanvas.getZoom() * curConfig.snappingStep;\n
\t\t\t\t\t\tdx *= multi;\n
\t\t\t\t\t\tdy *= multi;\n
\t\t\t\t\t}\n
\t\t\t\t\tsvgCanvas.moveSelectedElements(dx,dy);\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar linkControlPoints = function() {\n
\t\t\t\t$(\'#tool_node_link\').toggleClass(\'push_button_pressed tool_button\');\n
\t\t\t\tvar linked = $(\'#tool_node_link\').hasClass(\'push_button_pressed\');\n
\t\t\t\tpath.linkControlPoints(linked);\n
\t\t\t};\n
\n
\t\t\tvar clonePathNode = function() {\n
\t\t\t\tif (path.getNodePoint()) {\n
\t\t\t\t\tpath.clonePathNode();\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar deletePathNode = function() {\n
\t\t\t\tif (path.getNodePoint()) {\n
\t\t\t\t\tpath.deletePathNode();\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar addSubPath = function() {\n
\t\t\t\tvar button = $(\'#tool_add_subpath\');\n
\t\t\t\tvar sp = !button.hasClass(\'push_button_pressed\');\n
\t\t\t\tbutton.toggleClass(\'push_button_pressed tool_button\');\n
\t\t\t\tpath.addSubPath(sp);\n
\t\t\t};\n
\n
\t\t\tvar opencloseSubPath = function() {\n
\t\t\t\tpath.opencloseSubPath();\n
\t\t\t};\n
\n
\t\t\tvar selectNext = function() {\n
\t\t\t\tsvgCanvas.cycleElement(1);\n
\t\t\t};\n
\n
\t\t\tvar selectPrev = function() {\n
\t\t\t\tsvgCanvas.cycleElement(0);\n
\t\t\t};\n
\n
\t\t\tvar rotateSelected = function(cw, step) {\n
\t\t\t\tif (selectedElement == null || multiselected) {return;}\n
\t\t\t\tif (!cw) {step *= -1;}\n
\t\t\t\tvar angle = parseFloat($(\'#angle\').val()) + step;\n
\t\t\t\tsvgCanvas.setRotationAngle(angle);\n
\t\t\t\tupdateContextPanel();\n
\t\t\t};\n
\n
\t\t\tvar clickClear = function() {\n
\t\t\t\tvar dims = curConfig.dimensions;\n
\t\t\t\t$.confirm(uiStrings.notification.QwantToClear, function(ok) {\n
\t\t\t\t\tif (!ok) {return;}\n
\t\t\t\t\tsetSelectMode();\n
\t\t\t\t\tsvgCanvas.clear();\n
\t\t\t\t\tsvgCanvas.setResolution(dims[0], dims[1]);\n
\t\t\t\t\tupdateCanvas(true);\n
\t\t\t\t\tzoomImage();\n
\t\t\t\t\tpopulateLayers();\n
\t\t\t\t\tupdateContextPanel();\n
\t\t\t\t\tprepPaints();\n
\t\t\t\t\tsvgCanvas.runExtensions(\'onNewDocument\');\n
\t\t\t\t});\n
\t\t\t};\n
\n
\t\t\tvar clickBold = function() {\n
\t\t\t\tsvgCanvas.setBold( !svgCanvas.getBold() );\n
\t\t\t\tupdateContextPanel();\n
\t\t\t\treturn false;\n
\t\t\t};\n
\n
\t\t\tvar clickItalic = function() {\n
\t\t\t\tsvgCanvas.setItalic( !svgCanvas.getItalic() );\n
\t\t\t\tupdateContextPanel();\n
\t\t\t\treturn false;\n
\t\t\t};\n
\n
\t\t\tvar clickSave = function() {\n
\t\t\t\t// In the future, more options can be provided here\n
\t\t\t\tvar saveOpts = {\n
\t\t\t\t\t\'images\': $.pref(\'img_save\'),\n
\t\t\t\t\t\'round_digits\': 6\n
\t\t\t\t};\n
\t\t\t\tsvgCanvas.save(saveOpts);\n
\t\t\t};\n
\n
\t\t\tvar clickExport = function() {\n
\t\t\t\t$.select(\'Select an image type for export: \', [\n
\t\t\t\t\t// See http://kangax.github.io/jstests/toDataUrl_mime_type_test/ for a useful list of MIME types and browser support\n
\t\t\t\t\t// \'ICO\', // Todo: Find a way to preserve transparency in SVG-Edit if not working presently and do full packaging for x-icon; then switch back to position after \'PNG\'\n
\t\t\t\t\t\'PNG\',\n
\t\t\t\t\t\'JPEG\', \'BMP\', \'WEBP\'\n
\t\t\t\t], function (imgType) { // todo: replace hard-coded msg with uiStrings.notification.\n
\t\t\t\t\tif (!imgType) {\n
\t\t\t\t\t\treturn;\n
\t\t\t\t\t}\n
\t\t\t\t\t// Open placeholder window (prevents popup)\n
\t\t\t\t\tif (!customHandlers.exportImage && !customHandlers.pngsave) {\n
\t\t\t\t\t\tvar str = uiStrings.notification.loadingImage;\n
\t\t\t\t\t\texportWindow = window.open(\'data:text/html;charset=utf-8,<title>\' + str + \'<\\/title><h1>\' + str + \'<\\/h1>\');\n
\t\t\t\t\t}\n
\t\t\t\t\tvar quality = parseInt($(\'#image-slider\').val(), 10)/100;\n
\t\t\t\t\tif (window.canvg) {\n
\t\t\t\t\t\tsvgCanvas.rasterExport(imgType, quality);\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\t$.getScript(\'canvg/rgbcolor.js\', function() {\n
\t\t\t\t\t\t\t$.getScript(\'canvg/canvg.js\', function() {\n
\t\t\t\t\t\t\t\tsvgCanvas.rasterExport(imgType, quality);\n
\t\t\t\t\t\t\t});\n
\t\t\t\t\t\t});\n
\t\t\t\t\t}\n
\t\t\t\t}, function () {\n
\t\t\t\t\tvar sel = $(this);\n
\t\t\t\t\tif (sel.val() === \'JPEG\' || sel.val() === \'WEBP\') {\n
\t\t\t\t\t\tif (!$(\'#image-slider\').length) {\n
\t\t\t\t\t\t\t$(\'<div><label>Quality: <input id="image-slider" type="range" min="1" max="100" value="92" /></label></div>\').appendTo(sel.parent()); // Todo: i18n-ize label\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\telse {\n
\t\t\t\t\t\t$(\'#image-slider\').parent().remove();\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t};\n
\n
\t\t\t// by default, svgCanvas.open() is a no-op.\n
\t\t\t// it is up to an extension mechanism (opera widget, etc)\n
\t\t\t// to call setCustomHandlers() which will make it do something\n
\t\t\tvar clickOpen = function() {\n
\t\t\t\tsvgCanvas.open();\n
\t\t\t};\n
\n
\t\t\tvar clickImport = function() {\n
\t\t\t};\n
\n
\t\t\tvar clickUndo = function() {\n
\t\t\t\tif (undoMgr.getUndoStackSize() > 0) {\n
\t\t\t\t\tundoMgr.undo();\n
\t\t\t\t\tpopulateLayers();\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar clickRedo = function() {\n
\t\t\t\tif (undoMgr.getRedoStackSize() > 0) {\n
\t\t\t\t\tundoMgr.redo();\n
\t\t\t\t\tpopulateLayers();\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar clickGroup = function() {\n
\t\t\t\t// group\n
\t\t\t\tif (multiselected) {\n
\t\t\t\t\tsvgCanvas.groupSelectedElements();\n
\t\t\t\t}\n
\t\t\t\t// ungroup\n
\t\t\t\telse if (selectedElement) {\n
\t\t\t\t\tsvgCanvas.ungroupSelectedElement();\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tvar clickClone = function() {\n
\t\t\t\tsvgCanvas.cloneSelectedElements(20, 20);\n
\t\t\t};\n
\n
\t\t\tvar clickAlign = function() {\n
\t\t\t\tvar letter = this.id.replace(\'tool_align\', \'\').charAt(0);\n
\t\t\t\tsvgCanvas.alignSelectedElements(letter, $(\'#align_relative_to\').val());\n
\t\t\t};\n
\n
\t\t\tvar clickWireframe = function() {\n
\t\t\t\t$(\'#tool_wireframe\').toggleClass(\'push_button_pressed tool_button\');\n
\t\t\t\tworkarea.toggleClass(\'wireframe\');\n
\n
\t\t\t\tif (supportsNonSS) {return;}\n
\t\t\t\tvar wf_rules = $(\'#wireframe_rules\');\n
\t\t\t\tif (!wf_rules.length) {\n
\t\t\t\t\twf_rules = $(\'<style id="wireframe_rules"><\\/style>\').appendTo(\'head\');\n
\t\t\t\t} else {\n
\t\t\t\t\twf_rules.empty();\n
\t\t\t\t}\n
\n
\t\t\t\tupdateWireFrame();\n
\t\t\t};\n
\n
\t\t\t$(\'#svg_docprops_container, #svg_prefs_container\').draggable({cancel: \'button,fieldset\', containment: \'window\'});\n
\n
\t\t\tvar showDocProperties = function() {\n
\t\t\t\tif (docprops) {return;}\n
\t\t\t\tdocprops = true;\n
\n
\t\t\t\t// This selects the correct radio button by using the array notation\n
\t\t\t\t$(\'#image_save_opts input\').val([$.pref(\'img_save\')]);\n
\n
\t\t\t\t// update resolution option with actual resolution\n
\t\t\t\tvar res = svgCanvas.getResolution();\n
\t\t\t\tif (curConfig.baseUnit !== \'px\') {\n
\t\t\t\t\tres.w = svgedit.units.convertUnit(res.w) + curConfig.baseUnit;\n
\t\t\t\t\tres.h = svgedit.units.convertUnit(res.h) + curConfig.baseUnit;\n
\t\t\t\t}\n
\n
\t\t\t\t$(\'#canvas_width\').val(res.w);\n
\t\t\t\t$(\'#canvas_height\').val(res.h);\n
\t\t\t\t$(\'#canvas_title\').val(svgCanvas.getDocumentTitle());\n
\n
\t\t\t\t$(\'#svg_docprops\').show();\n
\t\t\t};\n
\n
\t\t\tvar showPreferences = function() {\n
\t\t\t\tif (preferences) {return;}\n
\t\t\t\tpreferences = true;\n
\t\t\t\t$(\'#main_menu\').hide();\n
\n
\t\t\t\t// Update background color with current one\n
\t\t\t\tvar blocks = $(\'#bg_blocks div\');\n
\t\t\t\tvar cur_bg = \'cur_background\';\n
\t\t\t\tvar canvas_bg = curPrefs.bkgd_color;\n
\t\t\t\tvar url = $.pref(\'bkgd_url\');\n
\t\t\t\tblocks.each(function() {\n
\t\t\t\t\tvar blk = $(this);\n
\t\t\t\t\tvar is_bg = blk.css(\'background-color\') == canvas_bg;\n
\t\t\t\t\tblk.toggleClass(cur_bg, is_bg);\n
\t\t\t\t\tif (is_bg) {$(\'#canvas_bg_url\').removeClass(cur_bg);}\n
\t\t\t\t});\n
\t\t\t\tif (!canvas_bg) {blocks.eq(0).addClass(cur_bg);}\n
\t\t\t\tif (url) {\n
\t\t\t\t\t$(\'#canvas_bg_url\').val(url);\n
\t\t\t\t}\n
\t\t\t\t$(\'#grid_snapping_on\').prop(\'checked\', curConfig.gridSnapping);\n
\t\t\t\t$(\'#grid_snapping_step\').attr(\'value\', curConfig.snappingStep);\n
\t\t\t\t$(\'#grid_color\').attr(\'value\', curConfig.gridColor);\n
\n
\t\t\t\t$(\'#svg_prefs\').show();\n
\t\t\t};\n
\n
\t\t\tvar hideSourceEditor = function() {\n
\t\t\t\t$(\'#svg_source_editor\').hide();\n
\t\t\t\teditingsource = false;\n
\t\t\t\t$(\'#svg_source_textarea\').blur();\n
\t\t\t};\n
\n
\t\t\tvar saveSourceEditor = function() {\n
\t\t\t\tif (!editingsource) {return;}\n
\n
\t\t\t\tvar saveChanges = function() {\n
\t\t\t\t\tsvgCanvas.clearSelection();\n
\t\t\t\t\thideSourceEditor();\n
\t\t\t\t\tzoomImage();\n
\t\t\t\t\tpopulateLayers();\n
\t\t\t\t\tupdateTitle();\n
\t\t\t\t\tprepPaints();\n
\t\t\t\t};\n
\n
\t\t\t\tif (!svgCanvas.setSvgString($(\'#svg_source_textarea\').val())) {\n
\t\t\t\t\t$.confirm(uiStrings.notification.QerrorsRevertToSource, function(ok) {\n
\t\t\t\t\t\tif (!ok) {return false;}\n
\t\t\t\t\t\tsaveChanges();\n
\t\t\t\t\t});\n
\t\t\t\t} else {\n
\t\t\t\t\tsaveChanges();\n
\t\t\t\t}\n
\t\t\t\tsetSelectMode();\n
\t\t\t};\n
\n
\t\t\tvar hideDocProperties = function() {\n
\t\t\t\t$(\'#svg_docprops\').hide();\n
\t\t\t\t$(\'#canvas_width,#canvas_height\').removeAttr(\'disabled\');\n
\t\t\t\t$(\'#resolution\')[0].selectedIndex = 0;\n
\t\t\t\t$(\'#image_save_opts input\').val([$.pref(\'img_save\')]);\n
\t\t\t\tdocprops = false;\n
\t\t\t};\n
\n
\t\t\tvar hidePreferences = function() {\n
\t\t\t\t$(\'#svg_prefs\').hide();\n
\t\t\t\tpreferences = false;\n
\t\t\t};\n
\n
\t\t\tvar saveDocProperties = function() {\n
\t\t\t\t// set title\n
\t\t\t\tvar newTitle = $(\'#canvas_title\').val();\n
\t\t\t\tupdateTitle(newTitle);\n
\t\t\t\tsvgCanvas.setDocumentTitle(newTitle);\n
\n
\t\t\t\t// update resolution\n
\t\t\t\tvar width = $(\'#canvas_width\'), w = width.val();\n
\t\t\t\tvar height = $(\'#canvas_height\'), h = height.val();\n
\n
\t\t\t\tif (w != \'fit\' && !svgedit.units.isValidUnit(\'width\', w)) {\n
\t\t\t\t\t$.alert(uiStrings.notification.invalidAttrValGiven);\n
\t\t\t\t\twidth.parent().addClass(\'error\');\n
\t\t\t\t\treturn false;\n
\t\t\t\t}\n
\n
\t\t\t\twidth.parent().removeClass(\'error\');\n
\n
\t\t\t\tif (h != \'fit\' && !svgedit.units.isValidUnit(\'height\', h)) {\n
\t\t\t\t\t$.alert(uiStrings.notification.invalidAttrValGiven);\n
\t\t\t\t\theight.parent().addClass(\'error\');\n
\t\t\t\t\treturn false;\n
\t\t\t\t}\n
\n
\t\t\t\theight.parent().removeClass(\'error\');\n
\n
\t\t\t\tif (!svgCanvas.setResolution(w, h)) {\n
\t\t\t\t\t$.alert(uiStrings.notification.noContentToFitTo);\n
\t\t\t\t\treturn false;\n
\t\t\t\t}\n
\n
\t\t\t\t// Set image save option\n
\t\t\t\t$.pref(\'img_save\', $(\'#image_save_opts :checked\').val());\n
\t\t\t\tupdateCanvas();\n
\t\t\t\thideDocProperties();\n
\t\t\t};\n
\n
\t\t\tvar savePreferences = editor.savePreferences = function() {\n
\t\t\t\t// Set background\n
\t\t\t\tvar color = $(\'#bg_blocks div.cur_background\').css(\'background-color\') || \'#FFF\';\n
\t\t\t\tsetBackground(color, $(\'#canvas_bg_url\').val());\n
\n
\t\t\t\t// set language\n
\t\t\t\tvar lang = $(\'#lang_select\').val();\n
\t\t\t\tif (lang !== $.pref(\'lang\')) {\n
\t\t\t\t\teditor.putLocale(lang, good_langs);\n
\t\t\t\t}\n
\n
\t\t\t\t// set icon size\n
\t\t\t\tsetIconSize($(\'#iconsize\').val());\n
\n
\t\t\t\t// set grid setting\n
\t\t\t\tcurConfig.gridSnapping = $(\'#grid_snapping_on\')[0].checked;\n
\t\t\t\tcurConfig.snappingStep = $(\'#grid_snapping_step\').val();\n
\t\t\t\tcurConfig.gridColor = $(\'#grid_color\').val();\n
\t\t\t\tcurConfig.showRulers = $(\'#show_rulers\')[0].checked;\n
\n
\t\t\t\t$(\'#rulers\').toggle(curConfig.showRulers);\n
\t\t\t\tif (curConfig.showRulers) {updateRulers();}\n
\t\t\t\tcurConfig.baseUnit = $(\'#base_unit\').val();\n
\n
\t\t\t\tsvgCanvas.setConfig(curConfig);\n
\n
\t\t\t\tupdateCanvas();\n
\t\t\t\thidePreferences();\n
\t\t\t};\n
\n
\t\t\tvar resetScrollPos = $.noop;\n
\n
\t\t\tvar cancelOverlays = function() {\n
\t\t\t\t$(\'#dialog_box\').hide();\n
\t\t\t\tif (!editingsource && !docprops && !preferences) {\n
\t\t\t\t\tif (cur_context) {\n
\t\t\t\t\t\tsvgCanvas.leaveContext();\n
\t\t\t\t\t}\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\n
\t\t\t\tif (editingsource) {\n
\t\t\t\t\tif (origSource !== $(\'#svg_source_textarea\').val()) {\n
\t\t\t\t\t\t$.confirm(uiStrings.notification.QignoreSourceChanges, function(ok) {\n
\t\t\t\t\t\t\tif (ok) {hideSourceEditor();}\n
\t\t\t\t\t\t});\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\thideSourceEditor();\n
\t\t\t\t\t}\n
\t\t\t\t} else if (docprops) {\n
\t\t\t\t\thideDocProperties();\n
\t\t\t\t} else if (preferences) {\n
\t\t\t\t\thidePreferences();\n
\t\t\t\t}\n
\t\t\t\tresetScrollPos();\n
\t\t\t};\n
\n
\t\t\tvar win_wh = {width:$(window).width(), height:$(window).height()};\n
\n
\t\t\t// Fix for Issue 781: Drawing area jumps to top-left corner on window resize (IE9)\n
\t\t\tif (svgedit.browser.isIE()) {\n
\t\t\t\t(function() {\n
\t\t\t\t\tresetScrollPos = function() {\n
\t\t\t\t\t\tif (workarea[0].scrollLeft === 0 && workarea[0].scrollTop === 0) {\n
\t\t\t\t\t\t\tworkarea[0].scrollLeft = curScrollPos.left;\n
\t\t\t\t\t\t\tworkarea[0].scrollTop = curScrollPos.top;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t};\n
\n
\t\t\t\t\tcurScrollPos = {\n
\t\t\t\t\t\tleft: workarea[0].scrollLeft,\n
\t\t\t\t\t\ttop: workarea[0].scrollTop\n
\t\t\t\t\t};\n
\n
\t\t\t\t\t$(window).resize(resetScrollPos);\n
\t\t\t\t\tsvgEditor.ready(function() {\n
\t\t\t\t\t\t// TODO: Find better way to detect when to do this to minimize\n
\t\t\t\t\t\t// flickering effect\n
\t\t\t\t\t\tsetTimeout(function() {\n
\t\t\t\t\t\t\tresetScrollPos();\n
\t\t\t\t\t\t}, 500);\n
\t\t\t\t\t});\n
\n
\t\t\t\t\tworkarea.scroll(function() {\n
\t\t\t\t\t\tcurScrollPos = {\n
\t\t\t\t\t\t\tleft: workarea[0].scrollLeft,\n
\t\t\t\t\t\t\ttop: workarea[0].scrollTop\n
\t\t\t\t\t\t};\n
\t\t\t\t\t});\n
\t\t\t\t}());\n
\t\t\t}\n
\n
\t\t\t$(window).resize(function(evt) {\n
\t\t\t\t$.each(win_wh, function(type, val) {\n
\t\t\t\t\tvar curval = $(window)[type]();\n
\t\t\t\t\tworkarea[0][\'scroll\' + (type === \'width\' ? \'Left\' : \'Top\')] -= (curval - val)/2;\n
\t\t\t\t\twin_wh[type] = curval;\n
\t\t\t\t});\n
\t\t\t\tsetFlyoutPositions();\n
\t\t\t});\n
\n
\t\t\t(function() {\n
\t\t\t\tworkarea.scroll(function() {\n
\t\t\t\t\t// TODO: jQuery\'s scrollLeft/Top() wouldn\'t require a null check\n
\t\t\t\t\tif ($(\'#ruler_x\').length != 0) {\n
\t\t\t\t\t\t$(\'#ruler_x\')[0].scrollLeft = workarea[0].scrollLeft;\n
\t\t\t\t\t}\n
\t\t\t\t\tif ($(\'#ruler_y\').length != 0) {\n
\t\t\t\t\t\t$(\'#ruler_y\')[0].scrollTop = workarea[0].scrollTop;\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\n
\t\t\t}());\n
\n
\t\t\t$(\'#url_notice\').click(function() {\n
\t\t\t\t$.alert(this.title);\n
\t\t\t});\n
\n
\t\t\t$(\'#change_image_url\').click(promptImgURL);\n
\n
\t\t\t// added these event handlers for all the push buttons so they\n
\t\t\t// behave more like buttons being pressed-in and not images\n
\t\t\t(function() {\n
\t\t\t\tvar toolnames = [\'clear\', \'open\', \'save\', \'source\', \'delete\', \'delete_multi\', \'paste\', \'clone\', \'clone_multi\', \'move_top\', \'move_bottom\'];\n
\t\t\t\tvar all_tools = \'\';\n
\t\t\t\tvar cur_class = \'tool_button_current\';\n
\n
\t\t\t\t$.each(toolnames, function(i,item) {\n
\t\t\t\t\tall_tools += \'#tool_\' + item + (i == toolnames.length-1 ? \',\' : \'\');\n
\t\t\t\t});\n
\n
\t\t\t\t$(all_tools).mousedown(function() {\n
\t\t\t\t\t$(this).addClass(cur_class);\n
\t\t\t\t}).bind(\'mousedown mouseout\', function() {\n
\t\t\t\t\t$(this).removeClass(cur_class);\n
\t\t\t\t});\n
\n
\t\t\t\t$(\'#tool_undo, #tool_redo\').mousedown(function() {\n
\t\t\t\t\tif (!$(this).hasClass(\'disabled\')) {$(this).addClass(cur_class);}\n
\t\t\t\t}).bind(\'mousedown mouseout\',function() {\n
\t\t\t\t\t$(this).removeClass(cur_class);}\n
\t\t\t\t);\n
\t\t\t}());\n
\n
\t\t\t// switch modifier key in tooltips if mac\n
\t\t\t// NOTE: This code is not used yet until I can figure out how to successfully bind ctrl/meta\n
\t\t\t// in Opera and Chrome\n
\t\t\tif (svgedit.browser.isMac() && !window.opera) {\n
\t\t\t\tvar shortcutButtons = [\'tool_clear\', \'tool_save\', \'tool_source\', \'tool_undo\', \'tool_redo\', \'tool_clone\'];\n
\t\t\t\ti = shortcutButtons.length;\n
\t\t\t\twhile (i--) {\n
\t\t\t\t\tvar button = document.getElementById(shortcutButtons[i]);\n
\t\t\t\t\tif (button) {\n
\t\t\t\t\t\tvar title = button.title;\n
\t\t\t\t\t\tvar index = title.indexOf(\'Ctrl+\');\n
\t\t\t\t\t\tbutton.title = [title.substr(0, index), \'Cmd+\', title.substr(index + 5)].join(\'\');\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t// TODO: go back to the color boxes having white background-color and then setting\n
\t\t\t//\tbackground-image to none.png (otherwise partially transparent gradients look weird)\n
\t\t\tvar colorPicker = function(elem) {\n
\t\t\t\tvar picker = elem.attr(\'id\') == \'stroke_color\' ? \'stroke\' : \'fill\';\n
//\t\t\t\tvar opacity = (picker == \'stroke\' ? $(\'#stroke_opacity\') : $(\'#fill_opacity\'));\n
\t\t\t\tvar paint = paintBox[picker].paint;\n
\t\t\t\tvar title = (picker == \'stroke\' ? \'Pick a Stroke Paint and Opacity\' : \'Pick a Fill Paint and Opacity\');\n
\t\t\t\t// var was_none = false; // Currently unused\n
\t\t\t\tvar pos = elem.offset();\n
\t\t\t\t$(\'#color_picker\')\n
\t\t\t\t\t.draggable({cancel: \'.jGraduate_tabs, .jGraduate_colPick, .jGraduate_gradPick, .jPicker\', containment: \'window\'})\n
\t\t\t\t\t.css(curConfig.colorPickerCSS || {\'left\': pos.left-140, \'bottom\': 40})\n
\t\t\t\t\t.jGraduate(\n
\t\t\t\t\t{\n
\t\t\t\t\t\tpaint: paint,\n
\t\t\t\t\t\twindow: { pickerTitle: title },\n
\t\t\t\t\t\timages: { clientPath: curConfig.jGraduatePath },\n
\t\t\t\t\t\tnewstop: \'inverse\'\n
\t\t\t\t\t},\n
\t\t\t\t\tfunction(p) {\n
\t\t\t\t\t\tpaint = new $.jGraduate.Paint(p);\n
\t\t\t\t\t\tpaintBox[picker].setPaint(paint);\n
\t\t\t\t\t\tsvgCanvas.setPaint(picker, paint);\n
\t\t\t\t\t\t$(\'#color_picker\').hide();\n
\t\t\t\t\t},\n
\t\t\t\t\tfunction() {\n
\t\t\t\t\t\t$(\'#color_picker\').hide();\n
\t\t\t\t\t});\n
\t\t\t};\n
\n
\t\t\tvar PaintBox = function(container, type) {\n
\t\t\t\tvar paintColor, paintOpacity,\n
\t\t\t\t\tcur = curConfig[type === \'fill\' ? \'initFill\' : \'initStroke\'];\n
\t\t\t\t// set up gradients to be used for the buttons\n
\t\t\t\tvar svgdocbox = new DOMParser().parseFromString(\n
\t\t\t\t\t\'<svg xmlns="http://www.w3.org/2000/svg"><rect width="16.5" height="16.5"\'+\n
\'\t\t\t\t\tfill="#\' + cur.color + \'" opacity="\' + cur.opacity + \'"/>\'+\n
\'\t\t\t\t\t<defs><linearGradient id="gradbox_"/></defs></svg>\', \'text/xml\');\n
\t\t\t\tvar docElem = svgdocbox.documentElement;\n
\n
\t\t\t\tdocElem = $(container)[0].appendChild(document.importNode(docElem, true));\n
\t\t\t\tdocElem.setAttribute(\'width\',16.5);\n
\n
\t\t\t\tthis.rect = docElem.firstChild;\n
\t\t\t\tthis.defs = docElem.getElementsByTagName(\'defs\')[0];\n
\t\t\t\tthis.grad = this.defs.firstChild;\n
\t\t\t\tthis.paint = new $.jGraduate.Paint({solidColor: cur.color});\n
\t\t\t\tthis.type = type;\n
\n
\t\t\t\tthis.setPaint = function(paint, apply) {\n
\t\t\t\t\tthis.paint = paint;\n
\n
\t\t\t\t\tvar fillAttr = \'none\';\n
\t\t\t\t\tvar ptype = paint.type;\n
\t\t\t\t\tvar opac = paint.alpha / 100;\n
\n
\t\t\t\t\tswitch ( ptype ) {\n
\t\t\t\t\t\tcase \'solidColor\':\n
\t\t\t\t\t\t\tfillAttr = (paint[ptype] != \'none\') ? \'#\' + paint[ptype] : paint[ptype];\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tcase \'linearGradient\':\n
\t\t\t\t\t\tcase \'radialGradient\':\n
\t\t\t\t\t\t\tthis.defs.removeChild(this.grad);\n
\t\t\t\t\t\t\tthis.grad = this.defs.appendChild(paint[ptype]);\n
\t\t\t\t\t\t\tvar id = this.grad.id = \'gradbox_\' + this.type;\n
\t\t\t\t\t\t\tfillAttr = \'url(#\' + id + \')\';\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tthis.rect.setAttribute(\'fill\', fillAttr);\n
\t\t\t\t\tthis.rect.setAttribute(\'opacity\', opac);\n
\n
\t\t\t\t\tif (apply) {\n
\t\t\t\t\t\tsvgCanvas.setColor(this.type, paintColor, true);\n
\t\t\t\t\t\tsvgCanvas.setPaintOpacity(this.type, paintOpacity, true);\n
\t\t\t\t\t}\n
\t\t\t\t};\n
\n
\t\t\t\tthis.update = function(apply) {\n
\t\t\t\t\tif (!selectedElement) {return;}\n
\t\t\t\t\tvar i, len;\n
\t\t\t\t\tvar type = this.type;\n
\t\t\t\t\tswitch (selectedElement.tagName) {\n
\t\t\t\t\tcase \'use\':\n
\t\t\t\t\tcase \'image\':\n
\t\t\t\t\tcase \'foreignObject\':\n
\t\t\t\t\t\t// These elements don\'t have fill or stroke, so don\'t change\n
\t\t\t\t\t\t// the current value\n
\t\t\t\t\t\treturn;\n
\t\t\t\t\tcase \'g\':\n
\t\t\t\t\tcase \'a\':\n
\t\t\t\t\t\tvar gPaint = null;\n
\n
\t\t\t\t\t\tvar childs = selectedElement.getElementsByTagName(\'*\');\n
\t\t\t\t\t\tfor (i = 0, len = childs.length; i < len; i++) {\n
\t\t\t\t\t\t\tvar elem = childs[i];\n
\t\t\t\t\t\t\tvar p = elem.getAttribute(type);\n
\t\t\t\t\t\t\tif (i === 0) {\n
\t\t\t\t\t\t\t\tgPaint = p;\n
\t\t\t\t\t\t\t} else if (gPaint !== p) {\n
\t\t\t\t\t\t\t\tgPaint = null;\n
\t\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tif (gPaint === null) {\n
\t\t\t\t\t\t\t// No common color, don\'t update anything\n
\t\t\t\t\t\t\tpaintColor = null;\n
\t\t\t\t\t\t\treturn;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tpaintColor = gPaint;\n
\t\t\t\t\t\tpaintOpacity = 1;\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tdefault:\n
\t\t\t\t\t\tpaintOpacity = parseFloat(selectedElement.getAttribute(type + \'-opacity\'));\n
\t\t\t\t\t\tif (isNaN(paintOpacity)) {\n
\t\t\t\t\t\t\tpaintOpacity = 1.0;\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tvar defColor = type === \'fill\' ? \'black\' : \'none\';\n
\t\t\t\t\t\tpaintColor = selectedElement.getAttribute(type) || defColor;\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tif (apply) {\n
\t\t\t\t\t\tsvgCanvas.setColor(type, paintColor, true);\n
\t\t\t\t\t\tsvgCanvas.setPaintOpacity(type, paintOpacity, true);\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tpaintOpacity *= 100;\n
\n
\t\t\t\t\tvar paint = getPaint(paintColor, paintOpacity, type);\n
\t\t\t\t\t// update the rect inside #fill_color/#stroke_color\n
\t\t\t\t\tthis.setPaint(paint);\n
\t\t\t\t};\n
\n
\t\t\t\tthis.prep = function() {\n
\t\t\t\t\tvar ptype = this.paint.type;\n
\n
\t\t\t\t\tswitch ( ptype ) {\n
\t\t\t\t\t\tcase \'linearGradient\':\n
\t\t\t\t\t\tcase \'radialGradient\':\n
\t\t\t\t\t\t\tvar paint = new $.jGraduate.Paint({copy: this.paint});\n
\t\t\t\t\t\t\tsvgCanvas.setPaint(type, paint);\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\t\t\t\t};\n
\t\t\t};\n
\n
\t\t\tpaintBox.fill = new PaintBox(\'#fill_color\', \'fill\');\n
\t\t\tpaintBox.stroke = new PaintBox(\'#stroke_color\', \'stroke\');\n
\n
\t\t\t$(\'#stroke_width\').val(curConfig.initStroke.width);\n
\t\t\t$(\'#group_opacity\').val(curConfig.initOpacity * 100);\n
\n
\t\t\t// Use this SVG elem to test vectorEffect support\n
\t\t\tvar testEl = paintBox.fill.rect.cloneNode(false);\n
\t\t\ttestEl.setAttribute(\'style\', \'vector-effect:non-scaling-stroke\');\n
\t\t\tsupportsNonSS = (testEl.style.vectorEffect === \'non-scaling-stroke\');\n
\t\t\ttestEl.removeAttribute(\'style\');\n
\t\t\tvar svgdocbox = paintBox.fill.rect.ownerDocument;\n
\t\t\t// Use this to test support for blur element. Seems to work to test support in Webkit\n
\t\t\tvar blurTest = svgdocbox.createElementNS(svgedit.NS.SVG, \'feGaussianBlur\');\n
\t\t\tif (blurTest.stdDeviationX === undefined) {\n
\t\t\t\t$(\'#tool_blur\').hide();\n
\t\t\t}\n
\t\t\t$(blurTest).remove();\n
\n
\t\t\t// Test for zoom icon support\n
\t\t\t(function() {\n
\t\t\t\tvar pre = \'-\' + uaPrefix.toLowerCase() + \'-zoom-\';\n
\t\t\t\tvar zoom = pre + \'in\';\n
\t\t\t\tworkarea.css(\'cursor\', zoom);\n
\t\t\t\tif (workarea.css(\'cursor\') === zoom) {\n
\t\t\t\t\tzoomInIcon = zoom;\n
\t\t\t\t\tzoomOutIcon = pre + \'out\';\n
\t\t\t\t}\n
\t\t\t\tworkarea.css(\'cursor\', \'auto\');\n
\t\t\t}());\n
\n
\t\t\t// Test for embedImage support (use timeout to not interfere with page load)\n
\t\t\tsetTimeout(function() {\n
\t\t\t\tsvgCanvas.embedImage(\'images/logo.png\', function(datauri) {\n
\t\t\t\t\tif (!datauri) {\n
\t\t\t\t\t\t// Disable option\n
\t\t\t\t\t\t$(\'#image_save_opts [value=embed]\').attr(\'disabled\', \'disabled\');\n
\t\t\t\t\t\t$(\'#image_save_opts input\').val([\'ref\']);\n
\t\t\t\t\t\t$.pref(\'img_save\', \'ref\');\n
\t\t\t\t\t\t$(\'#image_opt_embed\').css(\'color\', \'#666\').attr(\'title\', uiStrings.notification.featNotSupported);\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t}, 1000);\n
\n
\t\t\t$(\'#fill_color, #tool_fill .icon_label\').click(function() {\n
\t\t\t\tcolorPicker($(\'#fill_color\'));\n
\t\t\t\tupdateToolButtonState();\n
\t\t\t});\n
\n
\t\t\t$(\'#stroke_color, #tool_stroke .icon_label\').click(function() {\n
\t\t\t\tcolorPicker($(\'#stroke_color\'));\n
\t\t\t\tupdateToolButtonState();\n
\t\t\t});\n
\n
\t\t\t$(\'#group_opacityLabel\').click(function() {\n
\t\t\t\t$(\'#opacity_dropdown button\').mousedown();\n
\t\t\t\t$(window).mouseup();\n
\t\t\t});\n
\n
\t\t\t$(\'#zoomLabel\').click(function() {\n
\t\t\t\t$(\'#zoom_dropdown button\').mousedown();\n
\t\t\t\t$(window).mouseup();\n
\t\t\t});\n
\n
\t\t\t$(\'#tool_move_top\').mousedown(function(evt) {\n
\t\t\t\t$(\'#tools_stacking\').show();\n
\t\t\t\tevt.preventDefault();\n
\t\t\t});\n
\n
\t\t\t$(\'.layer_button\').mousedown(function() {\n
\t\t\t\t$(this).addClass(\'layer_buttonpressed\');\n
\t\t\t}).mouseout(function() {\n
\t\t\t\t$(this).removeClass(\'layer_buttonpressed\');\n
\t\t\t}).mouseup(function() {\n
\t\t\t\t$(this).removeClass(\'layer_buttonpressed\');\n
\t\t\t});\n
\n
\t\t\t$(\'.push_button\').mousedown(function() {\n
\t\t\t\tif (!$(this).hasClass(\'disabled\')) {\n
\t\t\t\t\t$(this).addClass(\'push_button_pressed\').removeClass(\'push_button\');\n
\t\t\t\t}\n
\t\t\t}).mouseout(function() {\n
\t\t\t\t$(this).removeClass(\'push_button_pressed\').addClass(\'push_button\');\n
\t\t\t}).mouseup(function() {\n
\t\t\t\t$(this).removeClass(\'push_button_pressed\').addClass(\'push_button\');\n
\t\t\t});\n
\n
\t\t\t// ask for a layer name\n
\t\t\t$(\'#layer_new\').click(function() {\n
\t\t\t\tvar uniqName,\n
\t\t\t\t\ti = svgCanvas.getCurrentDrawing().getNumLayers();\n
\t\t\t\tdo {\n
\t\t\t\t\tuniqName = uiStrings.layers.layer + \' \' + (++i);\n
\t\t\t\t} while(svgCanvas.getCurrentDrawing().hasLayer(uniqName));\n
\n
\t\t\t\t$.prompt(uiStrings.notification.enterUniqueLayerName, uniqName, function(newName) {\n
\t\t\t\t\tif (!newName) {return;}\n
\t\t\t\t\tif (svgCanvas.getCurrentDrawing().hasLayer(newName)) {\n
\t\t\t\t\t\t$.alert(uiStrings.notification.dupeLayerName);\n
\t\t\t\t\t\treturn;\n
\t\t\t\t\t}\n
\t\t\t\t\tsvgCanvas.createLayer(newName);\n
\t\t\t\t\tupdateContextPanel();\n
\t\t\t\t\tpopulateLayers();\n
\t\t\t\t});\n
\t\t\t});\n
\n
\t\t\tfunction deleteLayer() {\n
\t\t\t\tif (svgCanvas.deleteCurrentLayer()) {\n
\t\t\t\t\tupdateContextPanel();\n
\t\t\t\t\tpopulateLayers();\n
\t\t\t\t\t// This matches what SvgCanvas does\n
\t\t\t\t\t// TODO: make this behavior less brittle (svg-editor should get which\n
\t\t\t\t\t// layer is selected from the canvas and then select that one in the UI)\n
\t\t\t\t\t$(\'#layerlist tr.layer\').removeClass(\'layersel\');\n
\t\t\t\t\t$(\'#layerlist tr.layer:first\').addClass(\'layersel\');\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\tfunction cloneLayer() {\n
\t\t\t\tvar name = svgCanvas.getCurrentDrawing().getCurrentLayerName() + \' copy\';\n
\n
\t\t\t\t$.prompt(uiStrings.notification.enterUniqueLayerName, name, function(newName) {\n
\t\t\t\t\tif (!newName) {return;}\n
\t\t\t\t\tif (svgCanvas.getCurrentDrawing().hasLayer(newName)) {\n
\t\t\t\t\t\t$.alert(uiStrings.notification.dupeLayerName);\n
\t\t\t\t\t\treturn;\n
\t\t\t\t\t}\n
\t\t\t\t\tsvgCanvas.cloneLayer(newName);\n
\t\t\t\t\tupdateContextPanel();\n
\t\t\t\t\tpopulateLayers();\n
\t\t\t\t});\n
\t\t\t}\n
\n
\t\t\tfunction mergeLayer() {\n
\t\t\t\tif ($(\'#layerlist tr.layersel\').index() == svgCanvas.getCurrentDrawing().getNumLayers()-1) {\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\t\t\t\tsvgCanvas.mergeLayer();\n
\t\t\t\tupdateContextPanel();\n
\t\t\t\tpopulateLayers();\n
\t\t\t}\n
\n
\t\t\tfunction moveLayer(pos) {\n
\t\t\t\tvar curIndex = $(\'#layerlist tr.layersel\').index();\n
\t\t\t\tvar total = svgCanvas.getCurrentDrawing().getNumLayers();\n
\t\t\t\tif (curIndex > 0 || curIndex < total-1) {\n
\t\t\t\t\tcurIndex += pos;\n
\t\t\t\t\tsvgCanvas.setCurrentLayerPosition(total-curIndex-1);\n
\t\t\t\t\tpopulateLayers();\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t$(\'#layer_delete\').click(deleteLayer);\n
\n
\t\t\t$(\'#layer_up\').click(function() {\n
\t\t\t\tmoveLayer(-1);\n
\t\t\t});\n
\n
\t\t\t$(\'#layer_down\').click(function() {\n
\t\t\t\tmoveLayer(1);\n
\t\t\t});\n
\n
\t\t\t$(\'#layer_rename\').click(function() {\n
\t\t\t\t// var curIndex = $(\'#layerlist tr.layersel\').prevAll().length; // Currently unused\n
\t\t\t\tvar oldName = $(\'#layerlist tr.layersel td.layername\').text();\n
\t\t\t\t$.prompt(uiStrings.notification.enterNewLayerName, \'\', function(newName) {\n
\t\t\t\t\tif (!newName) {return;}\n
\t\t\t\t\tif (oldName == newName || svgCanvas.getCurrentDrawing().hasLayer(newName)) {\n
\t\t\t\t\t\t$.alert(uiStrings.notification.layerHasThatName);\n
\t\t\t\t\t\treturn;\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tsvgCanvas.renameCurrentLayer(newName);\n
\t\t\t\t\tpopulateLayers();\n
\t\t\t\t});\n
\t\t\t});\n
\n
\t\t\tvar SIDEPANEL_MAXWIDTH = 300;\n
\t\t\tvar SIDEPANEL_OPENWIDTH = 150;\n
\t\t\tvar sidedrag = -1, sidedragging = false, allowmove = false;\n
\n
\t\t\tvar changeSidePanelWidth = function(delta) {\n
\t\t\t\tvar rulerX = $(\'#ruler_x\');\n
\t\t\t\t$(\'#sidepanels\').width(\'+=\' + delta);\n
\t\t\t\t$(\'#layerpanel\').width(\'+=\' + delta);\n
\t\t\t\trulerX.css(\'right\', parseInt(rulerX.css(\'right\'), 10) + delta);\n
\t\t\t\tworkarea.css(\'right\', parseInt(workarea.css(\'right\'), 10) + delta);\n
\t\t\t\tsvgCanvas.runExtensions("workareaResized");\n
\t\t\t};\n
\n
\t\t\tvar resizeSidePanel = function(evt) {\n
\t\t\t\tif (!allowmove) {return;}\n
\t\t\t\tif (sidedrag == -1) {return;}\n
\t\t\t\tsidedragging = true;\n
\t\t\t\tvar deltaX = sidedrag - evt.pageX;\n
\t\t\t\tvar sideWidth = $(\'#sidepanels\').width();\n
\t\t\t\tif (sideWidth + deltaX > SIDEPANEL_MAXWIDTH) {\n
\t\t\t\t\tdeltaX = SIDEPANEL_MAXWIDTH - sideWidth;\n
\t\t\t\t\tsideWidth = SIDEPANEL_MAXWIDTH;\n
\t\t\t\t} else if (sideWidth + deltaX < 2) {\n
\t\t\t\t\tdeltaX = 2 - sideWidth;\n
\t\t\t\t\tsideWidth = 2;\n
\t\t\t\t}\n
\t\t\t\tif (deltaX == 0) {return;}\n
\t\t\t\tsidedrag -= deltaX;\n
\t\t\t\tchangeSidePanelWidth(deltaX);\n
\t\t\t};\n
\n
\t\t\t// if width is non-zero, then fully close it, otherwise fully open it\n
\t\t\t// the optional close argument forces the side panel closed\n
\t\t\tvar toggleSidePanel = function(close) {\n
\t\t\t\tvar w = $(\'#sidepanels\').width();\n
\t\t\t\tvar deltaX = (w > 2 || close ? 2 : SIDEPANEL_OPENWIDTH) - w;\n
\t\t\t\tchangeSidePanelWidth(deltaX);\n
\t\t\t};\n
\n
\t\t\t$(\'#sidepanel_handle\')\n
\t\t\t\t.mousedown(function(evt) {\n
\t\t\t\t\tsidedrag = evt.pageX;\n
\t\t\t\t\t$(window).mousemove(resizeSidePanel);\n
\t\t\t\t\tallowmove = false;\n
\t\t\t\t\t// Silly hack for Chrome, which always runs mousemove right after mousedown\n
\t\t\t\t\tsetTimeout(function() {\n
\t\t\t\t\t\tallowmove = true;\n
\t\t\t\t\t}, 20);\n
\t\t\t\t})\n
\t\t\t\t.mouseup(function(evt) {\n
\t\t\t\t\tif (!sidedragging) {toggleSidePanel();}\n
\t\t\t\t\tsidedrag = -1;\n
\t\t\t\t\tsidedragging = false;\n
\t\t\t\t});\n
\n
\t\t\t$(window).mouseup(function() {\n
\t\t\t\tsidedrag = -1;\n
\t\t\t\tsidedragging = false;\n
\t\t\t\t$(\'#svg_editor\').unbind(\'mousemove\', resizeSidePanel);\n
\t\t\t});\n
\n
\t\t\tpopulateLayers();\n
\n
\t\t//\tfunction changeResolution(x,y) {\n
\t\t//\t\tvar zoom = svgCanvas.getResolution().zoom;\n
\t\t//\t\tsetResolution(x * zoom, y * zoom);\n
\t\t//\t}\n
\n
\t\t\tvar centerCanvas = function() {\n
\t\t\t\t// this centers the canvas vertically in the workarea (horizontal handled in CSS)\n
\t\t\t\tworkarea.css(\'line-height\', workarea.height() + \'px\');\n
\t\t\t};\n
\n
\t\t\t$(window).bind(\'load resize\', centerCanvas);\n
\n
\t\t\tfunction stepFontSize(elem, step) {\n
\t\t\t\tvar orig_val = Number(elem.value);\n
\t\t\t\tvar sug_val = orig_val + step;\n
\t\t\t\tvar increasing = sug_val >= orig_val;\n
\t\t\t\tif (step === 0) {return orig_val;}\n
\n
\t\t\t\tif (orig_val >= 24) {\n
\t\t\t\t\tif (increasing) {\n
\t\t\t\t\t\treturn Math.round(orig_val * 1.1);\n
\t\t\t\t\t}\n
\t\t\t\t\treturn Math.round(orig_val / 1.1);\n
\t\t\t\t}\n
\t\t\t\tif (orig_val <= 1) {\n
\t\t\t\t\tif (increasing) {\n
\t\t\t\t\t\treturn orig_val * 2;\n
\t\t\t\t\t}\n
\t\t\t\t\treturn orig_val / 2;\n
\t\t\t\t}\n
\t\t\t\treturn sug_val;\n
\t\t\t}\n
\n
\t\t\tfunction stepZoom(elem, step) {\n
\t\t\t\tvar orig_val = Number(elem.value);\n
\t\t\t\tif (orig_val === 0) {return 100;}\n
\t\t\t\tvar sug_val = orig_val + step;\n
\t\t\t\tif (step === 0) {return orig_val;}\n
\n
\t\t\t\tif (orig_val >= 100) {\n
\t\t\t\t\treturn sug_val;\n
\t\t\t\t}\n
\t\t\t\tif (sug_val >= orig_val) {\n
\t\t\t\t\treturn orig_val * 2;\n
\t\t\t\t}\n
\t\t\t\treturn orig_val / 2;\n
\t\t\t}\n
\n
\t\t//\tfunction setResolution(w, h, center) {\n
\t\t//\t\tupdateCanvas();\n
\t\t// //\t\tw-=0; h-=0;\n
\t\t// //\t\t$(\'#svgcanvas\').css( { \'width\': w, \'height\': h } );\n
\t\t// //\t\t$(\'#canvas_width\').val(w);\n
\t\t// //\t\t$(\'#canvas_height\').val(h);\n
\t\t// //\n
\t\t// //\t\tif (center) {\n
\t\t// //\t\t\tvar w_area = workarea;\n
\t\t// //\t\t\tvar scroll_y = h/2 - w_area.height()/2;\n
\t\t// //\t\t\tvar scroll_x = w/2 - w_area.width()/2;\n
\t\t// //\t\t\tw_area[0].scrollTop = scroll_y;\n
\t\t// //\t\t\tw_area[0].scrollLeft = scroll_x;\n
\t\t// //\t\t}\n
\t\t//\t}\n
\n
\t\t\t$(\'#resolution\').change(function() {\n
\t\t\t\tvar wh = $(\'#canvas_width,#canvas_height\');\n
\t\t\t\tif (!this.selectedIndex) {\n
\t\t\t\t\tif ($(\'#canvas_width\').val() == \'fit\') {\n
\t\t\t\t\t\twh.removeAttr(\'disabled\').val(100);\n
\t\t\t\t\t}\n
\t\t\t\t} else if (this.value == \'content\') {\n
\t\t\t\t\twh.val(\'fit\').attr(\'disabled\', \'disabled\');\n
\t\t\t\t} else {\n
\t\t\t\t\tvar dims = this.value.split(\'x\');\n
\t\t\t\t\t$(\'#canvas_width\').val(dims[0]);\n
\t\t\t\t\t$(\'#canvas_height\').val(dims[1]);\n
\t\t\t\t\twh.removeAttr(\'disabled\');\n
\t\t\t\t}\n
\t\t\t});\n
\n
\t\t\t//Prevent browser from erroneously repopulating fields\n
\t\t\t$(\'input,select\').attr(\'autocomplete\', \'off\');\n
\n
\t\t\t// Associate all button actions as well as non-button keyboard shortcuts\n
\t\t\tActions = (function() {\n
\t\t\t\t// sel:\'selector\', fn:function, evt:\'event\', key:[key, preventDefault, NoDisableInInput]\n
\t\t\t\tvar tool_buttons = [\n
\t\t\t\t\t{sel: \'#tool_select\', fn: clickSelect, evt: \'click\', key: [\'V\', true]},\n
\t\t\t\t\t{sel: \'#tool_fhpath\', fn: clickFHPath, evt: \'click\', key: [\'Q\', true]},\n
\t\t\t\t\t{sel: \'#tool_line\', fn: clickLine, evt: \'click\', key: [\'L\', true]},\n
\t\t\t\t\t{sel: \'#tool_rect\', fn: clickRect, evt: \'mouseup\', key: [\'R\', true], parent: \'#tools_rect\', icon: \'rect\'},\n
\t\t\t\t\t{sel: \'#tool_square\', fn: clickSquare, evt: \'mouseup\', parent: \'#tools_rect\', icon: \'square\'},\n
\t\t\t\t\t{sel: \'#tool_fhrect\', fn: clickFHRect, evt: \'mouseup\', parent: \'#tools_rect\', icon: \'fh_rect\'},\n
\t\t\t\t\t{sel: \'#tool_ellipse\', fn: clickEllipse, evt: \'mouseup\', key: [\'E\', true], parent: \'#tools_ellipse\', icon: \'ellipse\'},\n
\t\t\t\t\t{sel: \'#tool_circle\', fn: clickCircle, evt: \'mouseup\', parent: \'#tools_ellipse\', icon: \'circle\'},\n
\t\t\t\t\t{sel: \'#tool_fhellipse\', fn: clickFHEllipse, evt: \'mouseup\', parent: \'#tools_ellipse\', icon: \'fh_ellipse\'},\n
\t\t\t\t\t{sel: \'#tool_path\', fn: clickPath, evt: \'click\', key: [\'P\', true]},\n
\t\t\t\t\t{sel: \'#tool_text\', fn: clickText, evt: \'click\', key: [\'T\', true]},\n
\t\t\t\t\t{sel: \'#tool_image\', fn: clickImage, evt: \'mouseup\'},\n
\t\t\t\t\t{sel: \'#tool_zoom\', fn: clickZoom, evt: \'mouseup\', key: [\'Z\', true]},\n
\t\t\t\t\t{sel: \'#tool_clear\', fn: clickClear, evt: \'mouseup\', key: [\'N\', true]},\n
\t\t\t\t\t{sel: \'#tool_save\', fn: function() {\n
\t\t\t\t\t\tif (editingsource) {\n
\t\t\t\t\t\t\tsaveSourceEditor();\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\telse {\n
\t\t\t\t\t\t\tclickSave();\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}, evt: \'mouseup\', key: [\'S\', true]},\n
\t\t\t\t\t{sel: \'#tool_export\', fn: clickExport, evt: \'mouseup\'},\n
\t\t\t\t\t{sel: \'#tool_open\', fn: clickOpen, evt: \'mouseup\', key: [\'O\', true]},\n
\t\t\t\t\t{sel: \'#tool_import\', fn: clickImport, evt: \'mouseup\'},\n
\t\t\t\t\t{sel: \'#tool_source\', fn: showSourceEditor, evt: \'click\', key: [\'U\', true]},\n
\t\t\t\t\t{sel: \'#tool_wireframe\', fn: clickWireframe, evt: \'click\', key: [\'F\', true]},\n
\t\t\t\t\t{sel: \'#tool_source_cancel,.overlay,#tool_docprops_cancel,#tool_prefs_cancel\', fn: cancelOverlays, evt: \'click\', key: [\'esc\', false, false], hidekey: true},\n
\t\t\t\t\t{sel: \'#tool_source_save\', fn: saveSourceEditor, evt: \'click\'},\n
\t\t\t\t\t{sel: \'#tool_docprops_save\', fn: saveDocProperties, evt: \'click\'},\n
\t\t\t\t\t{sel: \'#tool_docprops\', fn: showDocProperties, evt: \'mouseup\'},\n
\t\t\t\t\t{sel: \'#tool_prefs_save\', fn: savePreferences, evt: \'click\'},\n
\t\t\t\t\t{sel: \'#tool_prefs_option\', fn: function() {showPreferences(); return false;}, evt: \'mouseup\'},\n
\t\t\t\t\t{sel: \'#tool_delete,#tool_delete_multi\', fn: deleteSelected, evt: \'click\', key: [\'del/backspace\', true]},\n
\t\t\t\t\t{sel: \'#tool_reorient\', fn: reorientPath, evt: \'click\'},\n
\t\t\t\t\t{sel: \'#tool_node_link\', fn: linkControlPoints, evt: \'click\'},\n
\t\t\t\t\t{sel: \'#tool_node_clone\', fn: clonePathNode, evt: \'click\'},\n
\t\t\t\t\t{sel: \'#tool_node_delete\', fn: deletePathNode, evt: \'click\'},\n
\t\t\t\t\t{sel: \'#tool_openclose_path\', fn: opencloseSubPath, evt: \'click\'},\n
\t\t\t\t\t{sel: \'#tool_add_subpath\', fn: addSubPath, evt: \'click\'},\n
\t\t\t\t\t{sel: \'#tool_move_top\', fn: moveToTopSelected, evt: \'click\', key: \'ctrl+shift+]\'},\n
\t\t\t\t\t{sel: \'#tool_move_bottom\', fn: moveToBottomSelected, evt: \'click\', key: \'ctrl+shift+[\'},\n
\t\t\t\t\t{sel: \'#tool_topath\', fn: convertToPath, evt: \'click\'},\n
\t\t\t\t\t{sel: \'#tool_make_link,#tool_make_link_multi\', fn: makeHyperlink, evt: \'click\'},\n
\t\t\t\t\t{sel: \'#tool_undo\', fn: clickUndo, evt: \'click\', key: [\'Z\', true]},\n
\t\t\t\t\t{sel: \'#tool_redo\', fn: clickRedo, evt: \'click\', key: [\'Y\', true]},\n
\t\t\t\t\t{sel: \'#tool_clone,#tool_clone_multi\', fn: clickClone, evt: \'click\', key: [\'D\', true]},\n
\t\t\t\t\t{sel: \'#tool_group_elements\', fn: clickGroup, evt: \'click\', key: [\'G\', true]},\n
\t\t\t\t\t{sel: \'#tool_ungroup\', fn: clickGroup, evt: \'click\'},\n
\t\t\t\t\t{sel: \'#tool_unlink_use\', fn: clickGroup, evt: \'click\'},\n
\t\t\t\t\t{sel: \'[id^=tool_align]\', fn: clickAlign, evt: \'click\'},\n
\t\t\t\t\t// these two lines are required to make Opera work properly with the flyout mechanism\n
\t\t//\t\t\t{sel: \'#tools_rect_show\', fn: clickRect, evt: \'click\'},\n
\t\t//\t\t\t{sel: \'#tools_ellipse_show\', fn: clickEllipse, evt: \'click\'},\n
\t\t\t\t\t{sel: \'#tool_bold\', fn: clickBold, evt: \'mousedown\'},\n
\t\t\t\t\t{sel: \'#tool_italic\', fn: clickItalic, evt: \'mousedown\'},\n
\t\t\t\t\t{sel: \'#sidepanel_handle\', fn: toggleSidePanel, key: [\'X\']},\n
\t\t\t\t\t{sel: \'#copy_save_done\', fn: cancelOverlays, evt: \'click\'},\n
\n
\t\t\t\t\t// Shortcuts not associated with buttons\n
\n
\t\t\t\t\t{key: \'ctrl+left\', fn: function(){rotateSelected(0,1);}},\n
\t\t\t\t\t{key: \'ctrl+right\', fn: function(){rotateSelected(1,1);}},\n
\t\t\t\t\t{key: \'ctrl+shift+left\', fn: function(){rotateSelected(0,5);}},\n
\t\t\t\t\t{key: \'ctrl+shift+right\', fn: function(){rotateSelected(1,5);}},\n
\t\t\t\t\t{key: \'shift+O\', fn: selectPrev},\n
\t\t\t\t\t{key: \'shift+P\', fn: selectNext},\n
\t\t\t\t\t{key: [modKey+\'up\', true], fn: function(){zoomImage(2);}},\n
\t\t\t\t\t{key: [modKey+\'down\', true], fn: function(){zoomImage(0.5);}},\n
\t\t\t\t\t{key: [modKey+\']\', true], fn: function(){moveUpDownSelected(\'Up\');}},\n
\t\t\t\t\t{key: [modKey+\'[\', true], fn: function(){moveUpDownSelected(\'Down\');}},\n
\t\t\t\t\t{key: [\'up\', true], fn: function(){moveSelected(0,-1);}},\n
\t\t\t\t\t{key: [\'down\', true], fn: function(){moveSelected(0,1);}},\n
\t\t\t\t\t{key: [\'left\', true], fn: function(){moveSelected(-1,0);}},\n
\t\t\t\t\t{key: [\'right\', true], fn: function(){moveSelected(1,0);}},\n
\t\t\t\t\t{key: \'shift+up\', fn: function(){moveSelected(0,-10);}},\n
\t\t\t\t\t{key: \'shift+down\', fn: function(){moveSelected(0,10);}},\n
\t\t\t\t\t{key: \'shift+left\', fn: function(){moveSelected(-10,0);}},\n
\t\t\t\t\t{key: \'shift+right\', fn: function(){moveSelected(10,0);}},\n
\t\t\t\t\t{key: [\'alt+up\', true], fn: function(){svgCanvas.cloneSelectedElements(0,-1);}},\n
\t\t\t\t\t{key: [\'alt+down\', true], fn: function(){svgCanvas.cloneSelectedElements(0,1);}},\n
\t\t\t\t\t{key: [\'alt+left\', true], fn: function(){svgCanvas.cloneSelectedElements(-1,0);}},\n
\t\t\t\t\t{key: [\'alt+right\', true], fn: function(){svgCanvas.cloneSelectedElements(1,0);}},\n
\t\t\t\t\t{key: [\'alt+shift+up\', true], fn: function(){svgCanvas.cloneSelectedElements(0,-10);}},\n
\t\t\t\t\t{key: [\'alt+shift+down\', true], fn: function(){svgCanvas.cloneSelectedElements(0,10);}},\n
\t\t\t\t\t{key: [\'alt+shift+left\', true], fn: function(){svgCanvas.cloneSelectedElements(-10,0);}},\n
\t\t\t\t\t{key: [\'alt+shift+right\', true], fn: function(){svgCanvas.cloneSelectedElements(10,0);}},\n
\t\t\t\t\t{key: \'A\', fn: function(){svgCanvas.selectAllInCurrentLayer();}},\n
\n
\t\t\t\t\t// Standard shortcuts\n
\t\t\t\t\t{key: modKey+\'z\', fn: clickUndo},\n
\t\t\t\t\t{key: modKey + \'shift+z\', fn: clickRedo},\n
\t\t\t\t\t{key: modKey + \'y\', fn: clickRedo},\n
\n
\t\t\t\t\t{key: modKey+\'x\', fn: cutSelected},\n
\t\t\t\t\t{key: modKey+\'c\', fn: copySelected},\n
\t\t\t\t\t{key: modKey+\'v\', fn: pasteInCenter}\n
\t\t\t\t];\n
\n
\t\t\t\t// Tooltips not directly associated with a single function\n
\t\t\t\tvar key_assocs = {\n
\t\t\t\t\t\'4/Shift+4\': \'#tools_rect_show\',\n
\t\t\t\t\t\'5/Shift+5\': \'#tools_ellipse_show\'\n
\t\t\t\t};\n
\n
\t\t\t\treturn {\n
\t\t\t\t\tsetAll: function() {\n
\t\t\t\t\t\tvar flyouts = {};\n
\n
\t\t\t\t\t\t$.each(tool_buttons, function(i, opts) {\n
\t\t\t\t\t\t\t// Bind function to button\n
\t\t\t\t\t\t\tvar btn;\n
\t\t\t\t\t\t\tif (opts.sel) {\n
\t\t\t\t\t\t\t\tbtn = $(opts.sel);\n
\t\t\t\t\t\t\t\tif (btn.length == 0) {return true;} // Skip if markup does not exist\n
\t\t\t\t\t\t\t\tif (opts.evt) {\n
\t\t\t\t\t\t\t\t\tif (svgedit.browser.isTouch() && opts.evt === \'click\') {\n
\t\t\t\t\t\t\t\t\t\topts.evt = \'mousedown\';\n
\t\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\t\tbtn[opts.evt](opts.fn);\n
\t\t\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t\t\t// Add to parent flyout menu, if able to be displayed\n
\t\t\t\t\t\t\t\tif (opts.parent && $(opts.parent + \'_show\').length != 0) {\n
\t\t\t\t\t\t\t\t\tvar f_h = $(opts.parent);\n
\t\t\t\t\t\t\t\t\tif (!f_h.length) {\n
\t\t\t\t\t\t\t\t\t\tf_h = makeFlyoutHolder(opts.parent.substr(1));\n
\t\t\t\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t\t\t\tf_h.append(btn);\n
\n
\t\t\t\t\t\t\t\t\tif (!$.isArray(flyouts[opts.parent])) {\n
\t\t\t\t\t\t\t\t\t\tflyouts[opts.parent] = [];\n
\t\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\t\tflyouts[opts.parent].push(opts);\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t\t// Bind function to shortcut key\n
\t\t\t\t\t\t\tif (opts.key) {\n
\t\t\t\t\t\t\t\t// Set shortcut based on options\n
\t\t\t\t\t\t\t\tvar keyval, disInInp = true, fn = opts.fn, pd = false;\n
\t\t\t\t\t\t\t\tif ($.isArray(opts.key)) {\n
\t\t\t\t\t\t\t\t\tkeyval = opts.key[0];\n
\t\t\t\t\t\t\t\t\tif (opts.key.length > 1) {pd = opts.key[1];}\n
\t\t\t\t\t\t\t\t\tif (opts.key.length > 2) {disInInp = opts.key[2];}\n
\t\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\t\tkeyval = opts.key;\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\tkeyval += \'\';\n
\n
\t\t\t\t\t\t\t\t$.each(keyval.split(\'/\'), function(i, key) {\n
\t\t\t\t\t\t\t\t\t$(document).bind(\'keydown\', key, function(e) {\n
\t\t\t\t\t\t\t\t\t\tfn();\n
\t\t\t\t\t\t\t\t\t\tif (pd) {\n
\t\t\t\t\t\t\t\t\t\t\te.preventDefault();\n
\t\t\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\t\t\t// Prevent default on ALL keys?\n
\t\t\t\t\t\t\t\t\t\treturn false;\n
\t\t\t\t\t\t\t\t\t});\n
\t\t\t\t\t\t\t\t});\n
\n
\t\t\t\t\t\t\t\t// Put shortcut in title\n
\t\t\t\t\t\t\t\tif (opts.sel && !opts.hidekey && btn.attr(\'title\')) {\n
\t\t\t\t\t\t\t\t\tvar newTitle = btn.attr(\'title\').split(\'[\')[0] + \' (\' + keyval + \')\';\n
\t\t\t\t\t\t\t\t\tkey_assocs[keyval] = opts.sel;\n
\t\t\t\t\t\t\t\t\t// Disregard for menu items\n
\t\t\t\t\t\t\t\t\tif (!btn.parents(\'#main_menu\').length) {\n
\t\t\t\t\t\t\t\t\t\tbtn.attr(\'title\', newTitle);\n
\t\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t});\n
\n
\t\t\t\t\t\t// Setup flyouts\n
\t\t\t\t\t\tsetupFlyouts(flyouts);\n
\n
\t\t\t\t\t\t// Misc additional actions\n
\n
\t\t\t\t\t\t// Make \'return\' keypress trigger the change event\n
\t\t\t\t\t\t$(\'.attr_changer, #image_url\').bind(\'keydown\', \'return\',\n
\t\t\t\t\t\t\tfunction(evt) {$(this).change();evt.preventDefault();}\n
\t\t\t\t\t\t);\n
\n
\t\t\t\t\t\t$(window).bind(\'keydown\', \'tab\', function(e) {\n
\t\t\t\t\t\t\tif (ui_context === \'canvas\') {\n
\t\t\t\t\t\t\t\te.preventDefault();\n
\t\t\t\t\t\t\t\tselectNext();\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}).bind(\'keydown\', \'shift+tab\', function(e) {\n
\t\t\t\t\t\t\tif (ui_context === \'canvas\') {\n
\t\t\t\t\t\t\t\te.preventDefault();\n
\t\t\t\t\t\t\t\tselectPrev();\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t});\n
\n
\t\t\t\t\t\t$(\'#tool_zoom\').dblclick(dblclickZoom);\n
\t\t\t\t\t},\n
\t\t\t\t\tsetTitles: function() {\n
\t\t\t\t\t\t$.each(key_assocs, function(keyval, sel) {\n
\t\t\t\t\t\t\tvar menu = ($(sel).parents(\'#main_menu\').length);\n
\n
\t\t\t\t\t\t\t$(sel).each(function() {\n
\t\t\t\t\t\t\t\tvar t;\n
\t\t\t\t\t\t\t\tif (menu) {\n
\t\t\t\t\t\t\t\t\tt = $(this).text().split(\' [\')[0];\n
\t\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\t\tt = this.title.split(\' [\')[0];\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\tvar key_str = \'\';\n
\t\t\t\t\t\t\t\t// Shift+Up\n
\t\t\t\t\t\t\t\t$.each(keyval.split(\'/\'), function(i, key) {\n
\t\t\t\t\t\t\t\t\tvar mod_bits = key.split(\'+\'), mod = \'\';\n
\t\t\t\t\t\t\t\t\tif (mod_bits.length > 1) {\n
\t\t\t\t\t\t\t\t\t\tmod = mod_bits[0] + \'+\';\n
\t\t\t\t\t\t\t\t\t\tkey = mod_bits[1];\n
\t\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\t\tkey_str += (i?\'/\':\'\') + mod + (uiStrings[\'key_\'+key] || key);\n
\t\t\t\t\t\t\t\t});\n
\t\t\t\t\t\t\t\tif (menu) {\n
\t\t\t\t\t\t\t\t\tthis.lastChild.textContent = t +\' [\'+key_str+\']\';\n
\t\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\t\tthis.title = t +\' [\'+key_str+\']\';\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t});\n
\t\t\t\t\t\t});\n
\t\t\t\t\t},\n
\t\t\t\t\tgetButtonData: function(sel) {\n
\t\t\t\t\t\tvar b;\n
\t\t\t\t\t\t$.each(tool_buttons, function(i, btn) {\n
\t\t\t\t\t\t\tif (btn.sel === sel) {b = btn;}\n
\t\t\t\t\t\t});\n
\t\t\t\t\t\treturn b;\n
\t\t\t\t\t}\n
\t\t\t\t};\n
\t\t\t}());\n
\n
\t\t\tActions.setAll();\n
\n
\t\t\t// Select given tool\n
\t\t\teditor.ready(function() {\n
\t\t\t\tvar tool,\n
\t\t\t\t\titool = curConfig.initTool,\n
\t\t\t\t\tcontainer = $(\'#tools_left, #svg_editor .tools_flyout\'),\n
\t\t\t\t\tpre_tool = container.find(\'#tool_\' + itool),\n
\t\t\t\t\treg_tool = container.find(\'#\' + itool);\n
\t\t\t\tif (pre_tool.length) {\n
\t\t\t\t\ttool = pre_tool;\n
\t\t\t\t} else if (reg_tool.length) {\n
\t\t\t\t\ttool = reg_tool;\n
\t\t\t\t} else {\n
\t\t\t\t\ttool = $(\'#tool_select\');\n
\t\t\t\t}\n
\t\t\t\ttool.click().mouseup();\n
\n
\t\t\t\tif (curConfig.wireframe) {\n
\t\t\t\t\t$(\'#tool_wireframe\').click();\n
\t\t\t\t}\n
\n
\t\t\t\tif (curConfig.showlayers) {\n
\t\t\t\t\ttoggleSidePanel();\n
\t\t\t\t}\n
\n
\t\t\t\t$(\'#rulers\').toggle(!!curConfig.showRulers);\n
\n
\t\t\t\tif (curConfig.showRulers) {\n
\t\t\t\t\t$(\'#show_rulers\')[0].checked = true;\n
\t\t\t\t}\n
\n
\t\t\t\tif (curConfig.baseUnit) {\n
\t\t\t\t\t$(\'#base_unit\').val(curConfig.baseUnit);\n
\t\t\t\t}\n
\n
\t\t\t\tif (curConfig.gridSnapping) {\n
\t\t\t\t\t$(\'#grid_snapping_on\')[0].checked = true;\n
\t\t\t\t}\n
\n
\t\t\t\tif (curConfig.snappingStep) {\n
\t\t\t\t\t$(\'#grid_snapping_step\').val(curConfig.snappingStep);\n
\t\t\t\t}\n
\n
\t\t\t\tif (curConfig.gridColor) {\n
\t\t\t\t\t$(\'#grid_color\').val(curConfig.gridColor);\n
\t\t\t\t}\n
\t\t\t});\n
\n
\t\t\t// init SpinButtons\n
\t\t\t$(\'#rect_rx\').SpinButton({ min: 0, max: 1000, callback: changeRectRadius });\n
\t\t\t$(\'#stroke_width\').SpinButton({ min: 0, max: 99, smallStep: 0.1, callback: changeStrokeWidth });\n
\t\t\t$(\'#angle\').SpinButton({ min: -180, max: 180, step: 5, callback: changeRotationAngle });\n
\t\t\t$(\'#font_size\').SpinButton({ min: 0.001, stepfunc: stepFontSize, callback: changeFontSize });\n
\t\t\t$(\'#group_opacity\').SpinButton({ min: 0, max: 100, step: 5, callback: changeOpacity });\n
\t\t\t$(\'#blur\').SpinButton({ min: 0, max: 10, step: 0.1, callback: changeBlur });\n
\t\t\t$(\'#zoom\').SpinButton({ min: 0.001, max: 10000, step: 50, stepfunc: stepZoom, callback: changeZoom })\n
\t\t\t\t// Set default zoom\n
\t\t\t\t.val(svgCanvas.getZoom() * 100);\n
\n
\t\t\t$(\'#workarea\').contextMenu({\n
\t\t\t\t\tmenu: \'cmenu_canvas\',\n
\t\t\t\t\tinSpeed: 0\n
\t\t\t\t},\n
\t\t\t\tfunction(action, el, pos) {\n
\t\t\t\t\tswitch (action) {\n
\t\t\t\t\t\tcase \'delete\':\n
\t\t\t\t\t\t\tdeleteSelected();\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tcase \'cut\':\n
\t\t\t\t\t\t\tcutSelected();\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tcase \'copy\':\n
\t\t\t\t\t\t\tcopySelected();\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tcase \'paste\':\n
\t\t\t\t\t\t\tsvgCanvas.pasteElements();\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tcase \'paste_in_place\':\n
\t\t\t\t\t\t\tsvgCanvas.pasteElements(\'in_place\');\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tcase \'group_elements\':\n
\t\t\t\t\t\t\tsvgCanvas.groupSelectedElements();\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tcase \'ungroup\':\n
\t\t\t\t\t\t\tsvgCanvas.ungroupSelectedElement();\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tcase \'move_front\':\n
\t\t\t\t\t\t\tmoveToTopSelected();\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tcase \'move_up\':\n
\t\t\t\t\t\t\tmoveUpDownSelected(\'Up\');\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tcase \'move_down\':\n
\t\t\t\t\t\t\tmoveUpDownSelected(\'Down\');\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tcase \'move_back\':\n
\t\t\t\t\t\t\tmoveToBottomSelected();\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\tdefault:\n
\t\t\t\t\t\t\tif (svgedit.contextmenu && svgedit.contextmenu.hasCustomHandler(action)) {\n
\t\t\t\t\t\t\t\tsvgedit.contextmenu.getCustomHandler(action).call();\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\t\t\t\t\tif (svgCanvas.clipBoard.length) {\n
\t\t\t\t\t\tcanv_menu.enableContextMenuItems(\'#paste,#paste_in_place\');\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t);\n
\n
\t\t\tvar lmenu_func = function(action, el, pos) {\n
\t\t\t\tswitch ( action ) {\n
\t\t\t\t\tcase \'dupe\':\n
\t\t\t\t\t\tcloneLayer();\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'delete\':\n
\t\t\t\t\t\tdeleteLayer();\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'merge_down\':\n
\t\t\t\t\t\tmergeLayer();\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'merge_all\':\n
\t\t\t\t\t\tsvgCanvas.mergeAllLayers();\n
\t\t\t\t\t\tupdateContextPanel();\n
\t\t\t\t\t\tpopulateLayers();\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\t$(\'#layerlist\').contextMenu({\n
\t\t\t\t\tmenu: \'cmenu_layers\',\n
\t\t\t\t\tinSpeed: 0\n
\t\t\t\t},\n
\t\t\t\tlmenu_func\n
\t\t\t);\n
\n
\t\t\t$(\'#layer_moreopts\').contextMenu({\n
\t\t\t\t\tmenu: \'cmenu_layers\',\n
\t\t\t\t\tinSpeed: 0,\n
\t\t\t\t\tallowLeft: true\n
\t\t\t\t},\n
\t\t\t\tlmenu_func\n
\t\t\t);\n
\n
\t\t\t$(\'.contextMenu li\').mousedown(function(ev) {\n
\t\t\t\tev.preventDefault();\n
\t\t\t});\n
\n
\t\t\t$(\'#cmenu_canvas li\').disableContextMenu();\n
\t\t\tcanv_menu.enableContextMenuItems(\'#delete,#cut,#copy\');\n
\n
\t\t\twindow.addEventListener(\'beforeunload\', function(e) {\n
\t\t\t\t// Suppress warning if page is empty\n
\t\t\t\tif (undoMgr.getUndoStackSize() === 0) {\n
\t\t\t\t\teditor.showSaveWarning = false;\n
\t\t\t\t}\n
\n
\t\t\t\t// showSaveWarning is set to \'false\' when the page is saved.\n
\t\t\t\tif (!curConfig.no_save_warning && editor.showSaveWarning) {\n
\t\t\t\t\t// Browser already asks question about closing the page\n
\t\t\t\t\te.returnValue = uiStrings.notification.unsavedChanges; // Firefox needs this when beforeunload set by addEventListener (even though message is not used)\n
\t\t\t\t\treturn uiStrings.notification.unsavedChanges;\n
\t\t\t\t}\n
\t\t\t}, false);\n
\n
\t\t\teditor.openPrep = function(func) {\n
\t\t\t\t$(\'#main_menu\').hide();\n
\t\t\t\tif (undoMgr.getUndoStackSize() === 0) {\n
\t\t\t\t\tfunc(true);\n
\t\t\t\t} else {\n
\t\t\t\t\t$.confirm(uiStrings.notification.QwantToOpen, func);\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tfunction onDragEnter(e) {\n
\t\t\t\te.stopPropagation();\n
\t\t\t\te.preventDefault();\n
\t\t\t\t// and indicator should be displayed here, such as "drop files here"\n
\t\t\t}\n
\n
\t\t\tfunction onDragOver(e) {\n
\t\t\t\te.stopPropagation();\n
\t\t\t\te.preventDefault();\n
\t\t\t}\n
\n
\t\t\tfunction onDragLeave(e) {\n
\t\t\t\te.stopPropagation();\n
\t\t\t\te.preventDefault();\n
\t\t\t\t// hypothetical indicator should be removed here\n
\t\t\t}\n
\t\t\t// Use HTML5 File API: http://www.w3.org/TR/FileAPI/\n
\t\t\t// if browser has HTML5 File API support, then we will show the open menu item\n
\t\t\t// and provide a file input to click. When that change event fires, it will\n
\t\t\t// get the text contents of the file and send it to the canvas\n
\t\t\tif (window.FileReader) {\n
\t\t\t\tvar importImage = function(e) {\n
\t\t\t\t\t$.process_cancel(uiStrings.notification.loadingImage);\n
\t\t\t\t\te.stopPropagation();\n
\t\t\t\t\te.preventDefault();\n
\t\t\t\t\t$(\'#workarea\').removeAttr(\'style\');\n
\t\t\t\t\t$(\'#main_menu\').hide();\n
\t\t\t\t\tvar file = (e.type == \'drop\') ? e.dataTransfer.files[0] : this.files[0];\n
\t\t\t\t\tif (!file) {\n
\t\t\t\t\t\treturn;\n
\t\t\t\t\t}\n
\t\t\t\t\tif (file.type.indexOf(\'image\') != -1) {\n
\t\t\t\t\t\t// Detected an image\n
\t\t\t\t\t\t// svg handling\n
\t\t\t\t\t\tvar reader;\n
\t\t\t\t\t\tif (file.type.indexOf(\'svg\') != -1) {\n
\t\t\t\t\t\t\treader = new FileReader();\n
\t\t\t\t\t\t\treader.onloadend = function(e) {\n
\t\t\t\t\t\t\t\tsvgCanvas.importSvgString(e.target.result, true);\n
\t\t\t\t\t\t\t\tsvgCanvas.ungroupSelectedElement();\n
\t\t\t\t\t\t\t\tsvgCanvas.ungroupSelectedElement();\n
\t\t\t\t\t\t\t\tsvgCanvas.groupSelectedElements();\n
\t\t\t\t\t\t\t\tsvgCanvas.alignSelectedElements(\'m\', \'page\');\n
\t\t\t\t\t\t\t\tsvgCanvas.alignSelectedElements(\'c\', \'page\');\n
\t\t\t\t\t\t\t};\n
\t\t\t\t\t\t\treader.readAsText(file);\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t//bitmap handling\n
\t\t\t\t\t\t\treader = new FileReader();\n
\t\t\t\t\t\t\treader.onloadend = function(e) {\n
\t\t\t\t\t\t\t\t// let\'s insert the new image until we know its dimensions\n
\t\t\t\t\t\t\t\tvar insertNewImage = function(width, height) {\n
\t\t\t\t\t\t\t\t\tvar newImage = svgCanvas.addSvgElementFromJson({\n
\t\t\t\t\t\t\t\t\t\telement: \'image\',\n
\t\t\t\t\t\t\t\t\t\tattr: {\n
\t\t\t\t\t\t\t\t\t\t\tx: 0,\n
\t\t\t\t\t\t\t\t\t\t\ty: 0,\n
\t\t\t\t\t\t\t\t\t\t\twidth: width,\n
\t\t\t\t\t\t\t\t\t\t\theight: height,\n
\t\t\t\t\t\t\t\t\t\t\tid: svgCanvas.getNextId(),\n
\t\t\t\t\t\t\t\t\t\t\tstyle: \'pointer-events:inherit\'\n
\t\t\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\t\t});\n
\t\t\t\t\t\t\t\t\tsvgCanvas.setHref(newImage, e.target.result);\n
\t\t\t\t\t\t\t\t\tsvgCanvas.selectOnly([newImage]);\n
\t\t\t\t\t\t\t\t\tsvgCanvas.alignSelectedElements(\'m\', \'page\');\n
\t\t\t\t\t\t\t\t\tsvgCanvas.alignSelectedElements(\'c\', \'page\');\n
\t\t\t\t\t\t\t\t\tupdateContextPanel();\n
\t\t\t\t\t\t\t\t};\n
\t\t\t\t\t\t\t\t\t// create dummy img so we know the default dimensions\n
\t\t\t\t\t\t\t\tvar imgWidth = 100;\n
\t\t\t\t\t\t\t\tvar imgHeight = 100;\n
\t\t\t\t\t\t\t\tvar img = new Image();\n
\t\t\t\t\t\t\t\timg.src = e.target.result;\n
\t\t\t\t\t\t\t\timg.style.opacity = 0;\n
\t\t\t\t\t\t\t\timg.onload = function() {\n
\t\t\t\t\t\t\t\t\timgWidth = img.offsetWidth;\n
\t\t\t\t\t\t\t\t\timgHeight = img.offsetHeight;\n
\t\t\t\t\t\t\t\t\tinsertNewImage(imgWidth, imgHeight);\n
\t\t\t\t\t\t\t\t};\n
\t\t\t\t\t\t\t};\n
\t\t\t\t\t\t\treader.readAsDataURL(file);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t};\n
\n
\t\t\t\tworkarea[0].addEventListener(\'dragenter\', onDragEnter, false);\n
\t\t\t\tworkarea[0].addEventListener(\'dragover\', onDragOver, false);\n
\t\t\t\tworkarea[0].addEventListener(\'dragleave\', onDragLeave, false);\n
\t\t\t\tworkarea[0].addEventListener(\'drop\', importImage, false);\n
\n
\t\t\t\tvar open = $(\'<input type="file">\').change(function() {\n
\t\t\t\t\tvar f = this;\n
\t\t\t\t\teditor.openPrep(function(ok) {\n
\t\t\t\t\t\tif (!ok) {return;}\n
\t\t\t\t\t\tsvgCanvas.clear();\n
\t\t\t\t\t\tif (f.files.length==1) {\n
\t\t\t\t\t\t\t$.process_cancel(uiStrings.notification.loadingImage);\n
\t\t\t\t\t\t\tvar reader = new FileReader();\n
\t\t\t\t\t\t\treader.onloadend = function(e) {\n
\t\t\t\t\t\t\t\tloadSvgString(e.target.result);\n
\t\t\t\t\t\t\t\tupdateCanvas();\n
\t\t\t\t\t\t\t};\n
\t\t\t\t\t\t\treader.readAsText(f.files[0]);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t});\n
\t\t\t\t});\n
\t\t\t\t$(\'#tool_open\').show().prepend(open);\n
\n
\t\t\t\tvar imgImport = $(\'<input type="file">\').change(importImage);\n
\t\t\t\t$(\'#tool_import\').show().prepend(imgImport);\n
\t\t\t}\n
\n
//\t\t\t$(function() {\n
\t\t\t\tupdateCanvas(true);\n
//\t\t\t});\n
\n
\t\t//\tvar revnums = "svg-editor.js ($Rev: 2672 $) ";\n
\t\t//\trevnums += svgCanvas.getVersion();\n
\t\t//\t$(\'#copyright\')[0].setAttribute(\'title\', revnums);\n
\n
\t\t\t// Callback handler for embedapi.js\n
\t\t\ttry {\n
\t\t\t\twindow.addEventListener(\'message\', function(e) {\n
\t\t\t\t\t// We accept and post strings for the sake of IE9 support\n
\t\t\t\t\tif (typeof e.data !== \'string\' || e.data.charAt() === \'|\') {\n
\t\t\t\t\t\treturn;\n
\t\t\t\t\t}\n
\t\t\t\t\tvar data = JSON.parse(e.data);\n
\t\t\t\t\tif (!data || typeof data !== \'object\' || data.namespace !== \'svgCanvas\') {\n
\t\t\t\t\t\treturn;\n
\t\t\t\t\t}\n
\t\t\t\t\tvar cbid = data.id,\n
\t\t\t\t\t\tname = data.name,\n
\t\t\t\t\t\targs = data.args;\n
\t\t\t\t\ttry {\n
\t\t\t\t\t\te.source.postMessage(JSON.stringify({namespace: \'svg-edit\', id: cbid, result: svgCanvas[name].apply(svgCanvas, args)}), \'*\');\n
\t\t\t\t\t} catch(err) {\n
\t\t\t\t\t\te.source.postMessage(JSON.stringify({namespace: \'svg-edit\', id: cbid, error: err.message}), \'*\');\n
\t\t\t\t\t}\n
\t\t\t\t}, false);\n
\t\t\t} catch(err) {\n
\t\t\t\twindow.embed_error = err;\n
\t\t\t}\n
\n
\t\t\t// For Compatibility with older extensions\n
\t\t\t$(function() {\n
\t\t\t\twindow.svgCanvas = svgCanvas;\n
\t\t\t\tsvgCanvas.ready = svgEditor.ready;\n
\t\t\t});\n
\n
\t\t\teditor.setLang = function(lang, allStrings) {\n
\t\t\t\teditor.langChanged = true;\n
\t\t\t\t$.pref(\'lang\', lang);\n
\t\t\t\t$(\'#lang_select\').val(lang);\n
\t\t\t\tif (!allStrings) {\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\t\t\t\t// var notif = allStrings.notification; // Currently unused\n
\t\t\t\t// $.extend will only replace the given strings\n
\t\t\t\tvar oldLayerName = $(\'#layerlist tr.layersel td.layername\').text();\n
\t\t\t\tvar rename_layer = (oldLayerName == uiStrings.common.layer + \' 1\');\n
\n
\t\t\t\t$.extend(uiStrings, allStrings);\n
\t\t\t\tsvgCanvas.setUiStrings(allStrings);\n
\t\t\t\tActions.setTitles();\n
\n
\t\t\t\tif (rename_layer) {\n
\t\t\t\t\tsvgCanvas.renameCurrentLayer(uiStrings.common.layer + \' 1\');\n
\t\t\t\t\tpopulateLayers();\n
\t\t\t\t}\n
\n
\t\t\t\t// In case extensions loaded before the locale, now we execute a callback on them\n
\t\t\t\tif (extsPreLang.length) {\n
\t\t\t\t\twhile (extsPreLang.length) {\n
\t\t\t\t\t\tvar ext = extsPreLang.shift();\n
\t\t\t\t\t\text.langReady({lang: lang, uiStrings: uiStrings});\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\telse {\n
\t\t\t\t\tsvgCanvas.runExtensions(\'langReady\', {lang: lang, uiStrings: uiStrings});\n
\t\t\t\t}\n
\t\t\t\tsvgCanvas.runExtensions(\'langChanged\', lang);\n
\n
\t\t\t\t// Update flyout tooltips\n
\t\t\t\tsetFlyoutTitles();\n
\n
\t\t\t\t// Copy title for certain tool elements\n
\t\t\t\tvar elems = {\n
\t\t\t\t\t\'#stroke_color\': \'#tool_stroke .icon_label, #tool_stroke .color_block\',\n
\t\t\t\t\t\'#fill_color\': \'#tool_fill label, #tool_fill .color_block\',\n
\t\t\t\t\t\'#linejoin_miter\': \'#cur_linejoin\',\n
\t\t\t\t\t\'#linecap_butt\': \'#cur_linecap\'\n
\t\t\t\t};\n
\n
\t\t\t\t$.each(elems, function(source, dest) {\n
\t\t\t\t\t$(dest).attr(\'title\', $(source)[0].title);\n
\t\t\t\t});\n
\n
\t\t\t\t// Copy alignment titles\n
\t\t\t\t$(\'#multiselected_panel div[id^=tool_align]\').each(function() {\n
\t\t\t\t\t$(\'#tool_pos\' + this.id.substr(10))[0].title = this.title;\n
\t\t\t\t});\n
\t\t\t};\n
\t\t};\n
\n
\t\teditor.ready = function (cb) {\n
\t\t\tif (!isReady) {\n
\t\t\t\tcallbacks.push(cb);\n
\t\t\t} else {\n
\t\t\t\tcb();\n
\t\t\t}\n
\t\t};\n
\n
\t\teditor.runCallbacks = function () {\n
\t\t\t$.each(callbacks, function() {\n
\t\t\t\tthis();\n
\t\t\t});\n
\t\t\tisReady = true;\n
\t\t};\n
\n
\t\teditor.loadFromString = function (str) {\n
\t\t\teditor.ready(function() {\n
\t\t\t\tloadSvgString(str);\n
\t\t\t});\n
\t\t};\n
\n
\t\teditor.disableUI = function (featList) {\n
//\t\t\t$(function() {\n
//\t\t\t\t$(\'#tool_wireframe, #tool_image, #main_button, #tool_source, #sidepanels\').remove();\n
//\t\t\t\t$(\'#tools_top\').css(\'left\', 5);\n
//\t\t\t});\n
\t\t};\n
\n
\t\teditor.loadFromURL = function (url, opts) {\n
\t\t\tif (!opts) {opts = {};}\n
\n
\t\t\tvar cache = opts.cache;\n
\t\t\tvar cb = opts.callback;\n
\n
\t\t\teditor.ready(function() {\n
\t\t\t\t$.ajax({\n
\t\t\t\t\t\'url\': url,\n
\t\t\t\t\t\'dataType\': \'text\',\n
\t\t\t\t\tcache: !!cache,\n
\t\t\t\t\tbeforeSend:function(){\n
\t\t\t\t\t\t$.process_cancel(uiStrings.notification.loadingImage);\n
\t\t\t\t\t},\n
\t\t\t\t\tsuccess: function(str) {\n
\t\t\t\t\t\tloadSvgString(str, cb);\n
\t\t\t\t\t},\n
\t\t\t\t\terror: function(xhr, stat, err) {\n
\t\t\t\t\t\tif (xhr.status != 404 && xhr.responseText) {\n
\t\t\t\t\t\t\tloadSvgString(xhr.responseText, cb);\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t$.alert(uiStrings.notification.URLloadFail + \': \\n\' + err, cb);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t},\n
\t\t\t\t\tcomplete:function(){\n
\t\t\t\t\t\t$(\'#dialog_box\').hide();\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t});\n
\t\t};\n
\n
\t\teditor.loadFromDataURI = function(str) {\n
\t\t\teditor.ready(function() {\n
\t\t\t\tvar pre = \'data:image/svg+xml;base64,\';\n
\t\t\t\tvar src = str.substring(pre.length);\n
\t\t\t\tloadSvgString(svgedit.utilities.decode64(src));\n
\t\t\t});\n
\t\t};\n
\n
\t\teditor.addExtension = function () {\n
\t\t\tvar args = arguments;\n
\n
\t\t\t// Note that we don\'t want this on editor.ready since some extensions\n
\t\t\t// may want to run before then (like server_opensave).\n
\t\t\t$(function() {\n
\t\t\t\tif (svgCanvas) {svgCanvas.addExtension.apply(this, args);}\n
\t\t\t});\n
\t\t};\n
\n
\t\treturn editor;\n
\t}(jQuery));\n
\n
\t// Run init once DOM is loaded\n
\t$(svgEditor.init);\n
\n
}());\n


]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <none/>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
