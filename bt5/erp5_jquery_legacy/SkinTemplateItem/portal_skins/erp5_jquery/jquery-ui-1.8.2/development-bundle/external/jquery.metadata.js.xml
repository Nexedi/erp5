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
            <value> <string>ts77895651.73</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.metadata.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * Metadata - jQuery plugin for parsing metadata from elements\n
 *\n
 * Copyright (c) 2006 John Resig, Yehuda Katz, J�örn Zaefferer, Paul McLanahan\n
 *\n
 * Dual licensed under the MIT and GPL licenses:\n
 *   http://www.opensource.org/licenses/mit-license.php\n
 *   http://www.gnu.org/licenses/gpl.html\n
 *\n
 * Revision: $Id: jquery.metadata.js 4187 2007-12-16 17:15:27Z joern.zaefferer $\n
 *\n
 */\n
\n
/**\n
 * Sets the type of metadata to use. Metadata is encoded in JSON, and each property\n
 * in the JSON will become a property of the element itself.\n
 *\n
 * There are three supported types of metadata storage:\n
 *\n
 *   attr:  Inside an attribute. The name parameter indicates *which* attribute.\n
 *          \n
 *   class: Inside the class attribute, wrapped in curly braces: { }\n
 *   \n
 *   elem:  Inside a child element (e.g. a script tag). The\n
 *          name parameter indicates *which* element.\n
 *          \n
 * The metadata for an element is loaded the first time the element is accessed via jQuery.\n
 *\n
 * As a result, you can define the metadata type, use $(expr) to load the metadata into the elements\n
 * matched by expr, then redefine the metadata type and run another $(expr) for other elements.\n
 * \n
 * @name $.metadata.setType\n
 *\n
 * @example <p id="one" class="some_class {item_id: 1, item_label: \'Label\'}">This is a p</p>\n
 * @before $.metadata.setType("class")\n
 * @after $("#one").metadata().item_id == 1; $("#one").metadata().item_label == "Label"\n
 * @desc Reads metadata from the class attribute\n
 * \n
 * @example <p id="one" class="some_class" data="{item_id: 1, item_label: \'Label\'}">This is a p</p>\n
 * @before $.metadata.setType("attr", "data")\n
 * @after $("#one").metadata().item_id == 1; $("#one").metadata().item_label == "Label"\n
 * @desc Reads metadata from a "data" attribute\n
 * \n
 * @example <p id="one" class="some_class"><script>{item_id: 1, item_label: \'Label\'}</script>This is a p</p>\n
 * @before $.metadata.setType("elem", "script")\n
 * @after $("#one").metadata().item_id == 1; $("#one").metadata().item_label == "Label"\n
 * @desc Reads metadata from a nested script element\n
 * \n
 * @param String type The encoding type\n
 * @param String name The name of the attribute to be used to get metadata (optional)\n
 * @cat Plugins/Metadata\n
 * @descr Sets the type of encoding to be used when loading metadata for the first time\n
 * @type undefined\n
 * @see metadata()\n
 */\n
\n
(function($) {\n
\n
$.extend({\n
\tmetadata : {\n
\t\tdefaults : {\n
\t\t\ttype: \'class\',\n
\t\t\tname: \'metadata\',\n
\t\t\tcre: /({.*})/,\n
\t\t\tsingle: \'metadata\'\n
\t\t},\n
\t\tsetType: function( type, name ){\n
\t\t\tthis.defaults.type = type;\n
\t\t\tthis.defaults.name = name;\n
\t\t},\n
\t\tget: function( elem, opts ){\n
\t\t\tvar settings = $.extend({},this.defaults,opts);\n
\t\t\t// check for empty string in single property\n
\t\t\tif ( !settings.single.length ) settings.single = \'metadata\';\n
\t\t\t\n
\t\t\tvar data = $.data(elem, settings.single);\n
\t\t\t// returned cached data if it already exists\n
\t\t\tif ( data ) return data;\n
\t\t\t\n
\t\t\tdata = "{}";\n
\t\t\t\n
\t\t\tif ( settings.type == "class" ) {\n
\t\t\t\tvar m = settings.cre.exec( elem.className );\n
\t\t\t\tif ( m )\n
\t\t\t\t\tdata = m[1];\n
\t\t\t} else if ( settings.type == "elem" ) {\n
\t\t\t\tif( !elem.getElementsByTagName )\n
\t\t\t\t\treturn undefined;\n
\t\t\t\tvar e = elem.getElementsByTagName(settings.name);\n
\t\t\t\tif ( e.length )\n
\t\t\t\t\tdata = $.trim(e[0].innerHTML);\n
\t\t\t} else if ( elem.getAttribute != undefined ) {\n
\t\t\t\tvar attr = elem.getAttribute( settings.name );\n
\t\t\t\tif ( attr )\n
\t\t\t\t\tdata = attr;\n
\t\t\t}\n
\t\t\t\n
\t\t\tif ( data.indexOf( \'{\' ) <0 )\n
\t\t\tdata = "{" + data + "}";\n
\t\t\t\n
\t\t\tdata = eval("(" + data + ")");\n
\t\t\t\n
\t\t\t$.data( elem, settings.single, data );\n
\t\t\treturn data;\n
\t\t}\n
\t}\n
});\n
\n
/**\n
 * Returns the metadata object for the first member of the jQuery object.\n
 *\n
 * @name metadata\n
 * @descr Returns element\'s metadata object\n
 * @param Object opts An object contianing settings to override the defaults\n
 * @type jQuery\n
 * @cat Plugins/Metadata\n
 */\n
$.fn.metadata = function( opts ){\n
\treturn $.metadata.get( this[0], opts );\n
};\n
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
            <value> <int>3955</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
