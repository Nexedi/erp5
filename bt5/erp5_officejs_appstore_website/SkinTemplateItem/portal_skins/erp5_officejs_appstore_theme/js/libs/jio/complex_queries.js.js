/*
* Copyright 2013, Nexedi SA
* Released under the LGPL license.
* http://www.gnu.org/licenses/lgpl.html
*/

/**
 * Provides some function to use complex queries with item list
 *
 * @module complex_queries
 */
// define([module_name], [dependencies], module);
(function (dependencies, module) {
  "use strict";
  if (typeof define === 'function' && define.amd) {
    return define(dependencies, module);
  }
  if (typeof exports === 'object') {
    return module(exports);
  }
  window.complex_queries = {};
  module(window.complex_queries);
}(['exports'], function (to_export) {
  "use strict";

  /**
   * Add a secured (write permission denied) property to an object.
   *
   * @param  {Object} object The object to fill
   * @param  {String} key The object key where to store the property
   * @param  {Any} value The value to store
   */
  function _export(key, value) {
    Object.defineProperty(to_export, key, {
      "configurable": false,
      "enumerable": true,
      "writable": false,
      "value": value
    });
  }

/**
 * Parse a text request to a json query object tree
 *
 * @param  {String} string The string to parse
 * @return {Object} The json query tree
 */
function parseStringToObject(string) {


/*
	Default template driver for JS/CC generated parsers running as
	browser-based JavaScript/ECMAScript applications.
	
	WARNING: 	This parser template will not run as console and has lesser
				features for debugging than the console derivates for the
				various JavaScript platforms.
	
	Features:
	- Parser trace messages
	- Integrated panic-mode error recovery
	
	Written 2007, 2008 by Jan Max Meyer, J.M.K S.F. Software Technologies
	
	This is in the public domain.
*/

var NODEJS__dbg_withtrace		= false;
var NODEJS__dbg_string			= new String();

function __NODEJS_dbg_print( text )
{
	NODEJS__dbg_string += text + "\n";
}

function __NODEJS_lex( info )
{
	var state		= 0;
	var match		= -1;
	var match_pos	= 0;
	var start		= 0;
	var pos			= info.offset + 1;

	do
	{
		pos--;
		state = 0;
		match = -2;
		start = pos;

		if( info.src.length <= start )
			return 19;

		do
		{

switch( state )
{
	case 0:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 8 ) || ( info.src.charCodeAt( pos ) >= 10 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || info.src.charCodeAt( pos ) == 59 || ( info.src.charCodeAt( pos ) >= 63 && info.src.charCodeAt( pos ) <= 64 ) || ( info.src.charCodeAt( pos ) >= 66 && info.src.charCodeAt( pos ) <= 77 ) || ( info.src.charCodeAt( pos ) >= 80 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 9 ) state = 2;
		else if( info.src.charCodeAt( pos ) == 40 ) state = 3;
		else if( info.src.charCodeAt( pos ) == 41 ) state = 4;
		else if( info.src.charCodeAt( pos ) == 60 || info.src.charCodeAt( pos ) == 62 ) state = 5;
		else if( info.src.charCodeAt( pos ) == 34 ) state = 11;
		else if( info.src.charCodeAt( pos ) == 79 ) state = 12;
		else if( info.src.charCodeAt( pos ) == 32 ) state = 13;
		else if( info.src.charCodeAt( pos ) == 61 ) state = 14;
		else if( info.src.charCodeAt( pos ) == 65 ) state = 18;
		else if( info.src.charCodeAt( pos ) == 78 ) state = 19;
		else state = -1;
		break;

	case 1:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

	case 2:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else state = -1;
		match = 1;
		match_pos = pos;
		break;

	case 3:
		state = -1;
		match = 3;
		match_pos = pos;
		break;

	case 4:
		state = -1;
		match = 4;
		match_pos = pos;
		break;

	case 5:
		if( info.src.charCodeAt( pos ) == 61 ) state = 14;
		else state = -1;
		match = 11;
		match_pos = pos;
		break;

	case 6:
		state = -1;
		match = 8;
		match_pos = pos;
		break;

	case 7:
		state = -1;
		match = 9;
		match_pos = pos;
		break;

	case 8:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else state = -1;
		match = 6;
		match_pos = pos;
		break;

	case 9:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else state = -1;
		match = 5;
		match_pos = pos;
		break;

	case 10:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else state = -1;
		match = 7;
		match_pos = pos;
		break;

	case 11:
		if( info.src.charCodeAt( pos ) == 34 ) state = 7;
		else if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 33 ) || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 91 ) || ( info.src.charCodeAt( pos ) >= 93 && info.src.charCodeAt( pos ) <= 254 ) ) state = 11;
		else if( info.src.charCodeAt( pos ) == 92 ) state = 15;
		else state = -1;
		break;

	case 12:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 81 ) || ( info.src.charCodeAt( pos ) >= 83 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else if( info.src.charCodeAt( pos ) == 82 ) state = 8;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

	case 13:
		state = -1;
		match = 1;
		match_pos = pos;
		break;

	case 14:
		state = -1;
		match = 11;
		match_pos = pos;
		break;

	case 15:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 254 ) ) state = 11;
		else state = -1;
		break;

	case 16:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 67 ) || ( info.src.charCodeAt( pos ) >= 69 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else if( info.src.charCodeAt( pos ) == 68 ) state = 9;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

	case 17:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 83 ) || ( info.src.charCodeAt( pos ) >= 85 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else if( info.src.charCodeAt( pos ) == 84 ) state = 10;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

	case 18:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 77 ) || ( info.src.charCodeAt( pos ) >= 79 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else if( info.src.charCodeAt( pos ) == 78 ) state = 16;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

	case 19:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 78 ) || ( info.src.charCodeAt( pos ) >= 80 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else if( info.src.charCodeAt( pos ) == 79 ) state = 17;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

}


			pos++;

		}
		while( state > -1 );

	}
	while( 1 > -1 && match == 1 );

	if( match > -1 )
	{
		info.att = info.src.substr( start, match_pos - start );
		info.offset = match_pos;
		

	}
	else
	{
		info.att = new String();
		match = -1;
	}

	return match;
}


