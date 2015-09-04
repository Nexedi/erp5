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
            <value> <string>ts40515059.47</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ext-shapes.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals svgEditor, $, DOMParser*/\n
/*jslint es5: true, vars: true, eqeq: true*/\n
/*\n
 * ext-shapes.js\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Christian Tzurcanu\n
 * Copyright(c) 2010 Alexis Deveria\n
 *\n
 */\n
\n
svgEditor.addExtension(\'shapes\', function() {\'use strict\';\n
\tvar current_d, cur_shape_id;\n
\tvar canv = svgEditor.canvas;\n
\tvar cur_shape;\n
\tvar start_x, start_y;\n
\tvar svgroot = canv.getRootElem();\n
\tvar lastBBox = {};\n
\n
\t// This populates the category list\n
\tvar categories = {\n
\t\tbasic: \'Basic\',\n
\t\tobject: \'Objects\',\n
\t\tsymbol: \'Symbols\',\n
\t\tarrow: \'Arrows\',\n
\t\tflowchart: \'Flowchart\',\n
\t\tanimal: \'Animals\',\n
\t\tgame: \'Cards & Chess\',\n
\t\tdialog_balloon: \'Dialog balloons\',\n
\t\telectronics: \'Electronics\',\n
\t\tmath: \'Mathematical\',\n
\t\tmusic: \'Music\',\n
\t\tmisc: \'Miscellaneous\',\n
\t\traphael_1: \'raphaeljs.com set 1\',\n
\t\traphael_2: \'raphaeljs.com set 2\'\n
\t};\n
\n
\tvar library = {\n
\t\tbasic: {\n
\t\t\tdata: {\n
\t\t\t\t\'heart\': \'m150,73c61,-175 300,0 0,225c-300,-225 -61,-400 0,-225z\',\n
\t\t\t\t\'frame\': \'m0,0l300,0l0,300l-300,0zm35,-265l0,230l230,0l0,-230z\',\n
\t\t\t\t\'donut\': \'m1,150l0,0c0,-82.29042 66.70958,-149 149,-149l0,0c39.51724,0 77.41599,15.69816 105.35889,43.64108c27.94293,27.94293 43.64111,65.84165 43.64111,105.35892l0,0c0,82.29041 -66.70958,149 -149,149l0,0c-82.29041,0 -149,-66.70959 -149,-149zm74.5,0l0,0c0,41.1452 33.35481,74.5 74.5,74.5c41.14522,0 74.5,-33.3548 74.5,-74.5c0,-41.1452 -33.3548,-74.5 -74.5,-74.5l0,0c-41.14519,0 -74.5,33.35481 -74.5,74.5z\',\n
\t\t\t\t\'triangle\': \'m1,280.375l149,-260.75l149,260.75z\',\n
\t\t\t\t\'right_triangle\': \'m1,299l0,-298l298,298z\',\n
\t\t\t\t\'diamond\': \'m1,150l149,-149l149,149l-149,149l-149,-149z\',\n
\t\t\t\t\'pentagon\': \'m1.00035,116.97758l148.99963,-108.4053l148.99998,108.4053l-56.91267,175.4042l-184.1741,0l-56.91284,-175.4042z\',\n
\t\t\t\t\'hexagon\': \'m1,149.99944l63.85715,-127.71428l170.28572,0l63.85713,127.71428l-63.85713,127.71428l-170.28572,0l-63.85715,-127.71428z\',\n
\t\t\t\t\'septagon1\': \'m0.99917,191.06511l29.51249,-127.7108l119.48833,-56.83673l119.48836,56.83673l29.51303,127.7108l-82.69087,102.41679l-132.62103,0l-82.69031,-102.41679z\',\n
\t\t\t\t\'heptagon\': \'m1,88.28171l87.28172,-87.28171l123.43653,0l87.28172,87.28171l0,123.43654l-87.28172,87.28172l-123.43653,0l-87.28172,-87.28172l0,-123.43654z\',\n
\t\t\t\t\'decagon\': \'m1,150.00093l28.45646,-88.40318l74.49956,-54.63682l92.08794,0l74.50002,54.63682l28.45599,88.40318l-28.45599,88.40318l-74.50002,54.63681l-92.08794,0l-74.49956,-54.63681l-28.45646,-88.40318z\',\n
\t\t\t\t\'dodecagon\': \'m1,110.07421l39.92579,-69.14842l69.14842,-39.92579l79.85159,0l69.14842,39.92579l39.92578,69.14842l0,79.85159l-39.92578,69.14842l-69.14842,39.92578l-79.85159,0l-69.14842,-39.92578l-39.92579,-69.14842l0,-79.85159z\',\n
\t\t\t\t\'star_points_5\': \'m1,116.58409l113.82668,0l35.17332,-108.13487l35.17334,108.13487l113.82666,0l-92.08755,66.83026l35.17514,108.13487l-92.08759,-66.83208l-92.08757,66.83208l35.17515,-108.13487l-92.08758,-66.83026z\',\n
\t\t\t\t\'trapezoid\': \'m1,299l55.875,-298l186.25001,0l55.87498,298z\',\n
\t\t\t\t\'arrow_up\': \'m1.49805,149.64304l148.50121,-148.00241l148.50121,148.00241l-74.25061,0l0,148.71457l-148.5012,0l0,-148.71457z\',\n
\t\t\t\t\'vertical_scrool\': \'m37.375,261.625l0,-242.9375l0,0c0,-10.32083 8.36669,-18.6875 18.6875,-18.6875l224.25,0c10.32083,0 18.6875,8.36667 18.6875,18.6875c0,10.32081 -8.36667,18.6875 -18.6875,18.6875l-18.6875,0l0,242.9375c0,10.32083 -8.36668,18.6875 -18.6875,18.6875l-224.25,0l0,0c-10.32083,0 -18.6875,-8.36667 -18.6875,-18.6875c0,-10.32083 8.36667,-18.6875 18.6875,-18.6875zm37.375,-261.625l0,0c10.32081,0 18.6875,8.36667 18.6875,18.6875c0,10.32081 -8.36669,18.6875 -18.6875,18.6875c-5.1604,0 -9.34375,-4.18335 -9.34375,-9.34375c0,-5.16041 4.18335,-9.34375 9.34375,-9.34375l18.6875,0m186.875,18.6875l-205.5625,0m-37.375,224.25l0,0c5.1604,0 9.34375,4.18335 9.34375,9.34375c0,5.1604 -4.18335,9.34375 -9.34375,9.34375l18.6875,0m-18.6875,18.6875l0,0c10.32081,0 18.6875,-8.36667 18.6875,-18.6875l0,-18.6875\',\n
\t\t\t\t\'smiley\': \'m68.49886,214.78838q81.06408,55.67332 161.93891,0m-144.36983,-109.9558c0,-8.60432 6.97517,-15.57949 15.57948,-15.57949c8.60431,0 15.57948,6.97517 15.57948,15.57949c0,8.60431 -6.97517,15.57947 -15.57948,15.57947c-8.60431,0 -15.57948,-6.97516 -15.57948,-15.57947m95.83109,0c0,-8.60432 6.97517,-15.57949 15.57948,-15.57949c8.60431,0 15.57947,6.97517 15.57947,15.57949c0,8.60431 -6.97516,15.57947 -15.57947,15.57947c-8.60429,0 -15.57948,-6.97516 -15.57948,-15.57947m-181.89903,44.73038l0,0c0,-82.60133 66.96162,-149.56296 149.56296,-149.56296c82.60135,0 149.56296,66.96162 149.56296,149.56296c0,82.60135 -66.96161,149.56296 -149.56296,149.56296c-82.60133,0 -149.56296,-66.96161 -149.56296,-149.56296zm0,0l0,0c0,-82.60133 66.96162,-149.56296 149.56296,-149.56296c82.60135,0 149.56296,66.96162 149.56296,149.56296c0,82.60135 -66.96161,149.56296 -149.56296,149.56296c-82.60133,0 -149.56296,-66.96161 -149.56296,-149.56296z\',\n
\t\t\t\t\'left_braket\': \'m174.24565,298.5c-13.39009,0 -24.24489,-1.80908 -24.24489,-4.04065l0,-140.4187c0,-2.23158 -10.85481,-4.04065 -24.2449,-4.04065l0,0c13.39009,0 24.2449,-1.80907 24.2449,-4.04065l0,-140.4187l0,0c0,-2.23159 10.8548,-4.04066 24.24489,-4.04066\',\n
\t\t\t\t\'uml_actor\': \'m40.5,100l219,0m-108.99991,94.00006l107,105m-107.00009,-106.00006l-100,106m99.5,-231l0,125m33.24219,-158.75781c0,18.35916 -14.88303,33.24219 -33.24219,33.24219c-18.35916,0 -33.2422,-14.88303 -33.2422,-33.24219c0.00002,-18.35915 14.88304,-33.24219 33.2422,-33.24219c18.35916,0 33.24219,14.88304 33.24219,33.24219z\',\n
\t\t\t\t\'dialog_balloon_1\': \'m0.99786,35.96579l0,0c0,-19.31077 15.28761,-34.96524 34.14583,-34.96524l15.52084,0l0,0l74.50001,0l139.68748,0c9.05606,0 17.74118,3.68382 24.14478,10.24108c6.40356,6.55726 10.00107,15.45081 10.00107,24.72416l0,87.41311l0,0l0,52.44785l0,0c0,19.31078 -15.2876,34.96524 -34.14584,34.96524l-139.68748,0l-97.32507,88.90848l22.82506,-88.90848l-15.52084,0c-18.85822,0 -34.14583,-15.65446 -34.14583,-34.96524l0,0l0,-52.44785l0,0z\',\n
\t\t\t\t\'cloud\': \'m182.05086,34.31005c-0.64743,0.02048 -1.27309,0.07504 -1.92319,0.13979c-10.40161,1.03605 -19.58215,7.63722 -24.24597,17.4734l-2.47269,7.44367c0.53346,-2.57959 1.35258,-5.08134 2.47269,-7.44367c-8.31731,-8.61741 -19.99149,-12.59487 -31.52664,-10.72866c-11.53516,1.8662 -21.55294,9.3505 -27.02773,20.19925c-15.45544,-9.51897 -34.72095,-8.94245 -49.62526,1.50272c-14.90431,10.44516 -22.84828,28.93916 -20.43393,47.59753l1.57977,7.58346c-0.71388,-2.48442 -1.24701,-5.01186 -1.57977,-7.58346l-0.2404,0.69894c-12.95573,1.4119 -23.58103,11.46413 -26.34088,24.91708c-2.75985,13.45294 2.9789,27.25658 14.21789,34.21291l17.54914,4.26352c-6.1277,0.50439 -12.24542,-0.9808 -17.54914,-4.26352c-8.66903,9.71078 -10.6639,24.08736 -4.94535,35.96027c5.71854,11.87289 17.93128,18.70935 30.53069,17.15887l7.65843,-2.02692c-2.46413,1.0314 -5.02329,1.70264 -7.65843,2.02692c7.15259,13.16728 19.01251,22.77237 32.93468,26.5945c13.92217,3.82214 28.70987,1.56322 41.03957,-6.25546c10.05858,15.86252 27.91113,24.19412 45.81322,21.38742c17.90208,-2.8067 32.66954,-16.26563 37.91438,-34.52742l1.82016,-10.20447c-0.27254,3.46677 -0.86394,6.87508 -1.82016,10.20447c12.31329,8.07489 27.80199,8.52994 40.52443,1.18819c12.72244,-7.34175 20.6609,-21.34155 20.77736,-36.58929l-4.56108,-22.7823l-17.96776,-15.41455c13.89359,8.70317 22.6528,21.96329 22.52884,38.19685c16.5202,0.17313 30.55292,-13.98268 36.84976,-30.22897c6.29684,-16.24631 3.91486,-34.76801 -6.2504,-48.68089c4.21637,-10.35873 3.96622,-22.14172 -0.68683,-32.29084c-4.65308,-10.14912 -13.23602,-17.69244 -23.55914,-20.65356c-2.31018,-13.45141 -11.83276,-24.27162 -24.41768,-27.81765c-12.58492,-3.54603 -25.98557,0.82654 -34.41142,11.25287l-5.11707,8.63186c1.30753,-3.12148 3.01521,-6.03101 5.11707,-8.63186c-5.93959,-8.19432 -15.2556,-12.8181 -24.96718,-12.51096z\',\n
\t\t\t\t\'cylinder\': \'m299.0007,83.77844c0,18.28676 -66.70958,33.11111 -149.00002,33.11111m149.00002,-33.11111l0,0c0,18.28676 -66.70958,33.11111 -149.00002,33.11111c-82.29041,0 -148.99997,-14.82432 -148.99997,-33.11111m0,0l0,0c0,-18.28674 66.70956,-33.1111 148.99997,-33.1111c82.29044,0 149.00002,14.82436 149.00002,33.1111l0,132.44449c0,18.28674 -66.70958,33.11105 -149.00002,33.11105c-82.29041,0 -148.99997,-14.82431 -148.99997,-33.11105z\',\n
\t\t\t\t\'arrow_u_turn\': \'m1.00059,299.00055l0,-167.62497l0,0c0,-72.00411 58.37087,-130.37499 130.375,-130.37499l0,0l0,0c34.57759,0 67.73898,13.7359 92.18906,38.18595c24.45006,24.45005 38.18593,57.61144 38.18593,92.18904l0,18.625l37.24997,0l-74.49995,74.50002l-74.50002,-74.50002l37.25,0l0,-18.625c0,-30.8589 -25.0161,-55.87498 -55.87498,-55.87498l0,0l0,0c-30.85892,0 -55.875,25.01608 -55.875,55.87498l0,167.62497z\',\n
\t\t\t\t\'arrow_left_up\': \'m0.99865,224.5l74.50004,-74.5l0,37.25l111.74991,0l0,-111.75l-37.25,0l74.5,-74.5l74.5,74.5l-37.25,0l0,186.25l-186.24989,0l0,37.25l-74.50005,-74.5z\',\n
\t\t\t\t\'maximize\': \'m1.00037,150.34581l55.30305,-55.30267l0,27.65093l22.17356,0l0,-44.21833l44.21825,0l0,-22.17357l-27.65095,0l55.30267,-55.30292l55.3035,55.30292l-27.65175,0l0,22.17357l44.21835,0l0,44.21833l22.17357,0l0,-27.65093l55.30345,55.30267l-55.30345,55.3035l0,-27.65175l-22.17357,0l0,44.21834l-44.21835,0l0,22.17355l27.65175,0l-55.3035,55.30348l-55.30267,-55.30348l27.65095,0l0,-22.17355l-44.21825,0l0,-44.21834l-22.17356,0l0,27.65175l-55.30305,-55.3035z\',\n
\t\t\t\t\'cross\': \'m0.99844,99.71339l98.71494,0l0,-98.71495l101.26279,0l0,98.71495l98.71495,0l0,101.2628l-98.71495,0l0,98.71494l-101.26279,0l0,-98.71494l-98.71494,0z\',\n
\t\t\t\t\'plaque\': \'m-0.00197,49.94376l0,0c27.5829,0 49.94327,-22.36036 49.94327,-49.94327l199.76709,0l0,0c0,27.5829 22.36037,49.94327 49.94325,49.94327l0,199.7671l0,0c-27.58289,0 -49.94325,22.36034 -49.94325,49.94325l-199.76709,0c0,-27.58292 -22.36037,-49.94325 -49.94327,-49.94325z\',\n
\t\t\t\t\'page\': \'m249.3298,298.99744l9.9335,-39.73413l39.73413,-9.93355l-49.66763,49.66768l-248.33237,0l0,-298.00001l298.00001,0l0,248.33234\'\n
\n
\t\t\t},\n
\t\t\tbuttons: []\n
\t\t}\n
\t};\n
\n
\tvar cur_lib = library.basic;\n
\tvar mode_id = \'shapelib\';\n
\tvar startClientPos = {};\n
\n
\tfunction loadIcons() {\n
\t\t$(\'#shape_buttons\').empty().append(cur_lib.buttons);\n
\t}\n
\n
\tfunction makeButtons(cat, shapes) {\n
\t\tvar size = cur_lib.size || 300;\n
\t\tvar fill = cur_lib.fill || false;\n
\t\tvar off = size * 0.05;\n
\t\tvar vb = [-off, -off, size + off*2, size + off*2].join(\' \');\n
\t\tvar stroke = fill ? 0: (size/30);\n
\t\tvar shape_icon = new DOMParser().parseFromString(\n
\t\t\t\'<svg xmlns="http://www.w3.org/2000/svg"><svg viewBox="\' + vb + \'"><path fill="\'+(fill?\'#333\':\'none\')+\'" stroke="#000" stroke-width="\' + stroke + \'" /><\\/svg><\\/svg>\',\n
\t\t\t\'text/xml\');\n
\n
\t\tvar width = 24;\n
\t\tvar height = 24;\n
\t\tshape_icon.documentElement.setAttribute(\'width\', width);\n
\t\tshape_icon.documentElement.setAttribute(\'height\', height);\n
\t\tvar svg_elem = $(document.importNode(shape_icon.documentElement,true));\n
\n
\t\tvar data = shapes.data;\n
\n
\t\tcur_lib.buttons = [];\n
\t\tvar id;\n
\t\tfor (id in data) {\n
\t\t\tvar path_d = data[id];\n
\t\t\tvar icon = svg_elem.clone();\n
\t\t\ticon.find(\'path\').attr(\'d\', path_d);\n
\n
\t\t\tvar icon_btn = icon.wrap(\'<div class="tool_button">\').parent().attr({\n
\t\t\t\tid: mode_id + \'_\' + id,\n
\t\t\t\ttitle: id\n
\t\t\t});\n
\t\t\t// Store for later use\n
\t\t\tcur_lib.buttons.push(icon_btn[0]);\n
\t\t}\n
\t}\n
\n
\tfunction loadLibrary(cat_id) {\n
\n
\t\tvar lib = library[cat_id];\n
\n
\t\tif (!lib) {\n
\t\t\t$(\'#shape_buttons\').html(\'Loading...\');\n
\t\t\t$.getJSON(svgEditor.curConfig.extPath + \'shapelib/\' + cat_id + \'.json\', function(result) {\n
\t\t\t\tcur_lib = library[cat_id] = {\n
\t\t\t\t\tdata: result.data,\n
\t\t\t\t\tsize: result.size,\n
\t\t\t\t\tfill: result.fill\n
\t\t\t\t};\n
\t\t\t\tmakeButtons(cat_id, result);\n
\t\t\t\tloadIcons();\n
\t\t\t});\n
\t\t\treturn;\n
\t\t}\n
\t\tcur_lib = lib;\n
\t\tif (!lib.buttons.length) {makeButtons(cat_id, lib);}\n
\t\tloadIcons();\n
\t}\n
\n
\treturn {\n
\t\tsvgicons: svgEditor.curConfig.extPath + \'ext-shapes.xml\',\n
\t\tbuttons: [{\n
\t\t\tid: \'tool_shapelib\',\n
\t\t\ttype: \'mode_flyout\', // _flyout\n
\t\t\tposition: 6,\n
\t\t\ttitle: \'Shape library\',\n
\t\t\tevents: {\n
\t\t\t\tclick: function() {\n
\t\t\t\t\tcanv.setMode(mode_id);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}],\n
\t\tcallback: function() {\n
\t\t\t$(\'<style>\').text(\'\\\n
\t\t\t#shape_buttons {\\\n
\t\t\t\toverflow: auto;\\\n
\t\t\t\twidth: 180px;\\\n
\t\t\t\tmax-height: 300px;\\\n
\t\t\t\tdisplay: table-cell;\\\n
\t\t\t\tvertical-align: middle;\\\n
\t\t\t}\\\n
\t\t\t\\\n
\t\t\t#shape_cats {\\\n
\t\t\t\tmin-width: 110px;\\\n
\t\t\t\tdisplay: table-cell;\\\n
\t\t\t\tvertical-align: middle;\\\n
\t\t\t\theight: 300px;\\\n
\t\t\t}\\\n
\t\t\t#shape_cats > div {\\\n
\t\t\t\tline-height: 1em;\\\n
\t\t\t\tpadding: .5em;\\\n
\t\t\t\tborder:1px solid #B0B0B0;\\\n
\t\t\t\tbackground: #E8E8E8;\\\n
\t\t\t\tmargin-bottom: -1px;\\\n
\t\t\t}\\\n
\t\t\t#shape_cats div:hover {\\\n
\t\t\t\tbackground: #FFFFCC;\\\n
\t\t\t}\\\n
\t\t\t#shape_cats div.current {\\\n
\t\t\t\tfont-weight: bold;\\\n
\t\t\t}\').appendTo(\'head\');\n
\n
\t\t\tvar btn_div = $(\'<div id="shape_buttons">\');\n
\t\t\t$(\'#tools_shapelib > *\').wrapAll(btn_div);\n
\n
\t\t\tvar shower = $(\'#tools_shapelib_show\');\n
\n
\t\t\tloadLibrary(\'basic\');\n
\n
\t\t\t// Do mouseup on parent element rather than each button\n
\t\t\t$(\'#shape_buttons\').mouseup(function(evt) {\n
\t\t\t\tvar btn = $(evt.target).closest(\'div.tool_button\');\n
\n
\t\t\t\tif (!btn.length) {return;}\n
\n
\t\t\t\tvar copy = btn.children().clone();\n
\t\t\t\tshower.children(\':not(.flyout_arrow_horiz)\').remove();\n
\t\t\t\tshower\n
\t\t\t\t\t.append(copy)\n
\t\t\t\t\t.attr(\'data-curopt\', \'#\' + btn[0].id) // This sets the current mode\n
\t\t\t\t\t.mouseup();\n
\t\t\t\tcanv.setMode(mode_id);\n
\n
\t\t\t\tcur_shape_id = btn[0].id.substr((mode_id+\'_\').length);\n
\t\t\t\tcurrent_d = cur_lib.data[cur_shape_id];\n
\n
\t\t\t\t$(\'.tools_flyout\').fadeOut();\n
\t\t\t});\n
\n
\t\t\tvar shape_cats = $(\'<div id="shape_cats">\');\n
\t\t\tvar cat_str = \'\';\n
\n
\t\t\t$.each(categories, function(id, label) {\n
\t\t\t\tcat_str += \'<div data-cat=\' + id + \'>\' + label + \'</div>\';\n
\t\t\t});\n
\n
\t\t\tshape_cats.html(cat_str).children().bind(\'mouseup\', function() {\n
\t\t\t\tvar catlink = $(this);\n
\t\t\t\tcatlink.siblings().removeClass(\'current\');\n
\t\t\t\tcatlink.addClass(\'current\');\n
\n
\t\t\t\tloadLibrary(catlink.attr(\'data-cat\'));\n
\t\t\t\t// Get stuff\n
\t\t\t\treturn false;\n
\t\t\t});\n
\n
\t\t\tshape_cats.children().eq(0).addClass(\'current\');\n
\n
\t\t\t$(\'#tools_shapelib\').append(shape_cats);\n
\n
\t\t\tshower.mouseup(function() {\n
\t\t\t\tcanv.setMode(current_d ? mode_id : \'select\');\n
\t\t\t});\n
\t\t\t$(\'#tool_shapelib\').remove();\n
\n
\t\t\tvar h = $(\'#tools_shapelib\').height();\n
\t\t\t$(\'#tools_shapelib\').css({\n
\t\t\t\t\'margin-top\': -(h/2 - 15),\n
\t\t\t\t\'margin-left\': 3\n
\t\t\t});\n
\t\t},\n
\t\tmouseDown: function(opts) {\n
\t\t\tvar mode = canv.getMode();\n
\t\t\tif (mode !== mode_id) {return;}\n
\n
\t\t\tstart_x = opts.start_x;\n
\t\t\tvar x = start_x;\n
\t\t\tstart_y = opts.start_y;\n
\t\t\tvar y = start_y;\n
\t\t\tvar cur_style = canv.getStyle();\n
         \n
\t\t\tstartClientPos.x = opts.event.clientX;\n
\t\t\tstartClientPos.y = opts.event.clientY;\n
\n
\t\t\tcur_shape = canv.addSvgElementFromJson({\n
\t\t\t\t\'element\': \'path\',\n
\t\t\t\t\'curStyles\': true,\n
\t\t\t\t\'attr\': {\n
\t\t\t\t\t\'d\': current_d,\n
\t\t\t\t\t\'id\': canv.getNextId(),\n
\t\t\t\t\t\'opacity\': cur_style.opacity / 2,\n
\t\t\t\t\t\'style\': \'pointer-events:none\'\n
\t\t\t\t}\n
\t\t\t});\n
\n
\t\t\t// Make sure shape uses absolute values\n
\t\t\tif (/[a-z]/.test(current_d)) {\n
\t\t\t\tcurrent_d = cur_lib.data[cur_shape_id] = canv.pathActions.convertPath(cur_shape);\n
\t\t\t\tcur_shape.setAttribute(\'d\', current_d);\n
\t\t\t\tcanv.pathActions.fixEnd(cur_shape);\n
\t\t\t}\n
\t\t\tcur_shape.setAttribute(\'transform\', \'translate(\' + x + \',\' + y + \') scale(0.005) translate(\' + -x + \',\' + -y + \')\');\n
\n
\t\t\tcanv.recalculateDimensions(cur_shape);\n
\n
\t\t\tvar tlist = canv.getTransformList(cur_shape);\n
\n
\t\t\tlastBBox = cur_shape.getBBox();\n
\n
\t\t\treturn {\n
\t\t\t\tstarted: true\n
\t\t\t};\n
\t\t},\n
\t\tmouseMove: function(opts) {\n
\t\t\tvar mode = canv.getMode();\n
\t\t\tif (mode !== mode_id) {return;}\n
\n
\t\t\tvar zoom = canv.getZoom();\n
\t\t\tvar evt = opts.event;\n
\n
\t\t\tvar x = opts.mouse_x/zoom;\n
\t\t\tvar y = opts.mouse_y/zoom;\n
\n
\t\t\tvar tlist = canv.getTransformList(cur_shape),\n
\t\t\t\tbox = cur_shape.getBBox(),\n
\t\t\t\tleft = box.x, top = box.y, width = box.width,\n
\t\t\t\theight = box.height;\n
\t\t\tvar dx = (x-start_x), dy = (y-start_y);\n
\n
\t\t\tvar newbox = {\n
\t\t\t\t\'x\': Math.min(start_x,x),\n
\t\t\t\t\'y\': Math.min(start_y,y),\n
\t\t\t\t\'width\': Math.abs(x-start_x),\n
\t\t\t\t\'height\': Math.abs(y-start_y)\n
\t\t\t};\n
\n
\t\t\tvar tx = 0, ty = 0,\n
\t\t\t\tsy = height ? (height+dy)/height : 1,\n
\t\t\t\tsx = width ? (width+dx)/width : 1;\n
\n
\t\t\tsx = (newbox.width / lastBBox.width) || 1;\n
\t\t\tsy = (newbox.height / lastBBox.height) || 1;\n
\n
\t\t\t// Not perfect, but mostly works...\n
\t\t\tif (x < start_x) {\n
\t\t\t\ttx = lastBBox.width;\n
\t\t\t}\n
\t\t\tif (y < start_y) {ty = lastBBox.height;}\n
\n
\t\t\t// update the transform list with translate,scale,translate\n
\t\t\tvar translateOrigin = svgroot.createSVGTransform(),\n
\t\t\t\tscale = svgroot.createSVGTransform(),\n
\t\t\t\ttranslateBack = svgroot.createSVGTransform();\n
\n
\t\t\ttranslateOrigin.setTranslate(-(left+tx), -(top+ty));\n
\t\t\tif (!evt.shiftKey) {\n
\t\t\t\tvar max = Math.min(Math.abs(sx), Math.abs(sy));\n
\n
\t\t\t\tsx = max * (sx < 0 ? -1 : 1);\n
\t\t\t\tsy = max * (sy < 0 ? -1 : 1);\n
\t\t\t}\n
\t\t\tscale.setScale(sx,sy);\n
\n
\t\t\ttranslateBack.setTranslate(left+tx, top+ty);\n
\t\t\ttlist.appendItem(translateBack);\n
\t\t\ttlist.appendItem(scale);\n
\t\t\ttlist.appendItem(translateOrigin);\n
\n
\t\t\tcanv.recalculateDimensions(cur_shape);\n
\n
\t\t\tlastBBox = cur_shape.getBBox();\n
\t\t},\n
\t\tmouseUp: function(opts) {\n
\t\t\tvar mode = canv.getMode();\n
\t\t\tif (mode !== mode_id) {return;}\n
         \n
      var keepObject = (opts.event.clientX != startClientPos.x && opts.event.clientY != startClientPos.y);\n
\n
\t\t\treturn {\n
\t\t\t\tkeep: keepObject,\n
\t\t\t\telement: cur_shape,\n
\t\t\t\tstarted: false\n
\t\t\t};\n
\t\t}\n
\t};\n
});\n
\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>16908</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
