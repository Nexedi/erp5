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
            <value> <string>ts40515059.58</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>units.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals $, svgedit*/\n
/*jslint vars: true, eqeq: true*/\n
/**\n
 * Package: svgedit.units\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Alexis Deveria\n
 * Copyright(c) 2010 Jeff Schiller\n
 */\n
\n
// Dependencies:\n
// 1) jQuery\n
\n
(function() {\'use strict\';\n
\n
if (!svgedit.units) {\n
\tsvgedit.units = {};\n
}\n
\n
var NS = svgedit.NS;\n
var wAttrs = [\'x\', \'x1\', \'cx\', \'rx\', \'width\'];\n
var hAttrs = [\'y\', \'y1\', \'cy\', \'ry\', \'height\'];\n
var unitAttrs = [\'r\', \'radius\'].concat(wAttrs, hAttrs);\n
// unused\n
var unitNumMap = {\n
\t\'%\':  2,\n
\t\'em\': 3,\n
\t\'ex\': 4,\n
\t\'px\': 5,\n
\t\'cm\': 6,\n
\t\'mm\': 7,\n
\t\'in\': 8,\n
\t\'pt\': 9,\n
\t\'pc\': 10\n
};\n
\n
// Container of elements.\n
var elementContainer_;\n
\n
/**\n
 * Stores mapping of unit type to user coordinates.\n
 */\n
var typeMap_ = {};\n
\n
/**\n
 * ElementContainer interface\n
 *\n
 * function getBaseUnit() - returns a string of the base unit type of the container (\'em\')\n
 * function getElement() - returns an element in the container given an id\n
 * function getHeight() - returns the container\'s height\n
 * function getWidth() - returns the container\'s width\n
 * function getRoundDigits() - returns the number of digits number should be rounded to\n
 */\n
\n
/**\n
 * Function: svgedit.units.init()\n
 * Initializes this module.\n
 *\n
 * Parameters:\n
 * elementContainer - an object implementing the ElementContainer interface.\n
 */\n
svgedit.units.init = function(elementContainer) {\n
\telementContainer_ = elementContainer;\n
\n
\t// Get correct em/ex values by creating a temporary SVG.\n
\tvar svg = document.createElementNS(NS.SVG, \'svg\');\n
\tdocument.body.appendChild(svg);\n
\tvar rect = document.createElementNS(NS.SVG, \'rect\');\n
\trect.setAttribute(\'width\', \'1em\');\n
\trect.setAttribute(\'height\', \'1ex\');\n
\trect.setAttribute(\'x\', \'1in\');\n
\tsvg.appendChild(rect);\n
\tvar bb = rect.getBBox();\n
\tdocument.body.removeChild(svg);\n
\n
\tvar inch = bb.x;\n
\ttypeMap_ = {\n
\t\t\'em\': bb.width,\n
\t\t\'ex\': bb.height,\n
\t\t\'in\': inch,\n
\t\t\'cm\': inch / 2.54,\n
\t\t\'mm\': inch / 25.4,\n
\t\t\'pt\': inch / 72,\n
\t\t\'pc\': inch / 6,\n
\t\t\'px\': 1,\n
\t\t\'%\': 0\n
\t};\n
};\n
\n
// Group: Unit conversion functions\n
\n
// Function: svgedit.units.getTypeMap\n
// Returns the unit object with values for each unit\n
svgedit.units.getTypeMap = function() {\n
\treturn typeMap_;\n
};\n
\n
// Function: svgedit.units.shortFloat\n
// Rounds a given value to a float with number of digits defined in save_options\n
//\n
// Parameters:\n
// val - The value as a String, Number or Array of two numbers to be rounded\n
//\n
// Returns:\n
// If a string/number was given, returns a Float. If an array, return a string\n
// with comma-seperated floats\n
svgedit.units.shortFloat = function(val) {\n
\tvar digits = elementContainer_.getRoundDigits();\n
\tif (!isNaN(val)) {\n
\t\t// Note that + converts to Number\n
\t\treturn +((+val).toFixed(digits));\n
\t}\n
\tif ($.isArray(val)) {\n
\t\treturn svgedit.units.shortFloat(val[0]) + \',\' + svgedit.units.shortFloat(val[1]);\n
\t}\n
\treturn parseFloat(val).toFixed(digits) - 0;\n
};\n
\n
// Function: svgedit.units.convertUnit\n
// Converts the number to given unit or baseUnit\n
svgedit.units.convertUnit = function(val, unit) {\n
\tunit = unit || elementContainer_.getBaseUnit();\n
//\tbaseVal.convertToSpecifiedUnits(unitNumMap[unit]);\n
//\tvar val = baseVal.valueInSpecifiedUnits;\n
//\tbaseVal.convertToSpecifiedUnits(1);\n
\treturn svgedit.units.shortFloat(val / typeMap_[unit]);\n
};\n
\n
// Function: svgedit.units.setUnitAttr\n
// Sets an element\'s attribute based on the unit in its current value.\n
//\n
// Parameters:\n
// elem - DOM element to be changed\n
// attr - String with the name of the attribute associated with the value\n
// val - String with the attribute value to convert\n
svgedit.units.setUnitAttr = function(elem, attr, val) {\n
//\tif (!isNaN(val)) {\n
\t\t// New value is a number, so check currently used unit\n
//\t\tvar old_val = elem.getAttribute(attr);\n
\n
\t\t// Enable this for alternate mode\n
//\t\tif (old_val !== null && (isNaN(old_val) || elementContainer_.getBaseUnit() !== \'px\')) {\n
//\t\t\t// Old value was a number, so get unit, then convert\n
//\t\t\tvar unit;\n
//\t\t\tif (old_val.substr(-1) === \'%\') {\n
//\t\t\t\tvar res = getResolution();\n
//\t\t\t\tunit = \'%\';\n
//\t\t\t\tval *= 100;\n
//\t\t\t\tif (wAttrs.indexOf(attr) >= 0) {\n
//\t\t\t\t\tval = val / res.w;\n
//\t\t\t\t} else if (hAttrs.indexOf(attr) >= 0) {\n
//\t\t\t\t\tval = val / res.h;\n
//\t\t\t\t} else {\n
//\t\t\t\t\treturn val / Math.sqrt((res.w*res.w) + (res.h*res.h))/Math.sqrt(2);\n
//\t\t\t\t}\n
//\t\t\t} else {\n
//\t\t\t\tif (elementContainer_.getBaseUnit() !== \'px\') {\n
//\t\t\t\t\tunit = elementContainer_.getBaseUnit();\n
//\t\t\t\t} else {\n
//\t\t\t\t\tunit = old_val.substr(-2);\n
//\t\t\t\t}\n
//\t\t\t\tval = val / typeMap_[unit];\n
//\t\t\t}\n
//\n
//\t\tval += unit;\n
//\t\t}\n
//\t}\n
\telem.setAttribute(attr, val);\n
};\n
\n
var attrsToConvert = {\n
\t\'line\': [\'x1\', \'x2\', \'y1\', \'y2\'],\n
\t\'circle\': [\'cx\', \'cy\', \'r\'],\n
\t\'ellipse\': [\'cx\', \'cy\', \'rx\', \'ry\'],\n
\t\'foreignObject\': [\'x\', \'y\', \'width\', \'height\'],\n
\t\'rect\': [\'x\', \'y\', \'width\', \'height\'],\n
\t\'image\': [\'x\', \'y\', \'width\', \'height\'],\n
\t\'use\': [\'x\', \'y\', \'width\', \'height\'],\n
\t\'text\': [\'x\', \'y\']\n
};\n
\n
// Function: svgedit.units.convertAttrs\n
// Converts all applicable attributes to the configured baseUnit\n
//\n
// Parameters:\n
// element - a DOM element whose attributes should be converted\n
svgedit.units.convertAttrs = function(element) {\n
\tvar elName = element.tagName;\n
\tvar unit = elementContainer_.getBaseUnit();\n
\tvar attrs = attrsToConvert[elName];\n
\tif (!attrs) {return;}\n
\n
\tvar len = attrs.length;\n
\tvar i;\n
\tfor (i = 0; i < len; i++) {\n
\t\tvar attr = attrs[i];\n
\t\tvar cur = element.getAttribute(attr);\n
\t\tif (cur) {\n
\t\t\tif (!isNaN(cur)) {\n
\t\t\t\telement.setAttribute(attr, (cur / typeMap_[unit]) + unit);\n
\t\t\t}\n
\t\t\t// else {\n
\t\t\t\t// Convert existing?\n
\t\t\t// }\n
\t\t}\n
\t}\n
};\n
\n
// Function: svgedit.units.convertToNum\n
// Converts given values to numbers. Attributes must be supplied in \n
// case a percentage is given\n
//\n
// Parameters:\n
// attr - String with the name of the attribute associated with the value\n
// val - String with the attribute value to convert\n
svgedit.units.convertToNum = function(attr, val) {\n
\t// Return a number if that\'s what it already is\n
\tif (!isNaN(val)) {return val-0;}\n
\tvar num;\n
\tif (val.substr(-1) === \'%\') {\n
\t\t// Deal with percentage, depends on attribute\n
\t\tnum = val.substr(0, val.length-1)/100;\n
\t\tvar width = elementContainer_.getWidth();\n
\t\tvar height = elementContainer_.getHeight();\n
\n
\t\tif (wAttrs.indexOf(attr) >= 0) {\n
\t\t\treturn num * width;\n
\t\t}\n
\t\tif (hAttrs.indexOf(attr) >= 0) {\n
\t\t\treturn num * height;\n
\t\t}\n
\t\treturn num * Math.sqrt((width*width) + (height*height))/Math.sqrt(2);\n
\t}\n
\tvar unit = val.substr(-2);\n
\tnum = val.substr(0, val.length-2);\n
\t// Note that this multiplication turns the string into a number\n
\treturn num * typeMap_[unit];\n
};\n
\n
// Function: svgedit.units.isValidUnit\n
// Check if an attribute\'s value is in a valid format\n
//\n
// Parameters:\n
// attr - String with the name of the attribute associated with the value\n
// val - String with the attribute value to check\n
svgedit.units.isValidUnit = function(attr, val, selectedElement) {\n
\tvar valid = false;\n
\tif (unitAttrs.indexOf(attr) >= 0) {\n
\t\t// True if it\'s just a number\n
\t\tif (!isNaN(val)) {\n
\t\t\tvalid = true;\n
\t\t} else {\n
\t\t// Not a number, check if it has a valid unit\n
\t\t\tval = val.toLowerCase();\n
\t\t\t$.each(typeMap_, function(unit) {\n
\t\t\t\tif (valid) {return;}\n
\t\t\t\tvar re = new RegExp(\'^-?[\\\\d\\\\.]+\' + unit + \'$\');\n
\t\t\t\tif (re.test(val)) {valid = true;}\n
\t\t\t});\n
\t\t}\n
\t} else if (attr == \'id\') {\n
\t\t// if we\'re trying to change the id, make sure it\'s not already present in the doc\n
\t\t// and the id value is valid.\n
\n
\t\tvar result = false;\n
\t\t// because getElem() can throw an exception in the case of an invalid id\n
\t\t// (according to http://www.w3.org/TR/xml-id/ IDs must be a NCName)\n
\t\t// we wrap it in an exception and only return true if the ID was valid and\n
\t\t// not already present\n
\t\ttry {\n
\t\t\tvar elem = elementContainer_.getElement(val);\n
\t\t\tresult = (elem == null || elem === selectedElement);\n
\t\t} catch(e) {}\n
\t\treturn result;\n
\t}\n
\tvalid = true;\n
\n
\treturn valid;\n
};\n
\n
}());

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>7787</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