function __NODEJS_parse( src, err_off, err_la )
{
	var		sstack			= new Array();
	var		vstack			= new Array();
	var 	err_cnt			= 0;
	var		act;
	var		go;
	var		la;
	var		rval;
	var 	parseinfo		= new Function( "", "var offset; var src; var att;" );
	var		info			= new parseinfo();
	
/* Pop-Table */
var pop_tab = new Array(
	new Array( 0/* begin' */, 1 ),
	new Array( 13/* begin */, 1 ),
	new Array( 12/* search_text */, 1 ),
	new Array( 12/* search_text */, 2 ),
	new Array( 12/* search_text */, 3 ),
	new Array( 14/* and_expression */, 1 ),
	new Array( 14/* and_expression */, 3 ),
	new Array( 15/* boolean_expression */, 2 ),
	new Array( 15/* boolean_expression */, 1 ),
	new Array( 16/* expression */, 3 ),
	new Array( 16/* expression */, 2 ),
	new Array( 16/* expression */, 1 ),
	new Array( 17/* value */, 2 ),
	new Array( 17/* value */, 1 ),
	new Array( 18/* string */, 1 ),
	new Array( 18/* string */, 1 )
);

/* Action-Table */
var act_tab = new Array(
	/* State 0 */ new Array( 7/* "NOT" */,5 , 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 1 */ new Array( 19/* "$" */,0 ),
	/* State 2 */ new Array( 19/* "$" */,-1 ),
	/* State 3 */ new Array( 6/* "OR" */,14 , 7/* "NOT" */,5 , 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 , 19/* "$" */,-2 , 4/* "RIGHT_PARENTHESE" */,-2 ),
	/* State 4 */ new Array( 5/* "AND" */,16 , 19/* "$" */,-5 , 7/* "NOT" */,-5 , 3/* "LEFT_PARENTHESE" */,-5 , 8/* "COLUMN" */,-5 , 11/* "OPERATOR" */,-5 , 10/* "WORD" */,-5 , 9/* "STRING" */,-5 , 6/* "OR" */,-5 , 4/* "RIGHT_PARENTHESE" */,-5 ),
	/* State 5 */ new Array( 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 6 */ new Array( 19/* "$" */,-8 , 7/* "NOT" */,-8 , 3/* "LEFT_PARENTHESE" */,-8 , 8/* "COLUMN" */,-8 , 11/* "OPERATOR" */,-8 , 10/* "WORD" */,-8 , 9/* "STRING" */,-8 , 6/* "OR" */,-8 , 5/* "AND" */,-8 , 4/* "RIGHT_PARENTHESE" */,-8 ),
	/* State 7 */ new Array( 7/* "NOT" */,5 , 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 8 */ new Array( 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 9 */ new Array( 19/* "$" */,-11 , 7/* "NOT" */,-11 , 3/* "LEFT_PARENTHESE" */,-11 , 8/* "COLUMN" */,-11 , 11/* "OPERATOR" */,-11 , 10/* "WORD" */,-11 , 9/* "STRING" */,-11 , 6/* "OR" */,-11 , 5/* "AND" */,-11 , 4/* "RIGHT_PARENTHESE" */,-11 ),
	/* State 10 */ new Array( 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 11 */ new Array( 19/* "$" */,-13 , 7/* "NOT" */,-13 , 3/* "LEFT_PARENTHESE" */,-13 , 8/* "COLUMN" */,-13 , 11/* "OPERATOR" */,-13 , 10/* "WORD" */,-13 , 9/* "STRING" */,-13 , 6/* "OR" */,-13 , 5/* "AND" */,-13 , 4/* "RIGHT_PARENTHESE" */,-13 ),
	/* State 12 */ new Array( 19/* "$" */,-14 , 7/* "NOT" */,-14 , 3/* "LEFT_PARENTHESE" */,-14 , 8/* "COLUMN" */,-14 , 11/* "OPERATOR" */,-14 , 10/* "WORD" */,-14 , 9/* "STRING" */,-14 , 6/* "OR" */,-14 , 5/* "AND" */,-14 , 4/* "RIGHT_PARENTHESE" */,-14 ),
	/* State 13 */ new Array( 19/* "$" */,-15 , 7/* "NOT" */,-15 , 3/* "LEFT_PARENTHESE" */,-15 , 8/* "COLUMN" */,-15 , 11/* "OPERATOR" */,-15 , 10/* "WORD" */,-15 , 9/* "STRING" */,-15 , 6/* "OR" */,-15 , 5/* "AND" */,-15 , 4/* "RIGHT_PARENTHESE" */,-15 ),
	/* State 14 */ new Array( 7/* "NOT" */,5 , 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 15 */ new Array( 19/* "$" */,-3 , 4/* "RIGHT_PARENTHESE" */,-3 ),
	/* State 16 */ new Array( 7/* "NOT" */,5 , 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 17 */ new Array( 19/* "$" */,-7 , 7/* "NOT" */,-7 , 3/* "LEFT_PARENTHESE" */,-7 , 8/* "COLUMN" */,-7 , 11/* "OPERATOR" */,-7 , 10/* "WORD" */,-7 , 9/* "STRING" */,-7 , 6/* "OR" */,-7 , 5/* "AND" */,-7 , 4/* "RIGHT_PARENTHESE" */,-7 ),
	/* State 18 */ new Array( 4/* "RIGHT_PARENTHESE" */,23 ),
	/* State 19 */ new Array( 19/* "$" */,-10 , 7/* "NOT" */,-10 , 3/* "LEFT_PARENTHESE" */,-10 , 8/* "COLUMN" */,-10 , 11/* "OPERATOR" */,-10 , 10/* "WORD" */,-10 , 9/* "STRING" */,-10 , 6/* "OR" */,-10 , 5/* "AND" */,-10 , 4/* "RIGHT_PARENTHESE" */,-10 ),
	/* State 20 */ new Array( 19/* "$" */,-12 , 7/* "NOT" */,-12 , 3/* "LEFT_PARENTHESE" */,-12 , 8/* "COLUMN" */,-12 , 11/* "OPERATOR" */,-12 , 10/* "WORD" */,-12 , 9/* "STRING" */,-12 , 6/* "OR" */,-12 , 5/* "AND" */,-12 , 4/* "RIGHT_PARENTHESE" */,-12 ),
	/* State 21 */ new Array( 19/* "$" */,-4 , 4/* "RIGHT_PARENTHESE" */,-4 ),
	/* State 22 */ new Array( 19/* "$" */,-6 , 7/* "NOT" */,-6 , 3/* "LEFT_PARENTHESE" */,-6 , 8/* "COLUMN" */,-6 , 11/* "OPERATOR" */,-6 , 10/* "WORD" */,-6 , 9/* "STRING" */,-6 , 6/* "OR" */,-6 , 4/* "RIGHT_PARENTHESE" */,-6 ),
	/* State 23 */ new Array( 19/* "$" */,-9 , 7/* "NOT" */,-9 , 3/* "LEFT_PARENTHESE" */,-9 , 8/* "COLUMN" */,-9 , 11/* "OPERATOR" */,-9 , 10/* "WORD" */,-9 , 9/* "STRING" */,-9 , 6/* "OR" */,-9 , 5/* "AND" */,-9 , 4/* "RIGHT_PARENTHESE" */,-9 )
);

/* Goto-Table */
var goto_tab = new Array(
	/* State 0 */ new Array( 13/* begin */,1 , 12/* search_text */,2 , 14/* and_expression */,3 , 15/* boolean_expression */,4 , 16/* expression */,6 , 17/* value */,9 , 18/* string */,11 ),
	/* State 1 */ new Array(  ),
	/* State 2 */ new Array(  ),
	/* State 3 */ new Array( 12/* search_text */,15 , 14/* and_expression */,3 , 15/* boolean_expression */,4 , 16/* expression */,6 , 17/* value */,9 , 18/* string */,11 ),
	/* State 4 */ new Array(  ),
	/* State 5 */ new Array( 16/* expression */,17 , 17/* value */,9 , 18/* string */,11 ),
	/* State 6 */ new Array(  ),
	/* State 7 */ new Array( 12/* search_text */,18 , 14/* and_expression */,3 , 15/* boolean_expression */,4 , 16/* expression */,6 , 17/* value */,9 , 18/* string */,11 ),
	/* State 8 */ new Array( 16/* expression */,19 , 17/* value */,9 , 18/* string */,11 ),
	/* State 9 */ new Array(  ),
	/* State 10 */ new Array( 18/* string */,20 ),
	/* State 11 */ new Array(  ),
	/* State 12 */ new Array(  ),
	/* State 13 */ new Array(  ),
	/* State 14 */ new Array( 12/* search_text */,21 , 14/* and_expression */,3 , 15/* boolean_expression */,4 , 16/* expression */,6 , 17/* value */,9 , 18/* string */,11 ),
	/* State 15 */ new Array(  ),
	/* State 16 */ new Array( 14/* and_expression */,22 , 15/* boolean_expression */,4 , 16/* expression */,6 , 17/* value */,9 , 18/* string */,11 ),
	/* State 17 */ new Array(  ),
	/* State 18 */ new Array(  ),
	/* State 19 */ new Array(  ),
	/* State 20 */ new Array(  ),
	/* State 21 */ new Array(  ),
	/* State 22 */ new Array(  ),
	/* State 23 */ new Array(  )
);



/* Symbol labels */
var labels = new Array(
	"begin'" /* Non-terminal symbol */,
	"WHITESPACE" /* Terminal symbol */,
	"WHITESPACE" /* Terminal symbol */,
	"LEFT_PARENTHESE" /* Terminal symbol */,
	"RIGHT_PARENTHESE" /* Terminal symbol */,
	"AND" /* Terminal symbol */,
	"OR" /* Terminal symbol */,
	"NOT" /* Terminal symbol */,
	"COLUMN" /* Terminal symbol */,
	"STRING" /* Terminal symbol */,
	"WORD" /* Terminal symbol */,
	"OPERATOR" /* Terminal symbol */,
	"search_text" /* Non-terminal symbol */,
	"begin" /* Non-terminal symbol */,
	"and_expression" /* Non-terminal symbol */,
	"boolean_expression" /* Non-terminal symbol */,
	"expression" /* Non-terminal symbol */,
	"value" /* Non-terminal symbol */,
	"string" /* Non-terminal symbol */,
	"$" /* Terminal symbol */
);


	
	info.offset = 0;
	info.src = src;
	info.att = new String();
	
	if( !err_off )
		err_off	= new Array();
	if( !err_la )
	err_la = new Array();
	
	sstack.push( 0 );
	vstack.push( 0 );
	
	la = __NODEJS_lex( info );

	while( true )
	{
		act = 25;
		for( var i = 0; i < act_tab[sstack[sstack.length-1]].length; i+=2 )
		{
			if( act_tab[sstack[sstack.length-1]][i] == la )
			{
				act = act_tab[sstack[sstack.length-1]][i+1];
				break;
			}
		}

		if( NODEJS__dbg_withtrace && sstack.length > 0 )
		{
			__NODEJS_dbg_print( "\nState " + sstack[sstack.length-1] + "\n" +
							"\tLookahead: " + labels[la] + " (\"" + info.att + "\")\n" +
							"\tAction: " + act + "\n" + 
							"\tSource: \"" + info.src.substr( info.offset, 30 ) + ( ( info.offset + 30 < info.src.length ) ?
									"..." : "" ) + "\"\n" +
							"\tStack: " + sstack.join() + "\n" +
							"\tValue stack: " + vstack.join() + "\n" );
		}
		
			
		//Panic-mode: Try recovery when parse-error occurs!
		if( act == 25 )
		{
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "Error detected: There is no reduce or shift on the symbol " + labels[la] );
			
			err_cnt++;
			err_off.push( info.offset - info.att.length );			
			err_la.push( new Array() );
			for( var i = 0; i < act_tab[sstack[sstack.length-1]].length; i+=2 )
				err_la[err_la.length-1].push( labels[act_tab[sstack[sstack.length-1]][i]] );
			
			//Remember the original stack!
			var rsstack = new Array();
			var rvstack = new Array();
			for( var i = 0; i < sstack.length; i++ )
			{
				rsstack[i] = sstack[i];
				rvstack[i] = vstack[i];
			}
			
			while( act == 25 && la != 19 )
			{
				if( NODEJS__dbg_withtrace )
					__NODEJS_dbg_print( "\tError recovery\n" +
									"Current lookahead: " + labels[la] + " (" + info.att + ")\n" +
									"Action: " + act + "\n\n" );
				if( la == -1 )
					info.offset++;
					
				while( act == 25 && sstack.length > 0 )
				{
					sstack.pop();
					vstack.pop();
					
					if( sstack.length == 0 )
						break;
						
					act = 25;
					for( var i = 0; i < act_tab[sstack[sstack.length-1]].length; i+=2 )
					{
						if( act_tab[sstack[sstack.length-1]][i] == la )
						{
							act = act_tab[sstack[sstack.length-1]][i+1];
							break;
						}
					}
				}
				
				if( act != 25 )
					break;
				
				for( var i = 0; i < rsstack.length; i++ )
				{
					sstack.push( rsstack[i] );
					vstack.push( rvstack[i] );
				}
				
				la = __NODEJS_lex( info );
			}
			
			if( act == 25 )
			{
				if( NODEJS__dbg_withtrace )
					__NODEJS_dbg_print( "\tError recovery failed, terminating parse process..." );
				break;
			}


			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "\tError recovery succeeded, continuing" );
		}
		
		/*
		if( act == 25 )
			break;
		*/
		
		
		//Shift
		if( act > 0 )
		{			
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "Shifting symbol: " + labels[la] + " (" + info.att + ")" );
		
			sstack.push( act );
			vstack.push( info.att );
			
			la = __NODEJS_lex( info );
			
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "\tNew lookahead symbol: " + labels[la] + " (" + info.att + ")" );
		}
		//Reduce
		else
		{		
			act *= -1;
			
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "Reducing by producution: " + act );
			
			rval = void(0);
			
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "\tPerforming semantic action..." );
			
switch( act )
{
	case 0:
	{
		rval = vstack[ vstack.length - 1 ];
	}
	break;
	case 1:
	{
		 result = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 2:
	{
		 rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 3:
	{
		 rval = mkComplexQuery('OR',[vstack[ vstack.length - 2 ],vstack[ vstack.length - 1 ]]); 
	}
	break;
	case 4:
	{
		 rval = mkComplexQuery('OR',[vstack[ vstack.length - 3 ],vstack[ vstack.length - 1 ]]); 
	}
	break;
	case 5:
	{
		 rval = vstack[ vstack.length - 1 ] ; 
	}
	break;
	case 6:
	{
		 rval = mkComplexQuery('AND',[vstack[ vstack.length - 3 ],vstack[ vstack.length - 1 ]]); 
	}
	break;
	case 7:
	{
		 rval = mkNotQuery(vstack[ vstack.length - 1 ]); 
	}
	break;
	case 8:
	{
		 rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 9:
	{
		 rval = vstack[ vstack.length - 2 ]; 
	}
	break;
	case 10:
	{
		 simpleQuerySetKey(vstack[ vstack.length - 1 ],vstack[ vstack.length - 2 ].split(':').slice(0,-1).join(':')); rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 11:
	{
		 rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 12:
	{
		 vstack[ vstack.length - 1 ].operator = vstack[ vstack.length - 2 ] ; rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 13:
	{
		 rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 14:
	{
		 rval = mkSimpleQuery('',vstack[ vstack.length - 1 ]); 
	}
	break;
	case 15:
	{
		 rval = mkSimpleQuery('',vstack[ vstack.length - 1 ].split('"').slice(1,-1).join('"')); 
	}
	break;
}



			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "\tPopping " + pop_tab[act][1] + " off the stack..." );
				
			for( var i = 0; i < pop_tab[act][1]; i++ )
			{
				sstack.pop();
				vstack.pop();
			}
									
			go = -1;
			for( var i = 0; i < goto_tab[sstack[sstack.length-1]].length; i+=2 )
			{
				if( goto_tab[sstack[sstack.length-1]][i] == pop_tab[act][0] )
				{
					go = goto_tab[sstack[sstack.length-1]][i+1];
					break;
				}
			}
			
			if( act == 0 )
				break;
				
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "\tPushing non-terminal " + labels[ pop_tab[act][0] ] );
				
			sstack.push( go );
			vstack.push( rval );			
		}
		
		if( NODEJS__dbg_withtrace )
		{		
			alert( NODEJS__dbg_string );
			NODEJS__dbg_string = new String();
		}
	}

	if( NODEJS__dbg_withtrace )
	{
		__NODEJS_dbg_print( "\nParse complete." );
		alert( NODEJS__dbg_string );
	}
	
	return err_cnt;
}



var arrayExtend = function () {
  var j, i, newlist = [], list_list = arguments;
  for (j = 0; j < list_list.length; j += 1) {
    for (i = 0; i < list_list[j].length; i += 1) {
      newlist.push(list_list[j][i]);
    }
  }
  return newlist;

}, mkSimpleQuery = function (key, value, operator) {
  return {"type": "simple", "operator": "=", "key": key, "value": value};

}, mkNotQuery = function (query) {
  if (query.operator === "NOT") {
    return query.query_list[0];
  }
  return {"type": "complex", "operator": "NOT", "query_list": [query]};

}, mkComplexQuery = function (operator, query_list) {
  var i, query_list2 = [];
  for (i = 0; i < query_list.length; i += 1) {
    if (query_list[i].operator === operator) {
      query_list2 = arrayExtend(query_list2, query_list[i].query_list);
    } else {
      query_list2.push(query_list[i]);
    }
  }
  return {type:"complex",operator:operator,query_list:query_list2};

}, simpleQuerySetKey = function (query, key) {
  var i;
  if (query.type === "complex") {
    for (i = 0; i < query.query_list.length; ++i) {
      simpleQuerySetKey (query.query_list[i],key);
    }
    return true;
  }
  if (query.type === "simple" && !query.key) {
    query.key = key;
    return true;
  }
  return false;
},
  error_offsets = [],
  error_lookaheads = [],
  error_count = 0,
  result;

if ((error_count = __NODEJS_parse(string, error_offsets, error_lookaheads)) > 0) {
  var i;
  for (i = 0; i < error_count; i += 1) {
    throw new Error("Parse error near \"" +
                    string.substr(error_offsets[i]) +
                    "\", expecting \"" +
                    error_lookaheads[i].join() + "\"");
  }
}


  return result;
} // parseStringToObject

_export('parseStringToObject', parseStringToObject);

/*jslint indent: 2, maxlen: 80, sloppy: true */

var query_class_dict = {};

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global Query: true, query_class_dict: true, inherits: true,
         _export: true, QueryFactory: true */

/**
 * The ComplexQuery inherits from Query, and compares one or several metadata
 * values.
 *
 * @class ComplexQuery
 * @extends Query
 * @param  {Object} [spec={}] The specifications
 * @param  {String} [spec.operator="AND"] The compare method to use
 * @param  {String} spec.key The metadata key
 * @param  {String} spec.value The value of the metadata to compare
 */
function ComplexQuery(spec) {
  Query.call(this);

  /**
   * Logical operator to use to compare object values
   *
   * @attribute operator
   * @type String
   * @default "AND"
   * @optional
   */
  this.operator = spec.operator || "AND";

  /**
   * The sub Query list which are used to query an item.
   *
   * @attribute query_list
   * @type Array
   * @default []
   * @optional
   */
  this.query_list = spec.query_list || [];
  this.query_list = this.query_list.map(QueryFactory.create);

}
inherits(ComplexQuery, Query);

/**
 * #crossLink "Query/match:method"
 */
ComplexQuery.prototype.match = function (item, wildcard_character) {
  return this[this.operator](item, wildcard_character);
};

/**
 * #crossLink "Query/toString:method"
 */
ComplexQuery.prototype.toString = function () {
  var str_list = ["("], this_operator = this.operator;
  this.query_list.forEach(function (query) {
    str_list.push(query.toString());
    str_list.push(this_operator);
  });
  str_list.pop(); // remove last operator
  str_list.push(")");
  return str_list.join(" ");
};

/**
 * #crossLink "Query/serialized:method"
 */
ComplexQuery.prototype.serialized = function () {
  var s = {
    "type": "complex",
    "operator": this.operator,
    "query_list": []
  };
  this.query_list.forEach(function (query) {
    s.query_list.push(query.serialized());
  });
  return s;
};

/**
 * Comparison operator, test if all sub queries match the
 * item value
 *
 * @method AND
 * @param  {Object} item The item to match
 * @param  {String} wildcard_character The wildcard character
 * @return {Boolean} true if all match, false otherwise
 */
ComplexQuery.prototype.AND = function (item, wildcard_character) {
  var i;
  for (i = 0; i < this.query_list.length; i += 1) {
    if (!this.query_list[i].match(item, wildcard_character)) {
      return false;
    }
  }
  return true;
};

/**
 * Comparison operator, test if one of the sub queries matches the
 * item value
 *
 * @method OR
 * @param  {Object} item The item to match
 * @param  {String} wildcard_character The wildcard character
 * @return {Boolean} true if one match, false otherwise
 */
ComplexQuery.prototype.OR =  function (item, wildcard_character) {
  var i;
  for (i = 0; i < this.query_list.length; i += 1) {
    if (this.query_list[i].match(item, wildcard_character)) {
      return true;
    }
  }
  return false;
};

/**
 * Comparison operator, test if the sub query does not match the
 * item value
 *
 * @method NOT
 * @param  {Object} item The item to match
 * @param  {String} wildcard_character The wildcard character
 * @return {Boolean} true if one match, false otherwise
 */
ComplexQuery.prototype.NOT = function (item, wildcard_character) {
  return !this.query_list[0].match(item, wildcard_character);
};

query_class_dict.complex = ComplexQuery;

_export("ComplexQuery", ComplexQuery);

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global parseStringToObject: true, emptyFunction: true, sortOn: true, limit:
  true, select: true, _export: true, stringEscapeRegexpCharacters: true,
  deepClone: true */

/**
 * The query to use to filter a list of objects.
 * This is an abstract class.
 *
 * @class Query
 * @constructor
 */
function Query() {

  /**
   * Called before parsing the query. Must be overridden!
   *
   * @method onParseStart
   * @param  {Object} object The object shared in the parse process
   * @param  {Object} option Some option gave in parse()
   */
  this.onParseStart = emptyFunction;

  /**
   * Called when parsing a simple query. Must be overridden!
   *
   * @method onParseSimpleQuery
   * @param  {Object} object The object shared in the parse process
   * @param  {Object} option Some option gave in parse()
   */
  this.onParseSimpleQuery = emptyFunction;

  /**
   * Called when parsing a complex query. Must be overridden!
   *
   * @method onParseComplexQuery
   * @param  {Object} object The object shared in the parse process
   * @param  {Object} option Some option gave in parse()
   */
  this.onParseComplexQuery = emptyFunction;

  /**
   * Called after parsing the query. Must be overridden!
   *
   * @method onParseEnd
   * @param  {Object} object The object shared in the parse process
   * @param  {Object} option Some option gave in parse()
   */
  this.onParseEnd = emptyFunction;

}

/**
 * Filter the item list with matching item only
 *
 * @method exec
 * @param  {Array} item_list The list of object
 * @param  {Object} [option] Some operation option
 * @param  {String} [option.wildcard_character="%"] The wildcard character
 * @param  {Array} [option.select_list] A object keys to retrieve
 * @param  {Array} [option.sort_on] Couples of object keys and "ascending"
 *                 or "descending"
 * @param  {Array} [option.limit] Couple of integer, first is an index and
 *                 second is the length.
 */
Query.prototype.exec = function (item_list, option) {
  var i = 0;
  if (!Array.isArray(item_list)) {
    throw new TypeError("Query().exec(): Argument 1 is not of type 'array'");
  }
  if (option === undefined) {
    option = {};
  }
  if (typeof option !== 'object') {
    throw new TypeError("Query().exec(): " +
                        "Optional argument 2 is not of type 'object'");
  }
  if (option.wildcard_character === undefined) {
    option.wildcard_character = '%';
  }
  while (i < item_list.length) {
    if (!this.match(item_list[i], option.wildcard_character)) {
      item_list.splice(i, 1);
    } else {
      i += 1;
    }
  }
  if (option.sort_on) {
    sortOn(option.sort_on, item_list);
  }
  if (option.limit) {
    limit(option.limit, item_list);
  }
  select(option.select_list || [], item_list);
};

/**
 * Test if an item matches this query
 *
 * @method match
 * @param  {Object} item The object to test
 * @param  {String} wildcard_character The wildcard character to use
 * @return {Boolean} true if match, false otherwise
 */
Query.prototype.match = function () {
  return true;
};


/**
 * Browse the Query in deep calling parser method in each step.
 *
 * `onParseStart` is called first, on end `onParseEnd` is called.
 * It starts from the simple queries at the bottom of the tree calling the
 * parser method `onParseSimpleQuery`, and go up calling the
 * `onParseComplexQuery` method.
 *
 * @method parse
 * @param  {Object} option Any options you want (except 'parsed')
 * @return {Any} The parse result
 */
Query.prototype.parse = function (option) {
  var that = this, object;
  /**
   * The recursive parser.
   *
   * @param  {Object} object The object shared in the parse process
   * @param  {Object} options Some options usable in the parseMethods
   * @return {Any} The parser result
   */
  function recParse(object, option) {
    var i, query = object.parsed;
    if (query.type === "complex") {
      for (i = 0; i < query.query_list.length; i += 1) {
        object.parsed = query.query_list[i];
        recParse(object, option);
        query.query_list[i] = object.parsed;
      }
      object.parsed = query;
      that.onParseComplexQuery(object, option);
    } else if (query.type === "simple") {
      that.onParseSimpleQuery(object, option);
    }
  }
  object = {"parsed": JSON.parse(JSON.stringify(that.serialized()))};
  that.onParseStart(object, option);
  recParse(object, option);
  that.onParseEnd(object, option);
  return object.parsed;
};

/**
 * Convert this query to a parsable string.
 *
 * @method toString
 * @return {String} The string version of this query
 */
Query.prototype.toString = function () {
  return "";
};

/**
 * Convert this query to an jsonable object in order to be remake thanks to
 * QueryFactory class.
 *
 * @method serialized
 * @return {Object} The jsonable object
 */
Query.prototype.serialized = function () {
  return undefined;
};

_export("Query", Query);

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global _export, ComplexQuery, SimpleQuery, Query, parseStringToObject,
  query_class_dict */

/**
 * Provides static methods to create Query object
 *
 * @class QueryFactory
 */
function QueryFactory() {
  return;
}

/**
 * Creates Query object from a search text string or a serialized version
 * of a Query.
 *
 * @method create
 * @static
 * @param  {Object,String} object The search text or the serialized version
 *         of a Query
 * @return {Query} A Query object
 */
QueryFactory.create = function (object) {
  if (object === "") {
    return new Query();
  }
  if (typeof object === "string") {
    object = parseStringToObject(object);
  }
  if (typeof (object || {}).type === "string" &&
      query_class_dict[object.type]) {
    return new query_class_dict[object.type](object);
  }
  throw new TypeError("QueryFactory.create(): " +
                      "Argument 1 is not a search text or a parsable object");
};

_export("QueryFactory", QueryFactory);

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global _export: true, to_export: true */

function objectToSearchText(query) {
  var str_list = [];
  if (query.type === "complex") {
    str_list.push("(");
    (query.query_list || []).forEach(function (sub_query) {
      str_list.push(objectToSearchText(sub_query));
      str_list.push(query.operator);
    });
    str_list.length -= 1;
    str_list.push(")");
    return str_list.join(" ");
  }
  if (query.type === "simple") {
    return query.id + (query.id ? ": " : "") + (query.operator || "=") + ' "' +
      query.value + '"';
  }
  throw new TypeError("This object is not a query");
}
_export("objectToSearchText", objectToSearchText);

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global Query: true, inherits: true, query_class_dict: true, _export: true,
  convertStringToRegExp: true */

/**
 * The SimpleQuery inherits from Query, and compares one metadata value
 *
 * @class SimpleQuery
 * @extends Query
 * @param  {Object} [spec={}] The specifications
 * @param  {String} [spec.operator="="] The compare method to use
 * @param  {String} spec.key The metadata key
 * @param  {String} spec.value The value of the metadata to compare
 */
function SimpleQuery(spec) {
  Query.call(this);

  /**
   * Operator to use to compare object values
   *
   * @attribute operator
   * @type String
   * @default "="
   * @optional
   */
  this.operator = spec.operator || "=";

  /**
   * Key of the object which refers to the value to compare
   *
   * @attribute key
   * @type String
   */
  this.key = spec.key;

  /**
   * Value is used to do the comparison with the object value
   *
   * @attribute value
   * @type String
   */
  this.value = spec.value;

}
inherits(SimpleQuery, Query);

/**
 * #crossLink "Query/match:method"
 */
SimpleQuery.prototype.match = function (item, wildcard_character) {
  return this[this.operator](item[this.key], this.value, wildcard_character);
};

/**
 * #crossLink "Query/toString:method"
 */
SimpleQuery.prototype.toString = function () {
  return (this.key ? this.key + ": " : "") + (this.operator || "=") + ' "' +
    this.value + '"';
};

/**
 * #crossLink "Query/serialized:method"
 */
SimpleQuery.prototype.serialized = function () {
  return {
    "type": "simple",
    "operator": this.operator,
    "key": this.key,
    "value": this.value
  };
};

/**
 * Comparison operator, test if this query value matches the item value
 *
 * @method =
 * @param  {String} object_value The value to compare
 * @param  {String} comparison_value The comparison value
 * @param  {String} wildcard_character The wildcard_character
 * @return {Boolean} true if match, false otherwise
 */
SimpleQuery.prototype["="] = function (object_value, comparison_value,
                      wildcard_character) {
  var value, i;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  for (i = 0; i < object_value.length; i += 1) {
    value = object_value[i];
    if (typeof value === 'object') {
      value = value.content;
    }
    if (comparison_value === undefined) {
      if (value === undefined) {
        return true;
      }
      return false;
    }
    if (value === undefined) {
      return false;
    }
    if (
      convertStringToRegExp(
        comparison_value.toString(),
        wildcard_character
      ).test(value.toString())
    ) {
      return true;
    }
  }
  return false;
};

/**
 * Comparison operator, test if this query value does not match the item value
 *
 * @method !=
 * @param  {String} object_value The value to compare
 * @param  {String} comparison_value The comparison value
 * @param  {String} wildcard_character The wildcard_character
 * @return {Boolean} true if not match, false otherwise
 */
SimpleQuery.prototype["!="] = function (object_value, comparison_value,
                       wildcard_character) {
  var value, i;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  for (i = 0; i < object_value.length; i += 1) {
    value = object_value[i];
    if (typeof value === 'object') {
      value = value.content;
    }
    if (comparison_value === undefined) {
      if (value === undefined) {
        return false;
      }
      return true;
    }
    if (value === undefined) {
      return true;
    }
    if (
      convertStringToRegExp(
        comparison_value.toString(),
        wildcard_character
      ).test(value.toString())
    ) {
      return false;
    }
  }
  return true;
};

/**
 * Comparison operator, test if this query value is lower than the item value
 *
 * @method <
 * @param  {Number, String} object_value The value to compare
 * @param  {Number, String} comparison_value The comparison value
 * @return {Boolean} true if lower, false otherwise
 */
SimpleQuery.prototype["<"] = function (object_value, comparison_value) {
  var value;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  value = object_value[0];
  if (typeof value === 'object') {
    value = value.content;
  }
  return value < comparison_value;
};

/**
 * Comparison operator, test if this query value is equal or lower than the
 * item value
 *
 * @method <=
 * @param  {Number, String} object_value The value to compare
 * @param  {Number, String} comparison_value The comparison value
 * @return {Boolean} true if equal or lower, false otherwise
 */
SimpleQuery.prototype["<="] = function (object_value, comparison_value) {
  var value;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  value = object_value[0];
  if (typeof value === 'object') {
    value = value.content;
  }
  return value <= comparison_value;
};

/**
 * Comparison operator, test if this query value is greater than the item
 * value
 *
 * @method >
 * @param  {Number, String} object_value The value to compare
 * @param  {Number, String} comparison_value The comparison value
 * @return {Boolean} true if greater, false otherwise
 */
SimpleQuery.prototype[">"] = function (object_value, comparison_value) {
  var value;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  value = object_value[0];
  if (typeof value === 'object') {
    value = value.content;
  }
  return value > comparison_value;
};

/**
 * Comparison operator, test if this query value is equal or greater than the
 * item value
 *
 * @method >=
 * @param  {Number, String} object_value The value to compare
 * @param  {Number, String} comparison_value The comparison value
 * @return {Boolean} true if equal or greater, false otherwise
 */
SimpleQuery.prototype[">="] = function (object_value, comparison_value) {
  var value;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  value = object_value[0];
  if (typeof value === 'object') {
    value = value.content;
  }
  return value >= comparison_value;
};

query_class_dict.simple = SimpleQuery;

_export("SimpleQuery", SimpleQuery);

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global _export: true */

/**
 * Escapes regexp special chars from a string.
 *
 * @param  {String} string The string to escape
 * @return {String} The escaped string
 */
function stringEscapeRegexpCharacters(string) {
  if (typeof string === "string") {
    return string.replace(/([\\\.\$\[\]\(\)\{\}\^\?\*\+\-])/g, "\\$1");
  }
  throw new TypeError("complex_queries.stringEscapeRegexpCharacters(): " +
                      "Argument no 1 is not of type 'string'");
}

_export("stringEscapeRegexpCharacters", stringEscapeRegexpCharacters);

/**
 * Convert metadata values to array of strings. ex:
 *
 *     "a" -> ["a"],
 *     {"content": "a"} -> ["a"]
 *
 * @param  {Any} value The metadata value
 * @return {Array} The value in string array format
 */
function metadataValueToStringArray(value) {
  var i, new_value = [];
  if (value === undefined) {
    return undefined;
  }
  if (!Array.isArray(value)) {
    value = [value];
  }
  for (i = 0; i < value.length; i += 1) {
    if (typeof value[i] === 'object') {
      new_value[i] = value[i].content;
    } else {
      new_value[i] = value[i];
    }
  }
  return new_value;
}

/**
 * A sort function to sort items by key
 *
 * @param  {String} key The key to sort on
 * @param  {String} [way="ascending"] 'ascending' or 'descending'
 * @return {Function} The sort function
 */
function sortFunction(key, way) {
  if (way === 'descending') {
    return function (a, b) {
      // this comparison is 5 times faster than json comparison
      var i, l;
      a = metadataValueToStringArray(a[key]) || [];
      b = metadataValueToStringArray(b[key]) || [];
      l = a.length > b.length ? a.length : b.length;
      for (i = 0; i < l; i += 1) {
        if (a[i] === undefined) {
          return 1;
        }
        if (b[i] === undefined) {
          return -1;
        }
        if (a[i] > b[i]) {
          return -1;
        }
        if (a[i] < b[i]) {
          return 1;
        }
      }
      return 0;
    };
  }
  if (way === 'ascending') {
    return function (a, b) {
      // this comparison is 5 times faster than json comparison
      var i, l;
      a = metadataValueToStringArray(a[key]) || [];
      b = metadataValueToStringArray(b[key]) || [];
      l = a.length > b.length ? a.length : b.length;
      for (i = 0; i < l; i += 1) {
        if (a[i] === undefined) {
          return -1;
        }
        if (b[i] === undefined) {
          return 1;
        }
        if (a[i] > b[i]) {
          return 1;
        }
        if (a[i] < b[i]) {
          return -1;
        }
      }
      return 0;
    };
  }
  throw new TypeError("complex_queries.sortFunction(): " +
                      "Argument 2 must be 'ascending' or 'descending'");
}

/**
 * Clones all native object in deep. Managed types: Object, Array, String,
 * Number, Boolean, null.
 *
 * @param  {A} object The object to clone
 * @return {A} The cloned object
 */
function deepClone(object) {
  var i, cloned;
  if (Array.isArray(object)) {
    cloned = [];
    for (i = 0; i < object.length; i += 1) {
      cloned[i] = deepClone(object[i]);
    }
    return cloned;
  }
  if (typeof object === "object") {
    cloned = {};
    for (i in object) {
      if (object.hasOwnProperty(i)) {
        cloned[i] = deepClone(object[i]);
      }
    }
    return cloned;
  }
  return object;
}

/**
 * Inherits the prototype methods from one constructor into another. The
 * prototype of `constructor` will be set to a new object created from
 * `superConstructor`.
 *
 * @param  {Function} constructor The constructor which inherits the super one
 * @param  {Function} superConstructor The super constructor
 */
function inherits(constructor, superConstructor) {
  constructor.super_ = superConstructor;
  constructor.prototype = Object.create(superConstructor.prototype, {
    "constructor": {
      "configurable": true,
      "enumerable": false,
      "writable": true,
      "value": constructor
    }
  });
}

/**
 * Does nothing
 */
function emptyFunction() {
  return;
}

/**
 * Filter a list of items, modifying them to select only wanted keys. If
 * `clone` is true, then the method will act on a cloned list.
 *
 * @param  {Array} select_option Key list to keep
 * @param  {Array} list The item list to filter
 * @param  {Boolean} [clone=false] If true, modifies a clone of the list
 * @return {Array} The filtered list
 */
function select(select_option, list, clone) {
  var i, j, new_item;
  if (!Array.isArray(select_option)) {
    throw new TypeError("complex_queries.select(): " +
                        "Argument 1 is not of type Array");
  }
  if (!Array.isArray(list)) {
    throw new TypeError("complex_queries.select(): " +
                        "Argument 2 is not of type Array");
  }
  if (clone === true) {
    list = deepClone(list);
  }
  for (i = 0; i < list.length; i += 1) {
    new_item = {};
    for (j = 0; j < select_option.length; j += 1) {
      new_item[select_option[j]] = list[i][select_option[j]];
    }
    for (j in new_item) {
      if (new_item.hasOwnProperty(j)) {
        list[i] = new_item;
        break;
      }
    }
  }
  return list;
}

_export('select', select);

/**
 * Sort a list of items, according to keys and directions. If `clone` is true,
 * then the method will act on a cloned list.
 *
 * @param  {Array} sort_on_option List of couples [key, direction]
 * @param  {Array} list The item list to sort
 * @param  {Boolean} [clone=false] If true, modifies a clone of the list
 * @return {Array} The filtered list
 */
function sortOn(sort_on_option, list, clone) {
  var sort_index;
  if (!Array.isArray(sort_on_option)) {
    throw new TypeError("complex_queries.sortOn(): " +
                        "Argument 1 is not of type 'array'");
  }
  if (clone) {
    list = deepClone(list);
  }
  for (sort_index = sort_on_option.length - 1; sort_index >= 0;
       sort_index -= 1) {
    list.sort(sortFunction(
      sort_on_option[sort_index][0],
      sort_on_option[sort_index][1]
    ));
  }
  return list;
}

_export('sortOn', sortOn);

/**
 * Limit a list of items, according to index and length. If `clone` is true,
 * then the method will act on a cloned list.
 *
 * @param  {Array} limit_option A couple [from, length]
 * @param  {Array} list The item list to limit
 * @param  {Boolean} [clone=false] If true, modifies a clone of the list
 * @return {Array} The filtered list
 */
function limit(limit_option, list, clone) {
  if (!Array.isArray(limit_option)) {
    throw new TypeError("complex_queries.limit(): " +
                        "Argument 1 is not of type 'array'");
  }
  if (!Array.isArray(list)) {
    throw new TypeError("complex_queries.limit(): " +
                        "Argument 2 is not of type 'array'");
  }
  if (clone) {
    list = deepClone(list);
  }
  list.splice(0, limit_option[0]);
  if (limit_option[1]) {
    list.splice(limit_option[1]);
  }
  return list;
}

_export('limit', limit);

/**
 * Convert a search text to a regexp.
 *
 * @param  {String} string The string to convert
 * @param  {String} [wildcard_character=undefined] The wildcard chararter
 * @return {RegExp} The search text regexp
 */
function convertStringToRegExp(string, wildcard_character) {
  if (typeof string !== 'string') {
    throw new TypeError("complex_queries.convertStringToRegExp(): " +
                        "Argument 1 is not of type 'string'");
  }
  if (wildcard_character === undefined ||
      wildcard_character === null || wildcard_character === '') {
    return new RegExp("^" + stringEscapeRegexpCharacters(string) + "$");
  }
  if (typeof wildcard_character !== 'string' || wildcard_character.length > 1) {
    throw new TypeError("complex_queries.convertStringToRegExp(): " +
                        "Optional argument 2 must be a string of length <= 1");
  }
  return new RegExp("^" + stringEscapeRegexpCharacters(string).replace(
    new RegExp(stringEscapeRegexpCharacters(wildcard_character), 'g'),
    '.*'
  ) + "$");
}

_export('convertStringToRegExp', convertStringToRegExp);


  return to_export;
}));
